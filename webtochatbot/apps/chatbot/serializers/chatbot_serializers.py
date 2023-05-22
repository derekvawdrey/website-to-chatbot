from django.urls import path, include
from webtochatbot.apps.chatbot.models import Session, ChatbotMessage, UserMessage
from rest_framework import routers, serializers, viewsets


class ChatbotMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChatbotMessage
        fields = ['session', 'text', 'timestamp']

class UserMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserMessage
        fields = ['session', 'text', 'timestamp']

# Serializers define the API representation.
class SessionSerializer(serializers.HyperlinkedModelSerializer):

    chatbot_messages = ChatbotMessageSerializer(many=True)
    user_messages = UserMessageSerializer(many=True)

    class Meta:
        model = Session
        fields = ['user', 'uuid', 'title', 'start_time', "chatbot_messages", "user_messages"]