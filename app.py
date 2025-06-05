from flask import Flask, request, Response, stream_with_context, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os
from gpt_service import GPTService
from response_handlers import ResponseHandlers
from user_intent import IntentClassifier
from memory_manager import MemoryManager
from pdf_processor import PDFProcessor
from flask_cors import CORS
from rate_limit import InMemoryRateLimiter
from functools import wraps

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize in-memory rate limiter (50 messages per 3 hours)
rate_limiter = InMemoryRateLimiter(
    message_limit=50,
    reset_period_hours=3
)

# Initialize services
client = OpenAI(api_key=api_key)
response_handlers = ResponseHandlers()
gpt_service = GPTService(client, response_handlers)
intent_classifier = IntentClassifier(client)
pdf_processor = PDFProcessor()

# Dictionary to store memory managers for different sessions
session_memories = {}

def rate_limit_check(f):
    """
    Decorator to check rate limits before processing requests.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Get session_id from request
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        # For file uploads, get from form data
        if not session_id and request.form:
            session_id = request.form.get('session_id')
        
        if not session_id:
            # If no session_id, proceed without rate limiting
            return f(*args, **kwargs)
        
        # Check rate limit
        limit_status = rate_limiter.check_limit(session_id)
        
        if not limit_status['allowed']:
            return jsonify({
                'error': 'Message limit reached',
                'limit': limit_status['limit'],
                'current_count': limit_status['current_count'],
                'reset_time': limit_status['reset_time'].isoformat() if limit_status['reset_time'] else None,
                'message': f"You've reached the limit of {limit_status['limit']} messages. "
                          f"Please wait until {limit_status['reset_time'].strftime('%Y-%m-%d %H:%M:%S')} "
                          "or start a new session."
            }), 429  # 429 Too Many Requests
        
        # Call the original function
        result = f(*args, **kwargs)
        
        # Increment counter after successful processing
        rate_limiter.increment_count(session_id)
        
        # Add rate limit headers to response
        if isinstance(result, Response):
            result.headers['X-RateLimit-Limit'] = str(limit_status['limit'])
            result.headers['X-RateLimit-Remaining'] = str(limit_status['remaining'] - 1)
            result.headers['X-RateLimit-Used'] = str(limit_status['current_count'] + 1)
            if limit_status['reset_time']:
                result.headers['X-RateLimit-Reset'] = str(int(limit_status['reset_time'].timestamp()))
        
        return result
    
    return wrapper

def get_memory_manager(session_id=None):
    """Get or create a memory manager for the given session ID."""
    if not session_id:
        # Create a new session if none provided
        memory_manager = MemoryManager()
        session_id = memory_manager.session_id
        session_memories[session_id] = memory_manager
        return memory_manager, session_id
    
    # Return existing memory manager or create new one
    if session_id in session_memories:
        return session_memories[session_id], session_id
    else:
        memory_manager = MemoryManager(session_id=session_id)
        session_memories[session_id] = memory_manager
        return memory_manager, session_id

def handle_intent(intent_info, memory_manager, original_input):
    """Handle the classified intent and return appropriate response."""
    intent = intent_info['intent']
    args = intent_info.get('args', {})
    
    if intent == 'handle_greeting':
        return response_handlers.handle_greeting(args['greeting'], memory_manager.get_user_info())
        
    elif intent == 'handle_goodbye':
        return response_handlers.handle_goodbye(args['farewell'], memory_manager.get_user_info())
        
    elif intent == 'process_job_url':
        return gpt_service.generate_resume_sections(
            args['url'], 
            memory_manager.get_user_info(),
            memory_manager.get_chat_history()
        )
        
    elif intent == 'process_job_description':
        return gpt_service.process_job_description(
            args['job_description'], 
            memory_manager.get_user_info(),
            memory_manager.get_chat_history()
        )
        
    elif intent == 'answer_career_question':
        return gpt_service.chat_about_resumes(
            args['question'], 
            memory_manager.get_user_info(), 
            memory_manager.get_chat_history()
        )
    
    elif intent == 'handle_confirmation':
        return response_handlers.handle_confirmation(args['confirmation'], memory_manager.get_user_info())
    
    elif intent == 'handle_rejection':
        return response_handlers.handle_rejection(args['rejection'], memory_manager.get_user_info())
        
    elif intent == 'rewrite_resume_section':
        section = args['section']
        prompt = f"Please rewrite the {section} section of my resume to make it more effective."
        return gpt_service.chat_about_resumes(
            prompt,
            memory_manager.get_user_info(),
            memory_manager.get_chat_history()
        )
        
    elif intent == 'store_personal_info':
        # Store the personal information
        info_type = args['info_type']
        info_value = args['info_value']
        memory_manager.store_user_info(info_type, info_value)
        
        # Create a more specific confirmation message based on what was stored
        if info_type == 'experience':
            return f"Got it! I've noted that you have {info_value}. This will be helpful for tailoring your resume."
        elif info_type == 'current_role':
            return f"Perfect! I've noted that you work as {info_value}. Your background will be valuable for your career goals."
        elif info_type == 'name':
            return f"Nice to meet you, {info_value}! How can I help with your career today?"
        elif info_type == 'career_interest':
            return f"Excellent! I've noted your interest in {info_value}. I'm here to help you with your job search in this field."
        else:
            return f"Thanks for sharing that information! I've noted your {info_type}: {info_value}."
        
    elif intent == 'handle_off_topic':
        return "I'm specialized in helping with resumes, job applications, and career advice. How can I assist you with your career today?"
        
    else:
        return "I'm not sure I understood that. Could you please rephrase your question about careers or resumes?"

@app.route('/api/chat-stream', methods=['POST'])
@rate_limit_check
def chat_stream():
    data = request.json
    user_input = data.get('message', '')
    session_id = data.get('session_id', None)
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get or create memory manager for this session
    memory_manager, session_id = get_memory_manager(session_id)

    @stream_with_context
    def generate():
        try:
            # Check if user has reached message limit
            limit_status = rate_limiter.get_session_stats(session_id)
            if not limit_status['allowed']:
                reset_time = limit_status['reset_time'].strftime('%Y-%m-%d %H:%M:%S')
                yield f"You've reached the limit of {limit_status['limit']} messages. Please wait until {reset_time} for your limit to reset, or start a new session."
                return
                
            intent_info = intent_classifier.classify_intent(user_input, memory_manager.get_user_info())
            full_response = ""

            # Process the intent and generate response
            response = handle_intent(intent_info, memory_manager, user_input)
            
            # Stream the response
            for chunk in response.split(' '):
                chunk += ' '
                full_response += chunk
                yield chunk

            memory_manager.add_message(user_input, full_response)

        except Exception as e:
            yield f"[Error: {str(e)}]"

    return Response(generate(), mimetype='text/plain')

@app.route('/api/rate-limit/status', methods=['GET'])
def rate_limit_status():
    """Get rate limit status for a session."""
    session_id = request.args.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'No session_id provided'}), 400
    
    stats = rate_limiter.get_session_stats(session_id)
    
    return jsonify({
        'session_id': session_id,
        'messages_used': stats['current_count'],
        'messages_limit': stats['limit'],
        'messages_remaining': stats['remaining'],
        'reset_time': stats['reset_time'].isoformat() if stats['reset_time'] else None,
        'time_until_reset': stats['time_until_reset']
    })

@app.route('/api/rate-limit/reset', methods=['POST'])
def rate_limit_reset():
    """Reset rate limit for a session (admin endpoint)."""
    # Add authentication here in production
    data = request.json
    session_id = data.get('session_id')
    admin_key = data.get('admin_key')
    
    # Simple admin key check (use proper authentication in production)
    if admin_key != os.getenv('ADMIN_KEY', 'your-secret-admin-key'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not session_id:
        return jsonify({'error': 'No session_id provided'}), 400
    
    rate_limiter.reset_session(session_id)
    
    return jsonify({
        'message': 'Rate limit reset successfully',
        'session_id': session_id
    })

@app.route('/api/session', methods=['POST'])
def manage_session():
    """API endpoint for session management."""
    data = request.json
    action = data.get('action', '')
    session_id = data.get('session_id', None)
    
    memory_manager, session_id = get_memory_manager(session_id)
    
    if action == 'new':
        # Create a new session
        memory_manager = MemoryManager()
        session_id = memory_manager.session_id
        session_memories[session_id] = memory_manager
        
        # Get initial rate limit status
        limit_status = rate_limiter.get_session_stats(session_id)
        
        return jsonify({
            'session_id': session_id,
            'message': 'New session created',
            'rate_limit': {
                'messages_remaining': limit_status['remaining'],
                'messages_limit': limit_status['limit']
            }
        })
    
    elif action == 'info':
        # Get session info
        info = memory_manager.get_session_info()
        limit_status = rate_limiter.get_session_stats(session_id)
        
        return jsonify({
            'session_id': info['session_id'],
            'start_time': info['start_time'].isoformat(),
            'user_info_count': info['user_info_count'],
            'chat_history_length': info['chat_history_length'],
            'rate_limit': {
                'messages_used': limit_status['current_count'],
                'messages_remaining': limit_status['remaining'],
                'messages_limit': limit_status['limit'],
                'reset_time': limit_status['reset_time'].isoformat() if limit_status['reset_time'] else None
            }
        })
    
    elif action == 'clear_user':
        # Clear user info
        memory_manager.clear_user_info_only()
        return jsonify({'message': 'User information cleared', 'session_id': session_id})
    
    elif action == 'clear_history':
        # Clear chat history
        memory_manager.clear_chat_history_only()
        return jsonify({'message': 'Chat history cleared', 'session_id': session_id})
    
    elif action == 'export':
        # Export session data
        data = memory_manager.export_session_data()
        limit_status = rate_limiter.get_session_stats(session_id)
        data['rate_limit'] = {
            'messages_used': limit_status['current_count'],
            'messages_limit': limit_status['limit']
        }
        return jsonify(data)
    
    else:
        return jsonify({'error': 'Invalid action'}), 400


@app.route('/api/upload/pdf', methods=['POST'])
@rate_limit_check
def upload_pdf():
    """API endpoint specifically for PDF uploads."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    session_id = request.form.get('session_id', None)
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'File must be a PDF'}), 400
    
    # Get memory manager for this session
    memory_manager, session_id = get_memory_manager(session_id)
    
    try:
        # Extract text from PDF
        extracted_text = pdf_processor.extract_text_from_pdf(file)
        
        # Detect document type
        doc_type = pdf_processor.detect_document_type(extracted_text)
        
        # Store the extracted text in memory for future reference
        memory_manager.store_user_info(f"uploaded_{doc_type}_text", extracted_text[:500] + "...")
        
        # Process based on document type
        if doc_type == 'resume':
            response = gpt_service.chat_about_resumes(
                f"I've uploaded my resume. Can you analyze it and give me feedback? Here's the content:\n\n{extracted_text}",
                memory_manager.get_user_info(),
                memory_manager.get_chat_history()
            )
        else:
            response = gpt_service.process_job_description(
                extracted_text,
                memory_manager.get_user_info(),
                memory_manager.get_chat_history()
            )
        
        # Add to memory
        memory_manager.add_message(
            f"[Uploaded {doc_type} PDF: {file.filename}]", 
            response
        )
        
        # Get rate limit status
        limit_status = rate_limiter.get_session_stats(session_id)
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'filename': file.filename,
            'document_type': doc_type,
            'extracted_text_preview': extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
            'rate_limit': {
                'messages_remaining': limit_status['remaining'] - 1,
                'messages_limit': limit_status['limit']
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'api_key_configured': bool(api_key),
        'rate_limiter': 'in-memory',
        'rate_limit_config': {
            'message_limit': 50,
            'reset_period_hours': 3
        }
    })

@app.route('/api/admin/sessions', methods=['GET'])
def admin_get_sessions():
    """Get all active sessions (admin endpoint)."""
    # Add authentication here in production
    admin_key = request.headers.get('X-Admin-Key')
    
    if admin_key != os.getenv('ADMIN_KEY', 'your-secret-admin-key'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    sessions = rate_limiter.get_all_active_sessions()
    
    return jsonify({
        'active_sessions': sessions,
        'total_sessions': len(sessions)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
