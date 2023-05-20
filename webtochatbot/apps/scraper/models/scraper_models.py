from django.db import models

class PageUrl(models.Model):
    url = models.CharField(max_length=200)
    def __str__(self):
        return self.url

# Create your models here.
class ScrapedPage(models.Model):
    related_url = models.ForeignKey(PageUrl, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default="", null=False, blank=False)
    content = models.TextField()
    embedding = models.TextField()

    def __str__(self):
        return self.title
    