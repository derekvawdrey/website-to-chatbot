from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from webtochatbot.apps.scraper.models import BaseUrl, ScrapedPage, EmbeddedContent
from django.utils.translation import gettext as _
from django.conf import settings
import openai
import tiktoken

class Command(BaseCommand):
    help = 'Embeds the data scraped from a specific base url'

    def add_arguments(self, parser):
        parser.add_argument('--base-url', type=str)
        parser.add_argument('--max-tokens', type=int)

    def handle(self, *args, **options):
        print("NOTICE: embedding costs money as openAI API is involved.")
        base_url = options['base_url']
        max_tokens = options['max_tokens']

        if base_url is None:
            raise CommandError('Please provide a base url')
        if max_tokens is None:
            raise CommandError('Please provide max tokens')
        if max_tokens > 350:
             raise CommandError('max_tokens must be less than or equal to 350')

        if max_tokens < 100:
            print("It is recommended that max_tokens be above 100")
            confirm = input(_('Please confirm you wish to proceed, and you know what you are doing (yes/no)'))
            if confirm != 'yes':
                print("Aborting...")
                return 
        
        scraped_pages = ScrapedPage.objects.filter(related_url__url=options['base_url'])
        confirm = input(_(str(len(scraped_pages)) + " pages found, do you wish to proceed to embedding?: (yes/no)"))
        if confirm != 'yes':
                print("Aborting...")
                return 
        self.upload_to_openai(scraped_pages, max_tokens)

    def upload_to_openai(self, scraped_pages, max_tokens):
        openai.api_key = settings.OPENAI_API_KEY
        for page in scraped_pages:
            # Split text into chunks that can now be embedded
            split_text = (self.split_into_many(page.content_to_embed, max_tokens))
            for chunk in split_text:
                embedding = openai.Embedding.create(input=chunk, model='text-embedding-ada-002')['data'][0]['embedding']
                EmbeddedContent.objects.create(
                    related_scraped_page=page,
                    embedding = embedding,
                    is_embedded=True,
                )
                print("Embedded chunk successfully")
        
    def split_into_many(self, text, max_tokens):
        tokenizer = tiktoken.encoding_for_model("gpt-4")
        # Split the text into sentences
        sentences = text.split('. ')

        # Get the number of tokens for each sentence
        n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]
        
        chunks = []
        tokens_so_far = 0
        chunk = []

        # Loop through the sentences and tokens joined together in a tuple
        for sentence, token in zip(sentences, n_tokens):

            # If the number of tokens so far plus the number of tokens in the current sentence is greater 
            # than the max number of tokens, then add the chunk to the list of chunks and reset
            # the chunk and tokens so far
            if tokens_so_far + token > max_tokens:
                chunks.append(". ".join(chunk) + ".")
                chunk = []
                tokens_so_far = 0

            # If the number of tokens in the current sentence is greater than the max number of 
            # tokens, go to the next sentence
            if token > max_tokens:
                continue

            # Otherwise, add the sentence to the chunk and add the number of tokens to the total
            chunk.append(sentence)
            tokens_so_far += token + 1
            
        # Add the last chunk to the list of chunks
        if chunk:
            chunks.append(". ".join(chunk) + ".")

        return chunks

