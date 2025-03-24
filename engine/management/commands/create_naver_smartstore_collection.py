from django.core.management import BaseCommand

from django.conf import settings
from coxwave.utils import util_naver_smartstore


class Command(BaseCommand):
    help = 'Create Naver Smartstore Collection'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args, **options):
        self.stdout.write('Start to create Naver Smartstore Collection')

        util_naver_smartstore.create_naver_smartstore_faq(f'{settings.PROJECT_PATH}/engine/data/final_result.pkl')

        self.stdout.write('Done')
