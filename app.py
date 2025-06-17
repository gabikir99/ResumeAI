from flask import Flask, request, Response, stream_with_context, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
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
        session_id = None
        
        # Try to get session_id from different sources without interfering with request parsing
        if request.content_type and 'application/json' in request.content_type:
            # Only try to get JSON if content type is actually JSON
            try:
                data = request.get_json() or {}
                session_id = data.get('session_id')
            except:
                pass
        elif request.form:
            # For multipart/form-data (file uploads)
            session_id = request.form.get('session_id')
        elif request.args:
            # For URL parameters
            session_id = request.args.get('session_id')
        
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

def stream_response_with_delay(text, chunk_size=5):
    """
    Stream a response with artificial delay to simulate typing.
    Splits text into words and yields them with small delays.
    """
    import time
    words = text.split()
    
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        if i > 0:  # Add space between chunks (except first)
            chunk = ' ' + chunk
        yield chunk
        time.sleep(0.1)  # Small delay between chunks

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
    
    elif intent == 'handle_confirmation':
        return response_handlers.handle_confirmation(args['confirmation'], memory_manager.get_user_info())
    
    elif intent == 'handle_rejection':
        return response_handlers.handle_rejection(args['rejection'], memory_manager.get_user_info())
        
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
    
    elif intent == 'answer_yes_no_question':
        return gpt_service.chat_about_resumes(
            f"{args['question']}\n\nPlease answer in one word: yes or no.",
            memory_manager.get_user_info(),
            memory_manager.get_chat_history()
        )

    elif intent == 'answer_with_user_instuctions':
        return gpt_service.chat_about_resumes(
            f"{args['question']}\n\nPlease answer using this style: {args['style']}.",
            memory_manager.get_user_info(),
            memory_manager.get_chat_history()
        )
        
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
        # FIXED: Instead of generic error, treat as career question
        return gpt_service.chat_about_resumes(
            original_input, 
            memory_manager.get_user_info(), 
            memory_manager.get_chat_history()
        )

@app.route('/')
def home():
    return "Flask app is running"

@app.route('/api/register', methods=['POST'])
def register_user():
    """API endpoint for user registration."""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirmPassword', '')
        
        # Import the database functions
        from database import create_account
        
        # Use your existing database service to create the account
        result = create_account(name, email, password, confirm_password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'user': {
                    'id': result['user']['id'],
                    'name': result['user']['name'],
                    'email': result['user']['email']
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Registration failed')
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    """API endpoint for user login."""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
   
        from database import login
        
        
        result = login(email, password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'user': {
                    'id': result['user']['id'],
                    'name': result['user']['name'],
                    'email': result['user']['email']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
    
# Add this to your app.py file

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """API endpoint to get user information by ID."""
    try:
        session_id = request.headers.get('Session-ID')
        
        # Import the database service
        from database.service import DatabaseService
        
        db_service = DatabaseService()
        user = db_service.get_user_by_id(user_id)
        
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/chat-stream', methods=['POST'])
@rate_limit_check
def chat_stream():
    data = request.json
    user_input = data.get('message', '')
    session_id = data.get('session_id', None)
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
    
    memory_manager, session_id = get_memory_manager(session_id)

    @stream_with_context
    def generate():
        try:
            limit_status = rate_limiter.get_session_stats(session_id)
            if not limit_status['allowed']:
                reset_time = limit_status['reset_time'].strftime('%Y-%m-%d %H:%M:%S')
                response_text = f"You've reached the limit of {limit_status['limit']} messages. Please wait until {reset_time} for your limit to reset, or start a new session."
                
                # Stream even the rate limit message
                for chunk in stream_response_with_delay(response_text):
                    yield chunk
                return
                
            intent_info = intent_classifier.classify_intent(user_input, memory_manager.get_user_info())
            full_response = ""

            # Check if we have a streaming response from GPT service
            try:
                # Try to get streaming response first
                for chunk in gpt_service.generate_streaming_response(intent_info, memory_manager, user_input):
                    full_response += chunk
                    yield chunk
            except Exception as streaming_error:
                print(f"Streaming failed, using fallback: {streaming_error}")
                # Fallback to non-streaming with artificial delay
                response = handle_intent(intent_info, memory_manager, user_input)
                full_response = response
                
                # Stream the complete response with artificial delay
                for chunk in stream_response_with_delay(response):
                    yield chunk

            memory_manager.add_message(user_input, full_response)

        except Exception as e:
            error_message = f"[Error: {str(e)}]"
            for chunk in stream_response_with_delay(error_message):
                yield chunk

    return Response(generate(), 
                    mimetype='text/plain',
                    headers={
                        'Cache-Control': 'no-cache',
                        'X-Accel-Buffering': 'no',
                        'Transfer-Encoding': 'chunked'
                    })

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
    user_message = request.form.get('message', '')  # Get the user's actual message
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'File must be a PDF'}), 400
    file.seek(0)
    
    # Get memory manager for this session
    memory_manager, session_id = get_memory_manager(session_id)
    
    try:
        # Extract text from PDF
        extracted_text = pdf_processor.extract_text_from_pdf(file)
        
        # Detect document type
        doc_type = pdf_processor.detect_document_type(extracted_text)
        
        # Store the extracted text in memory for future reference
        memory_manager.store_user_info(f"uploaded_{doc_type}_text", extracted_text[:500] + "...")
        
        # FIXED: Use the user's actual message instead of generic prompt
        if user_message:
            # User provided specific instructions
            full_prompt = f"{user_message}\n\nHere's the {doc_type} content:\n\n{extracted_text}"
        else:
            # Fallback to generic analysis if no message provided
            if doc_type == 'resume':
                full_prompt = f"I've uploaded my resume. Can you analyze it and give me feedback? Here's the content:\n\n{extracted_text}"
            else:
                full_prompt = f"I've uploaded a job description. Here's the content:\n\n{extracted_text}"
        
        # Process based on document type but use the user's actual request
        if doc_type == 'resume':
            response = gpt_service.chat_about_resumes(
                full_prompt,
                memory_manager.get_user_info(),
                memory_manager.get_chat_history()
            )
        else:
            response = gpt_service.process_job_description(
                extracted_text,
                memory_manager.get_user_info(),
                memory_manager.get_chat_history()
            )
        
        # Add to memory with the user's actual message
        memory_manager.add_message(
            f"{user_message} [Uploaded {doc_type} PDF: {file.filename}]" if user_message else f"[Uploaded {doc_type} PDF: {file.filename}]", 
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

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """API endpoint for submitting anonymous feedback."""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    feedback_text = data.get('feedback', '')
    
    if not feedback_text or len(feedback_text.strip()) == 0:
        return jsonify({'error': 'Feedback cannot be empty'}), 400
    
    # Get email configuration from environment variables
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    recipient_email = os.getenv("ADMIN_EMAIL")
    
    if not all([smtp_server, smtp_port, smtp_username, smtp_password, recipient_email]):
        return jsonify({'error': 'Email configuration incomplete'}), 500
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient_email
        msg['Subject'] = f"Anonymous Feedback - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Email body
        body = f"""
        New anonymous feedback has been received:
        
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Feedback:
        {feedback_text}
        
        This is an automated notification.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return jsonify({
            'message': 'Thank you for your feedback!',
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to send feedback: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)