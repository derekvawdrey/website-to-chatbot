from django.db import models
from django.conf import settings
import uuid

# Create your models here.
class Session(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField(auto_now_add=True)

class ChatbotMessage(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    embedding_information = models.TextField(default="")
    referenced_urls = models.TextField(default="")
    text = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

class UserMessage(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)