from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import pinecone, openai
from webtochatbot.apps.chatbot.models import Session, ChatbotMessage, UserMessage
from webtochatbot.apps.chatbot.utils.format_response import formatPineconeResponse, generateGPTPrompt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import uuid




@api_view(["GET"])
def userInput(request):
    user = request.user
    # Current session
    session_uuid = request.query_params.get('session_uuid', '')
    # Check length of user input
    user_input = request.query_params.get('user_input', '')
    if len(user_input) > 200:
        return Response({'error': 'user_input is too long (>200)'}, status=status.HTTP_400_BAD_REQUEST)
    elif len(user_input) < 1:
        return Response({'error': 'user_input is empty'}, status=status.HTTP_400_BAD_REQUEST)
    if len(session_uuid) < 1:
        return Response({'error': 'session_uuid is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Fetch session
    current_session = Session.objects.get_or_create(user=user)

    user_messages = UserMessage.objects.filter(session=current_session)
    chatbot_messages = ChatbotMessage.objects.filter(session=current_session)
    
    pinecone_index = settings.PINECONE_INDEX
    pinecone_api_key = settings.PINECONE_API_KEY
    pinecone_environment = settings.PINECONE_ENVIRONMENT
    pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
    openai.api_key = settings.OPENAI_API_KEY
    embed_query = openai.Embedding.create(
        input=user_input,
        engine=settings.OPENAI_EMBEDDING_MODEL
    )

    # retrieve from Pinecone
    query_embeds = embed_query['data'][0]['embedding']
    index = pinecone.Index(pinecone_index)
    # get relevant contexts (including the questions)
    response = index.query(query_embeds, top_k=5, include_metadata=True)

    # get relevant URLs
    urls = ""
    for n in response["matches"]:
        urls += n["metadata"]["url"] + "\n"

    pinecone_responses = formatPineconeResponse(response)
    gpt_messages = generateGPTPrompt(pinecone_responses, user_messages, chatbot_messages)

    response_from_gpt = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=gpt_messages,
        temperature = 0,
        max_tokens = 300
    )

    assistant_response_without_urls = response_from_gpt["choices"][0]["message"]["content"]
    UserMessage.objects.create(session=current_session, content=user_input)
    ChatbotMessage.objects.create(session=current_session, content=assistant_response_without_urls)
    return Response({'message': assistant_response_without_urls, 'urls': urls}, status=status.HTTP_200_OK)
