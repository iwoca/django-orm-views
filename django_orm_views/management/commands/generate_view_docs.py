from django.core.management import BaseCommand
from ...constants import LOG
from ...sync import generate_view_docs
from iwoca_data_docs.ci import commit_bulk


class Command(BaseCommand):
    help = 'Write postgres view docs to json file'

    def handle(self, *_, **options):

        commit_bulk(generate_view_docs())

        # Inform everything that we rebuilt all the json docs
        msg = 'Successfully rebuilt all postgres view docs'
        LOG.getChild('sync_views').info(msg)
        self.stdout.write(msg)
