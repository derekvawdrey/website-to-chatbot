"""
URL configuration for webtochatbot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import webtochatbot.apps.chatbot.views.chatbot_web as chatbot_web_views
import webtochatbot.apps.chatbot.views.api_views as chatbot_api_views

urlpatterns = [
    path("api/send_user_input", chatbot_api_views.userInput, name="send_user_input"),
    path("", chatbot_web_views.home, name="home")
]
