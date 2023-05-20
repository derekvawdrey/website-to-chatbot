from django.core.management.base import BaseCommand, CommandError
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

class Command(BaseCommand):
    help = 'Scrapes a website and stores the results in the database'

    def add_arguments(self, parser):
        parser.add_argument('--base-url', type=str)
    
    def handle(self, *args, **options):
        pass
    
    def sanitize(self):
        pass
