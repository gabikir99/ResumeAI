from utils import print_streaming

def handle_greeting(greeting, user_memory=None):
    """Handle user greetings with personalized responses."""
    greeting_responses = [
        "Hello! How can I help with your resume or job search today?",
        "Hi there! Ready to work on your career development?",
        "Greetings! What career assistance do you need today?",
        "Welcome! How can I help with your professional development?"
    ]
    
    # Personalize greeting if we know the user's name
    if user_memory and 'name' in user_memory:
        personalized_responses = [
            f"Hello {user_memory['name']}! How can I help with your resume or job search today?",
            f"Hi {user_memory['name']}! Ready to work on your career development?",
            f"Greetings {user_memory['name']}! What career assistance do you need today?",
            f"Welcome back {user_memory['name']}! How can I help with your professional development?"
        ]
        greeting_responses = personalized_responses
    
    # Select a response (could be randomized in a more sophisticated implementation)
    response = greeting_responses[0]
    print_streaming(response)
    return response

def handle_goodbye(farewell, user_memory=None):
    """Handle user farewells with personalized responses."""
    farewell_responses = [
        "Goodbye! Feel free to return when you need more help with your career.",
        "Take care! I'm here when you need resume or job search assistance.",
        "Until next time! Best of luck with your career journey.",
        "Farewell! Come back anytime for more career advice."
    ]
    
    # Personalize farewell if we know the user's name
    if user_memory and 'name' in user_memory:
        personalized_responses = [
            f"Goodbye {user_memory['name']}! Feel free to return when you need more help with your career.",
            f"Take care {user_memory['name']}! I'm here when you need resume or job search assistance.",
            f"Until next time {user_memory['name']}! Best of luck with your career journey.",
            f"Farewell {user_memory['name']}! Come back anytime for more career advice."
        ]
        farewell_responses = personalized_responses
    
    # Select a response (could be randomized in a more sophisticated implementation)
    response = farewell_responses[0]
    print_streaming(response)
    return response
