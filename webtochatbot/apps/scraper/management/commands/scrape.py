import datetime
from django.core.management.base import BaseCommand, CommandError
from webtochatbot.apps.scraper.models import ScrapedPage, BaseUrl
from django.utils.translation import gettext as _
import requests
import re
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import urllib
import os
# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^http[s]*://.+'
# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])


class Command(BaseCommand):
    help = 'Scrapes a website and stores the results in the database'

    def add_arguments(self, parser):
        parser.add_argument('--base-url', type=str)
        parser.add_argument('--html-elements-to-gather', type=str)
        parser.add_argument('--html-elements-to-ignore', type=str)
    
    def handle(self, *args, **options):
        # Check if base url is provided
        if options['base_url'] is None or options['html_elements_to_gather'] is None:
            raise CommandError('Please provide base url and body content identifier')

        if self.deleteAllBaseUrls(options['base_url']):
            self.startScrape(options['base_url'], options['html_elements_to_gather'], options['html_elements_to_ignore'])
            
        pass

    # Do a clean wipe of the database of base url objects before starting the scrape
    def deleteAllBaseUrls(self, base_url):
        # Check if base url object exists
        baseUrlObjects = BaseUrl.objects.filter(url=base_url)
        if len(baseUrlObjects) > 0:
            print("We will delete all references to this base url before proceeding.")
            confirm = input(_('Please confirm the deletion process by typing (yes/no)'))
            if confirm != 'yes':
                print("Aborting...")
                return False
        print("Deleting all references to this base url")
        BaseUrl.objects.filter(url=base_url).delete()
        print("Creating BaseUrl object")
        BaseUrl.objects.create(url=base_url)
        return True
    
    # Collect all the urls from the base url and start scraping them
    def startScrape(self, base_url, html_elements_to_gather, html_elements_to_ignore):
        print("Starting to scrape")
        self.scrape(base_url, html_elements_to_gather,html_elements_to_ignore)
        self.finishScrape(base_url,html_elements_to_gather)
        print("Finished scraping")
        pass

    def scrape(self, url, html_elements_to_gather, html_elements_to_ignore):
        # Parse the URL and get the domain
        local_domain = urlparse(url).netloc

        # Create a queue to store the URLs to crawl
        queue = deque([url])

        # Create a set to store the URLs that have already been seen (no duplicates)
        seen = set([url])

        # Create a directory to store the text files
        baseUrlObject = BaseUrl.objects.get(url=url)

        # While the queue is not empty, continue crawling
        while queue:
            
            # Get the next URL from the queue
            url = queue.pop()

            # Pre-check url string to check if it is a file or not.
            if(self.stringContainsExtension(url)):
                print(" - Skipping because it is a file/invalid: " + url)
                continue
            # Get the text from the URL using BeautifulSoup
            response = requests.get(url)

            # Double check if not page
            if(self.isNotPage(response)):
                print(" - Skipping because not a page: " + url)
                continue

            

            if response.status_code != 200:
                print(" - Skipping because status code not 200:" + url)
                continue
            print(" + " + url) # for debugging and to see the progress
            html_text = response.text
            soup = BeautifulSoup(html_text, "html.parser")
            text = ""

            if html_elements_to_ignore is not None:
                for s in soup.select(html_elements_to_ignore):
                    s.extract()

            # Find text to embed 
            contents = soup.select(html_elements_to_gather)
            for content in contents:
                text += content.get_text() + "\n"

            # find title
            title = url
            if(soup.find('title')):
                title = soup.find('title').text
            # If the crawler gets to a page that requires JavaScript, it will stop the crawl
            if ("You need to enable JavaScript to run this app." in text):
                print("Unable to parse page " + url + " due to JavaScript being required")
            
            # Write the data to the database
            ScrapedPage.objects.create(
                related_url=baseUrlObject,
                page_url=url, 
                title=title,
                full_html=html_text,
                content_to_embed=self.sanitize(text),
                is_scraped=True,
            )
            

            # Get the hyperlinks from the URL and add them to the queue
            for link in self.get_domain_hyperlinks(local_domain, url):
                if link not in seen:
                    queue.append(link)
                    seen.add(link)

    # Function to get the hyperlinks from a URL
    def get_hyperlinks(self, url):
        # Try to open the URL and read the HTML
        try:
            # Open the URL and read the HTML
            with urllib.request.urlopen(url) as response:
                # If the response is not HTML, return an empty list
                if not response.info().get('Content-Type').startswith("text/html"):
                    return []
                # Decode the HTML
                html = response.read().decode('utf-8')
        except Exception as e:
            print(e)
            return []

        # Create the HTML Parser and then Parse the HTML to get hyperlinks
        parser = HyperlinkParser()
        parser.feed(html)

        return parser.hyperlinks

    # Function to get the hyperlinks from a URL that are within the same domain
    def get_domain_hyperlinks(self, local_domain, url):
        clean_links = []
        for link in set(self.get_hyperlinks(url)):
            clean_link = None

            # If the link is a URL, check if it is within the same domain
            if re.search(HTTP_URL_PATTERN, link):
                # Parse the URL and check if the domain is the same
                url_obj = urlparse(link)
                if url_obj.netloc == local_domain:
                    clean_link = link

            # If the link is not a URL, check if it is a relative link
            else:
                if link.startswith("/"):
                    link = link[1:]
                elif link.startswith("#") or link.startswith("mailto:"):
                    continue
                clean_link = "https://" + local_domain + "/" + link

            if clean_link is not None:
                if clean_link.endswith("/"):
                    clean_link = clean_link[:-1]
                clean_links.append(clean_link)

        # Return the list of hyperlinks that are within the same domain
        return list(set(clean_links))

    def stringContainsExtension(self, url):
        if(not url):
            return False
        file_extensions = ['�','page=', 'email:','@gmail','.com','@yahoo','.txt', '.pdf','.edu?','edlf/newsletters','clientredirect?', 'shared/code', '.php', '.pdf', '.docx', '.xlsx', '.png', '.jpg', '.jpeg', "#", "tel:", "/files/media"]
        for char in file_extensions:
            if char in url:
                return True
        return False
    def isNotPage(self, response):
        content_type = response.headers.get('content-type')
        if 'text/html' in content_type:
            return False
        else:
            return True

    

    def finishScrape(self, base_url, html_elements_to_gather):
        BaseUrl.objects.filter(url=base_url).update(is_scraped=True)
        pass

    def sanitize(self, string):
        string = string.replace('\n', ' ')
        string = string.replace('\\n', ' ')
        string = string.replace('  ', ' ')
        string = string.replace('yu.edu','')
        string = string.replace('  ', ' ')
        string = string.replace('	','')
        string = string.replace(' 								','')
        string = re.sub(r'\s+', ' ', string)
        return string

    
