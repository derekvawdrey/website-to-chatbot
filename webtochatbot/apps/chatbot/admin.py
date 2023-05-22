from django.contrib import admin
from .models import Session, UserMessage, ChatbotMessage
# Register your models here.
admin.site.register(Session)
admin.site.register(UserMessage)
admin.site.register(ChatbotMessage)