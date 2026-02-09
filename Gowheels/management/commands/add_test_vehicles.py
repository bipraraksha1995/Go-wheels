from django.core.management.base import BaseCommand
from gowheels.models import Vehicle

class Command(BaseCommand):
    help = 'Add test vehicle data'

    def handle(self, *args, **options):
        # Create test vehicles
        Vehicle.objects.get_or_create(
            brand_name='Toyota',
            model_name='Camry',
            defaults={
                'category_name': 'Car',
                'year': 2023,
                'state': 'California',
                'price': 150.00,
                'pricing_type': 'per-hour',
                'approval_status': 'approved',
                'available': True,
                'promoted': False,
                'sponsored': False
            }
        )
        
        Vehicle.objects.get_or_create(
            brand_name='Honda',
            model_name='Civic',
            defaults={
                'category_name': 'Car',
                'year': 2022,
                'state': 'Texas',
                'price': 120.00,
                'pricing_type': 'per-hour',
                'approval_status': 'approved',
                'available': True,
                'promoted': True,
                'sponsored': False
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Test vehicles created successfully'))