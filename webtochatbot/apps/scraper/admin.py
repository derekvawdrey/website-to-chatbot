from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(BaseUrl)
admin.site.register(ScrapedPage)
admin.site.register(EmbeddedContent)