import csv

from django.core.management import BaseCommand
from django.apps import apps
from django.utils import timezone

from django.conf import settings


class Command(BaseCommand):
    help = 'export data from database in csv format'
    def add_arguments(self, parser):
        parser.add_argument('model_name', type=str)

    def handle(self, *args, **options):
        model_name = options['model_name'].capitalize()
        file = settings.BASE_DIR / f'export_{model_name}_{timezone.now().strftime('%Y-%m-%d')}.csv'

        model = None
        for app in apps.get_app_configs():
            try:
                model = app.get_model(model_name)
                break
            except LookupError:
                continue
        if not model:
            self.stdout.write(self.style.WARNING(f'No model found for {options['model_name']}'))
            return

        model_item = model.objects.all()

        with open(file,'w',newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([field.name for field in model._meta.fields if field.name != 'id'])

            for row in model_item:
                writer.writerow([row.title,row.author])

        self.stdout.write(self.style.SUCCESS(f'Successfully exported {file}'))