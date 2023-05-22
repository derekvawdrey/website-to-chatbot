from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import pinecone, openai

# Create your views here.
def home(request):
    # return render(request, 'home.html')
    return HttpResponse('Chatbot')
