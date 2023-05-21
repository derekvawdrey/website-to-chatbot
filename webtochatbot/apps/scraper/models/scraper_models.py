from django.db import models
from bs4 import BeautifulSoup

# Stores the base url
class BaseUrl(models.Model):
    url = models.CharField(max_length=200)
    is_scraped = models.BooleanField(default=False)
    def __str__(self):
        return self.url

# This class will be used to store the scraped data
class ScrapedPage(models.Model):
    related_url = models.ForeignKey(BaseUrl, on_delete=models.CASCADE)
    page_url = models.CharField(max_length=200, default="", null=False, blank=False)
    title = models.CharField(max_length=200, default="", null=False, blank=False)
    full_html = models.TextField(default="", null=False, blank=False)
    content_to_embed = models.TextField(default="")
    embedding = models.TextField(default="")
    is_embedded = models.BooleanField(default=False)
    date_embedded = models.DateTimeField(blank=True, null=True)
    is_scraped = models.BooleanField(default=False)
    date_scraped = models.DateTimeField(auto_now_add=True,blank=True, null=True)

    def __str__(self):
        return self.title
    
        

