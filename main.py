import os
from dotenv import load_dotenv
from openai import OpenAI
from gpt_service import GPTService
from response_handlers import ResponseHandlers
from user_intent import IntentClassifier
from memory_manager import MemoryManager

def main():
    """Main function to run the resume chatbot."""
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        return
    
    # Initialize services
    client = OpenAI(api_key=api_key)
    gpt_service = GPTService(client)
    response_handlers = ResponseHandlers()
    intent_classifier = IntentClassifier(client)
    
    # Initialize memory manager for conversation history and user info
    memory_manager = MemoryManager(k=15)
    
    print("Welcome to your AI Career Assistant! How can I help you today?")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye! Best of luck with your career journey.")
                break
            
            if not user_input:
                continue
            
            # Classify the user's intent
            intent_info = intent_classifier.classify_intent(user_input, memory_manager.get_user_info())
            
            # Handle the intent
            response = _handle_intent(intent_info, gpt_service, response_handlers, memory_manager)
            
            if response:
                print("\n", end="")
                from utils import print_streaming
                print_streaming(response)
                
        except KeyboardInterrupt:
            print("\n\nGoodbye! Best of luck with your career journey.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

def _handle_intent(intent_info, gpt_service, response_handlers, memory_manager):
    """Handle the classified intent and return appropriate response."""
    intent = intent_info['intent']
    args = intent_info.get('args', {})
    
    if intent == 'handle_greeting':
        response = response_handlers.handle_greeting(args['greeting'], memory_manager.get_user_info())
        memory_manager.add_message(args['greeting'], response)
        return response
        
    elif intent == 'handle_goodbye':
        response = response_handlers.handle_goodbye(args['farewell'], memory_manager.get_user_info())
        memory_manager.add_message(args['farewell'], response)
        return response
        
    elif intent == 'process_job_url':
        response = gpt_service.generate_resume_sections(args['url'], memory_manager.get_chat_history())
        memory_manager.add_message(args['url'], response)
        return response
        
    elif intent == 'process_job_description':
        response = gpt_service.process_job_description(args['job_description'], memory_manager.get_chat_history())
        memory_manager.add_message(args['job_description'], response)
        return response
        
    elif intent == 'answer_career_question':
        response = gpt_service.chat_about_resumes(args['question'], memory_manager.get_user_info(), memory_manager.get_chat_history())
        memory_manager.add_message(args['question'], response)
        return response
        
    elif intent == 'store_personal_info':
        # Store the personal information
        info_type = args['info_type']
        info_value = args['info_value']
        memory_manager.store_user_info(info_type, info_value)
        
        # Respond naturally
        user_message = f"I've noted that your {info_type} is {info_value}. How can I help with your resume or career questions?"
        response = gpt_service.chat_about_resumes(
            user_message, 
            memory_manager.get_user_info(),
            memory_manager.get_chat_history()
        )
        memory_manager.add_message(args['info_type'] + ": " + args['info_value'], response)
        return response
        
    elif intent == 'handle_off_topic':
        from utils import print_streaming
        response = "I'm specialized in helping with resumes, job applications, and career advice. How can I assist you with your career today?"
        print_streaming(response)
        memory_manager.add_message(args['off_topic_query'], response)
        return ""
        
    else:
        from utils import print_streaming
        response = "I'm not sure I understood that. Could you please rephrase your question about careers or resumes?"
        print_streaming(response)
        memory_manager.add_message("Unknown query", response)
        return ""

if __name__ == "__main__":
    main()
