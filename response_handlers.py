import random

class ResponseHandlers:
    """Handle specific types of responses like greetings and farewells."""
    
    def __init__(self):
        """Initialize response handlers."""
        self.greeting_responses = [
            "Hello! How can I help with your resume or job search today?",
            "Hi there! Ready to work on your career development?",
            "Greetings! What career assistance do you need today?",
            "Welcome! How can I help with your professional development?"
        ]
        
        self.farewell_responses = [
            "Goodbye! Feel free to return when you need more help with your career.",
            "Take care! I'm here when you need resume or job search assistance.",
            "Until next time! Best of luck with your career journey.",
            "Farewell! Come back anytime for more career advice."
        ]
    
    def handle_greeting(self, greeting, user_info=None):
        """Handle user greetings with personalized responses."""
        # Check if we have the user's name
        if user_info and 'name' in user_info and user_info['name']:
            name = user_info['name']
            responses = [
                f"Hello {name}! How can I help with your resume or job search today?",
                f"Hi {name}! Ready to work on your career development?",
                f"Greetings {name}! What career assistance do you need today?",
                f"Welcome back {name}! How can I help with your professional development?"
            ]
        else:
            # Use generic responses if no name is stored
            responses = self.greeting_responses.copy()
        
        response = random.choice(responses)
        return response
    
    def handle_goodbye(self, farewell, user_info=None):
        """Handle user farewells with personalized responses."""
        # Check if we have the user's name
        if user_info and 'name' in user_info and user_info['name']:
            name = user_info['name']
            responses = [
                f"Goodbye {name}! Feel free to return when you need more help with your career.",
                f"Take care {name}! I'm here when you need resume or job search assistance.",
                f"Until next time {name}! Best of luck with your career journey.",
                f"Farewell {name}! Come back anytime for more career advice."
            ]
        else:
            # Use generic responses if no name is stored
            responses = self.farewell_responses.copy()
        
        response = random.choice(responses)
        return response
    
    def handle_confirmation(self, confirmation, user_info=None):
        confirmation_lower = confirmation.lower()
    
        if any(word in confirmation_lower for word in ['next', 'move on', 'continue', 'proceed']):
            responses = [
                "Absolutely! 👍 What's the next job you'd like help with?",
                "Perfect! ✅ Ready to tackle the next application!",
                "Great! 🎉 What position should we work on next?",
                "Sounds good! ⭐ Tell me about the next opportunity!"
            ]
        else:
            responses = [
                "Great! 👍 Let me know if you need anything else!",
                "Perfect! ✅ I'm here if you need more help!",
                "Awesome! 🎉 Feel free to ask if you have other questions!",
                "Excellent! ⭐ Happy to help with anything else!"
            ]
        return random.choice(responses)

    def handle_rejection(self, rejection, user_info=None):
        rejection_lower = rejection.lower()
        
        # Check if it's rejecting a specific suggestion/offer
        if any(word in rejection_lower for word in ['not interested', 'no thanks', 'no thank you']):
            responses = [
                "No problem at all! 😊 Let me know what you'd prefer to work on!",
                "That's totally fine! 👌 What would be more helpful for you?",
                "No worries! 🙂 What other career assistance can I provide?",
                "Understood! 💙 How else can I help with your job search?"
            ]
        else:
            # For simple "no" responses
            responses = [
                "No problem at all! 😊 Let me know if you need help later!",
                "That's totally fine! 👌 I'm here whenever you're ready!",
                "No worries! 🙂 Feel free to reach out anytime!",
                "Understood! 💙 I'm here if you change your mind!"
            ]
        
        return random.choice(responses)