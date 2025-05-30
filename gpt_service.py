from utils import print_streaming, Website

def message_for(content, system_prompt, is_website=True):
    """Create message format for GPT API."""
    if is_website:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content.user_prompt()},
        ]
    else:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ]

def generate_resume_sections(url, client, system_prompt):
    """Generate resume sections from a job posting URL."""
    website = Website(url)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=message_for(website, system_prompt, is_website=True),
        max_tokens=1500,
        temperature=0.3,
        stream=True
    )
    
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print_streaming(content)
            full_response += content
    
    return full_response

def chat_about_resumes(query, client, system_prompt, user_memory=None):
    """Chat about resume and career-related topics."""
    # Create messages with user memory context if available
    messages = message_for(query, system_prompt, is_website=False)
    
    # Add user memory context if available
    if user_memory and len(user_memory) > 0:
        memory_context = "User information: "
        memory_items = []
        for key, value in user_memory.items():
            memory_items.append(f"{key}: {value}")
        
        memory_context += ", ".join(memory_items)
        memory_context += "\n\nIf the user asks about their personal information (like 'what is my name?', 'what experience do I have?', etc.), respond with the stored information in a natural way."
        
        # Insert memory context as a system message before the user query
        messages.insert(1, {"role": "system", "content": memory_context})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1500,
        temperature=0.7,
        stream=True
    )
    
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print_streaming(content)
            full_response += content
    
    return full_response

def process_job_description(text, client, system_prompt):
    """Process a job description directly from text."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=message_for(text, system_prompt, is_website=False),
        max_tokens=1500,
        temperature=0.3,
        stream=True
    )
    
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print_streaming(content)
            full_response += content
    
    return full_response
