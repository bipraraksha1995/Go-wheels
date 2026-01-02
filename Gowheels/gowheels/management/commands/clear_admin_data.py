from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil

class Command(BaseCommand):
    help = 'Clear all admin data and images from database and media files'

    def handle(self, *args, **options):
        try:
            from gowheels.models import AdminGroup, AdminCategory, AdminBrand, AdminModel, BrandImage, ModelImage, VehicleImage, Vehicle
            
            # Delete all admin data
            AdminModel.objects.all().delete()
            AdminBrand.objects.all().delete() 
            AdminCategory.objects.all().delete()
            AdminGroup.objects.all().delete()
            
            # Delete old brand/model images
            BrandImage.objects.all().delete()
            ModelImage.objects.all().delete()
            
            # Delete vehicle images
            VehicleImage.objects.all().delete()
            
            # Delete vehicles
            Vehicle.objects.all().delete()
            
            # Clear media directories
            media_dirs = [
                os.path.join(settings.MEDIA_ROOT, 'brands'),
                os.path.join(settings.MEDIA_ROOT, 'models'), 
                os.path.join(settings.MEDIA_ROOT, 'vehicles'),
                os.path.join(settings.MEDIA_ROOT, 'admin_groups'),
                os.path.join(settings.MEDIA_ROOT, 'admin_categories'),
                os.path.join(settings.MEDIA_ROOT, 'admin_brands'),
                os.path.join(settings.MEDIA_ROOT, 'admin_models')
            ]
            
            for media_dir in media_dirs:
                if os.path.exists(media_dir):
                    shutil.rmtree(media_dir)
                    self.stdout.write(f'Cleared directory: {media_dir}')
            
            self.stdout.write(self.style.SUCCESS('Successfully cleared all admin data and images'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))