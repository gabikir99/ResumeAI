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