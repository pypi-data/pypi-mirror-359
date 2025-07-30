import os
import subprocess
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = "Runs the Django project with Daphne ASGI and live WebSocket support"

    def add_arguments(self, parser):
        parser.add_argument(
            '--port', default='8000', help='Port number for Daphne (default: 8000)'
        )
        parser.add_argument(
            '--host', default='127.0.0.1', help='Host to bind Daphne to (default: 127.0.0.1)'
        )

    def handle(self, *args, **options):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # auto fallback
        settings_module = os.environ['DJANGO_SETTINGS_MODULE']

        self.stdout.write(self.style.NOTICE(f"Using settings module: {settings_module}"))

        project_module = settings_module.split('.')[0]
        asgi_path = f"{project_module}.routing:application"

        self.stdout.write(self.style.SUCCESS(f"ning Daphne: {asgi_path}"))

        try:
            subprocess.run([
                "daphne",
                "-b", options["host"],
                "-p", options["port"],
                asgi_path
            ])
        except FileNotFoundError:
            raise CommandError("Daphne is not installed. Run `pip install daphne`.")
