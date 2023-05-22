def formatPineconeResponse(response):
    feed_to_chat_gpt = ""
    for n in response["matches"]:
        feed_to_chat_gpt += n["metadata"]["text"]
    return feed_to_chat_gpt

def generateGPTPrompt(pinecone_responses, user_messages, chatbot_messages):
    messages = []
    already_added_urls = []
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
    messages.append({"role":"system","content": "VALID_URLS:" + ''.join(already_added_urls)})

    chatbot_count = len(chatbot_messages)
    user_count = len(user_messages)
    max_count = max(chatbot_count, user_count)

    # Limit amount of responses that GPT can be fed. 
    if(len(user_responses) > 3):
        user_responses = user_responses[-3:]
    if(len(chatbot_count) > 3):
        chatbot_count = chatbot_count[-3:]

    # Add in messages in order
    for i in range(max_count):
        if i < chatbot_count:
            messages.append({"role": "assistant", "content": chatbot_messages[i]})
        if i < user_count:
            messages.append({"role": "user", "content": user_messages[i]})

    # Append remaining assistant_responses if any
    for i in range(chatbot_count, max_count):
        messages.append({"role": "assistant", "content": chatbot_messages[i]})

    # Append remaining user_responses if any
    for i in range(user_count, max_count):
        messages.append({"role": "user", "content": user_messages[i]})

    return messages