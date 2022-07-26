from django.core.management import BaseCommand

from ...constants import LOG
from ...sync import sync_views


class Command(BaseCommand):
    help = 'Syncs all postgres views existing using the django_orm_views framework'

    def add_arguments(self, parser):
        parser.add_argument(
            '--grant-select-permissions-to-user',
            action='store',
            dest='grant_select_to_user',
            help='Delete poll instead of closing it',
        )

    def handle(self, *_, **options):
        grant_select_to_user = options.get('grant_select_to_user')
        sync_views(
            grant_select_permissions_to_user=grant_select_to_user
        )

        # Inform everything that we sync'd views (Logging + stdout)
        msg = 'Successfully sync\'d all views using django_orm_views'
        LOG.getChild('sync_views').info(msg)
        self.stdout.write(msg)
