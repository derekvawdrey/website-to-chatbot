from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Embeds the data scraped from a specific base url'

    def add_arguments(self, parser):
        parser.add_argument('--base-url', type=str)

    def handle(self, *args, **options):
        pass