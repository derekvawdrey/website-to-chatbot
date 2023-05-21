import pinecone, json
from django.core.management.base import BaseCommand, CommandError
from webtochatbot.apps.scraper.models import EmbeddedContent
from django.utils.translation import gettext as _
from django.conf import settings
from tqdm.auto import tqdm

class Command(BaseCommand):
    help = 'Scrapes a website and stores the results in the database'

    def add_arguments(self, parser):
        parser.add_argument('--base-url', type=str)

    def handle(self, *args, **options):
        # Check if base url is provided
        if options['base_url'] is None:
            raise CommandError('Please provide base url')
        
        print("In order to upload the embedded content, we will purge the previous pinecone index.")
        user_input = input("Can we purge the pinecone index and upsert the data? (yes/no)")
        if user_input != "yes":
            print("Aborted...")
            return

        
        pinecone_index = settings.PINECONE_INDEX
        pinecone_api_key = settings.PINECONE_API_KEY
        pinecone_environment = settings.PINECONE_ENVIRONMENT
        print("Uploading Embeddings to pinecone index " + pinecone_index)
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
        # Purge pinecone index
        index = pinecone.Index(pinecone_index)
        index.delete(deleteAll='true')
        print("Index purge complete")
        self.upload_all_embeddings(options['base_url'], index)


    def upload_all_embeddings(self, base_url, index):
        batch_size = 50
        embedded_content = EmbeddedContent.objects.filter(related_scraped_page__related_url__url = base_url)
        print("Total number of embedded content to upload: " + str(len(embedded_content)))
        for i in tqdm(range(0, len(embedded_content), batch_size)):
            json_list = []
            i_end = min(len(embedded_content), i+batch_size)
            meta_batch = embedded_content[i:i_end]
            for x in meta_batch:
                value = {"id":str(x.id), 
                "metadata":{'fname': x.related_scraped_page.title,
                'text': x.content_to_embed,
                'url': x.related_scraped_page.page_url},
                'values': json.loads(x.embedding)
                }
                json_list.append(value)
            index.upsert(vectors=json_list)