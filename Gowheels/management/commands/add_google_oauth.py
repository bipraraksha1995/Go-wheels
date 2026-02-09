"""
Django management command to add Google OAuth application to database
Run: python manage.py add_google_oauth
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from decouple import config


class Command(BaseCommand):
    help = 'Add Google OAuth application to database'

    def handle(self, *args, **options):
        # Get credentials from .env
        google_client_id = config('GOOGLE_CLIENT_ID', default='')
        google_client_secret = config('GOOGLE_CLIENT_SECRET', default='')

        if not google_client_id or not google_client_secret:
            self.stdout.write(
                self.style.ERROR(
                    'Error: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set in .env'
                )
            )
            return

        # Check if Google app already exists
        try:
            google_app = SocialApp.objects.get(provider='google')
            self.stdout.write(
                self.style.WARNING('Google OAuth app already exists')
            )
            # Update credentials
            google_app.client_id = google_client_id
            google_app.secret = google_client_secret
            google_app.save()
            self.stdout.write(
                self.style.SUCCESS('Google OAuth app credentials updated')
            )
        except SocialApp.DoesNotExist:
            # Create new Google app
            google_app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id=google_client_id,
                secret=google_client_secret,
            )
            self.stdout.write(
                self.style.SUCCESS('Google OAuth app created successfully')
            )

        # Add sites
        try:
            site = Site.objects.get_current()
            google_app.sites.add(site)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Google OAuth app linked to site: {site.domain}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error linking site: {str(e)}')
            )

        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Google OAuth setup complete!\n'
                'You can now use: <a href="/accounts/google/login/">Login with Google</a>'
            )
        )
