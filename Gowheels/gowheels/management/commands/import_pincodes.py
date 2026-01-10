import csv
from django.core.management.base import BaseCommand
from gowheels.models import Pincode

class Command(BaseCommand):
    help = 'Import pincodes from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            pincodes = []
            
            for row in reader:
                # Skip rows with invalid coordinates
                if row['Latitude'] == 'NA' or row['Longitude'] == 'NA':
                    continue
                    
                try:
                    pincodes.append(Pincode(
                        code=row['Pincode'],
                        city=row['District'],
                        state=row['StateName'],
                        latitude=float(row['Latitude']),
                        longitude=float(row['Longitude'])
                    ))
                except (ValueError, KeyError):
                    continue
                
                if len(pincodes) >= 1000:
                    Pincode.objects.bulk_create(pincodes, ignore_conflicts=True)
                    pincodes = []
                    self.stdout.write(f'Imported batch of 1000 pincodes')
            
            if pincodes:
                Pincode.objects.bulk_create(pincodes, ignore_conflicts=True)
                
        self.stdout.write(self.style.SUCCESS('Successfully imported all pincodes'))