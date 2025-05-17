from django.core.management.base import BaseCommand
from analysis.utils import load_sample_data

class Command(BaseCommand):
    help = 'Load initial real estate data from Excel'
    
    def handle(self, *args, **options):
        success, message = load_sample_data()
        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.ERROR(message))