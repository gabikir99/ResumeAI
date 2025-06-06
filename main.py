import os
from dotenv import load_dotenv
from openai import OpenAI
from gpt_service import GPTService
from response_handlers import ResponseHandlers
from user_intent import IntentClassifier
from memory_manager import MemoryManager
from utils import print_streaming
from rate_limit import InMemoryRateLimiter

def main():
    """Main function to run the resume chatbot with in-memory rate limiting."""
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        return
    
    # Initialize in-memory rate limiter (50 messages per 24 hours)
    rate_limiter = InMemoryRateLimiter(message_limit=5, reset_period_hours=1)
    
    # Initialize services
    client = OpenAI(api_key=api_key)
    gpt_service = GPTService(client)
    response_handlers = ResponseHandlers()
    intent_classifier = IntentClassifier(client)
    
    # Initialize memory manager with session management
    memory_manager = MemoryManager(k=30)
    session_id = memory_manager.session_id
    
    print("Welcome to your AI Career Assistant! How can I help you today?")
    print(f"Session ID: {session_id[:8]}...")
    
    # Show initial rate limit status
    limit_status = rate_limiter.get_session_stats(session_id)
    print(f"📊 Rate Limit: {limit_status['remaining']}/{limit_status['limit']} messages remaining")
    
    print("\nAvailable commands:")
    print("  /new-session    - Start completely fresh session")
    print("  /session-info   - Show current session details")
    print("  /rate-limit     - Check rate limit status")
    print("  /clear-user     - Clear user info only")
    print("  /clear-history  - Clear chat history only")
    print("  /memory         - Show current memory state")
    print("  /help           - Show commands again")
    print("  exit/quit       - Exit the program")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye! Best of luck with your career journey.")
                break
            
            # Rate limit command
            if user_input.lower() == '/rate-limit':
                stats = rate_limiter.get_session_stats(session_id)
                print(f"📊 Rate Limit Status:")
                print(f"   Messages used: {stats['current_count']}/{stats['limit']}")
                print(f"   Messages remaining: {stats['remaining']}")
                if stats['reset_time']:
                    print(f"   Resets at: {stats['reset_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Time until reset: {stats['time_until_reset']}")
                continue
            
            # Enhanced commands for session management
            if user_input.lower() == '/new-session':
                old_session = memory_manager.session_id[:8]
                memory_manager.start_new_session()
                session_id = memory_manager.session_id
                print(f"🆕 Started completely new session!")
                print(f"   Previous: {old_session}... → Current: {session_id[:8]}...")
                
                # Show rate limit for new session
                limit_status = rate_limiter.get_session_stats(session_id)
                print(f"📊 Rate Limit: {limit_status['remaining']}/{limit_status['limit']} messages remaining")
                continue
                
            if user_input.lower() == '/session-info':
                info = memory_manager.get_session_info()
                print(f"📊 Current Session Info:")
                print(f"   Session ID: {info['session_id'][:8]}...")
                print(f"   Started: {info['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   User Info Items: {info['user_info_count']}")
                print(f"   Chat History Words: {info['chat_history_length']}")
                
                # Add rate limit info
                stats = rate_limiter.get_session_stats(session_id)
                print(f"   Messages used: {stats['current_count']}/{stats['limit']}")
                print(f"   Messages remaining: {stats['remaining']}")
                continue
                
            if user_input.lower() == '/clear-user':
                memory_manager.clear_user_info_only()
                continue
                
            if user_input.lower() == '/clear-history':
                memory_manager.clear_chat_history_only()
                continue
            
            if user_input.lower() == '/memory':
                user_info = memory_manager.get_user_info()
                chat_history = memory_manager.get_chat_history()
                print(f"📋 Current Memory State:")
                print(f"   Session: {memory_manager.session_id[:8]}...")
                print(f"   User Info: {user_info if user_info else 'None stored'}")
                print(f"   Chat History: {len(chat_history.split()) if chat_history else 0} words")
                if chat_history:
                    print(f"   Last Exchange: ...{chat_history[-100:]}" if len(chat_history) > 100 else f"   History: {chat_history}")
                continue
            
            if user_input.lower() == '/help':
                print("\n🤖 Available Commands:")
                print("  /new-session    - Start completely fresh session (clears everything)")
                print("  /session-info   - Show current session details")
                print("  /rate-limit     - Check rate limit status")
                print("  /clear-user     - Clear user info only (keep chat history)")
                print("  /clear-history  - Clear chat history only (keep user info)")
                print("  /memory         - Show what's currently stored")
                print("  /help           - Show this help message")
                print("  exit/quit       - Exit the program")
                print("\n💡 Use /new-session to start fresh with a new 50-message limit!")
                continue
            
            if not user_input:
                continue
            
            # Check rate limit before processing
            limit_check = rate_limiter.check_limit(session_id)
            if not limit_check['allowed']:
                print(f"\n❌ Rate limit exceeded!")
                print(f"   You've used all {limit_check['limit']} messages for this session.")
                if limit_check['reset_time']:
                    print(f"   Limit resets at: {limit_check['reset_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Time until reset: {limit_check['time_until_reset']}")
                print("   Use /new-session to start a fresh session with a new limit.")
                continue
            
            # Classify the user's intent
            intent_info = intent_classifier.classify_intent(user_input, memory_manager.get_user_info())
            
            # Handle the intent
            response = _handle_intent(intent_info, gpt_service, response_handlers, memory_manager, user_input)
            
            # Add conversation to memory
            if response:
                memory_manager.add_message(user_input, response)
                
                # Increment rate limit counter
                rate_limiter.increment_count(session_id)
                
                # Show remaining messages
                stats = rate_limiter.get_session_stats(session_id)
                if stats['remaining'] <= 5:
                    print(f"\n⚠️  Warning: Only {stats['remaining']} messages remaining in this session.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye! Best of luck with your career journey.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

def _handle_intent(intent_info, gpt_service, response_handlers, memory_manager, original_input):
    """Handle the classified intent and return appropriate response."""
    intent = intent_info['intent']
    args = intent_info.get('args', {})
    
    if intent == 'handle_greeting':
        response = response_handlers.handle_greeting(args['greeting'], memory_manager.get_user_info())
        print("\n", end="")
        print_streaming(response)
        return response
        
    elif intent == 'handle_goodbye':
        response = response_handlers.handle_goodbye(args['farewell'], memory_manager.get_user_info())
        print("\n", end="")
        print_streaming(response)
        return response
    
    elif intent == 'handle_confirmation':
        response = "Great! Making those changes now."
        print("\n", end="")
        print_streaming(response)
        return response

    elif intent == 'handle_rejection':
        response = "No worries! Let me know if you'd like help later."
        print("\n", end="")
        print_streaming(response)
        return response
        
    elif intent == 'process_job_url':
        print("\n", end="")
        response = gpt_service.generate_resume_sections(
            args['url'], 
            memory_manager.get_user_info(),
            memory_manager.get_chat_history()
        )
        return response
        
    elif intent == 'process_job_description':
        print("\n", end="")
        response = gpt_service.process_job_description(
            args['job_description'], 
            memory_manager.get_user_info(),
            memory_manager.get_chat_history()
        )
        return response
        
    elif intent == 'answer_career_question':
        print("\n", end="")
        response = gpt_service.chat_about_resumes(
            args['question'], 
            memory_manager.get_user_info(), 
            memory_manager.get_chat_history()
        )
        return response
        
    elif intent == 'store_personal_info':
        # Store the personal information
        info_type = args['info_type']
        info_value = args['info_value']
        memory_manager.store_user_info(info_type, info_value)
        
        # Create a more specific confirmation message based on what was stored
        if info_type == 'experience':
            confirmation_message = f"Got it! I've noted that you have {info_value}. This will be helpful for tailoring your resume."
        elif info_type == 'current_role':
            confirmation_message = f"Perfect! I've noted that you work as {info_value}. Your background will be valuable for your career goals."
        elif info_type == 'name':
            confirmation_message = f"Nice to meet you, {info_value}! How can I help with your career today?"
        elif info_type == 'career_interest':
            confirmation_message = f"Excellent! I've noted your interest in {info_value}. I'm here to help you with your job search in this field."
        else:
            confirmation_message = f"Thanks for sharing that information! I've noted your {info_type}: {info_value}."
        
        print("\n", end="")
        print_streaming(confirmation_message)
        return confirmation_message
        
    elif intent == 'handle_off_topic':
        response = "I'm specialized in helping with resumes, job applications, and career advice. How can I assist you with your career today?"
        print("\n", end="")
        print_streaming(response)
        return response
        
    else:
        response = "I'm not sure I understood that. Could you please rephrase your question about careers or resumes?"
        print("\n", end="")
        print_streaming(response)
        return response

if __name__ == "__main__":
    main()