import os
from dotenv import load_dotenv
from openai import OpenAI
from gpt_service import GPTService
from response_handlers import ResponseHandlers
from user_intent import IntentClassifier

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
    
    # Initialize user memory for personalization
    user_memory = {}
    
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
            intent_info = intent_classifier.classify_intent(user_input, user_memory)
            
            # Handle the intent
            response = _handle_intent(intent_info, gpt_service, response_handlers, user_memory)
            
            if response:
                print(f"\n{response}")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye! Best of luck with your career journey.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

def _handle_intent(intent_info, gpt_service, response_handlers, user_memory):
    """Handle the classified intent and return appropriate response."""
    intent = intent_info['intent']
    args = intent_info.get('args', {})
    
    if intent == 'handle_greeting':
        return response_handlers.handle_greeting(args['greeting'], user_memory)
        
    elif intent == 'handle_goodbye':
        return response_handlers.handle_goodbye(args['farewell'], user_memory)
        
    elif intent == 'process_job_url':
        return gpt_service.generate_resume_sections(args['url'])
        
    elif intent == 'process_job_description':
        return gpt_service.process_job_description(args['job_description'])
        
    elif intent == 'answer_career_question':
        return gpt_service.chat_about_resumes(args['question'], user_memory)
        
    elif intent == 'store_personal_info':
        # Store the personal information
        info_type = args['info_type']
        info_value = args['info_value']
        user_memory[info_type] = info_value
        
        # Respond naturally
        return gpt_service.chat_about_resumes(
            f"I've noted that your {info_type} is {info_value}. How can I help with your resume or career questions?", 
            user_memory
        )
        
    elif intent == 'handle_off_topic':
        return "I'm specialized in helping with resumes, job applications, and career advice. How can I assist you with your career today?"
        
    else:
        return "I'm not sure I understood that. Could you please rephrase your question about careers or resumes?"

if __name__ == "__main__":
    main()
