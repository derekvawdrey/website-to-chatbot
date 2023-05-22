def formatPineconeResponse(response):
    feed_to_chat_gpt = ""
    for n in response["matches"]:
        feed_to_chat_gpt += n["metadata"]["text"]
    return feed_to_chat_gpt

def generateGPTPrompt(pinecone_responses, user_messages, chatbot_messages,user_input):
    messages = []
    already_added_urls = []

    chatbot_count = len(chatbot_messages)
    user_count = len(user_messages)
    max_count = max(chatbot_count, user_count)

    # Add previous embedding information
    if(len(chatbot_messages) > 0):
        pinecone_responses += chatbot_messages[chatbot_count-1].embedding_information
    
    # Feed the URLS to 
    messages.append({"role":"system","content": "Never change character, you are a professional, helpful chatbot that provides in detail answers."})
    messages.append({"role":"system", "content": 
    """You're a chatbot representing the McKay School of Education at BYU. 
    You'll answer questions related to the McKay School of Education and BYU. 
    If you provide page links/urls only provide from the VALID_URLS section
    refrain from providing directions to any page, tell them you can't provide the information.
    If the user asks unrelated questions, redirect the conversation back to the McKay School of Education.
    Don't request a user for their Student ID.
    Assume that the conversation is always about the McKay School of Education.""" + pinecone_responses})
    

    # Remove everything but the most recent three elements from user_messages
    while len(user_messages) > 3:
        user_messages.pop(0)  # Remove the first element

    # Remove everything but the most recent three elements from chatbot_messages
    while len(chatbot_messages) > 3:
        chatbot_messages.pop(0)  # Remove the first element

    # Add previously referenced URLs
    already_added_urls = ""
    for n in chatbot_messages:
        already_added_urls += n.referenced_urls
    messages.append({"role":"system","content": f"VALID_URLS:{already_added_urls}"})
    

    # Add in messages in order
    for i in range(max_count):
        if i < chatbot_count:
            messages.append({"role": "assistant", "content": chatbot_messages[i].text})
            
        if i < user_count:
            messages.append({"role": "user", "content": user_messages[i].text})

    # Append remaining assistant_responses if any
    for i in range(chatbot_count, max_count):
        messages.append({"role": "assistant", "content": chatbot_messages[i].text})

    # Append remaining user_responses if any
    for i in range(user_count, max_count):
        messages.append({"role": "user", "content": user_messages[i].text})
    
    messages.append({"role": "user", "content": f"Answer this question:{user_input}"})

    return messages