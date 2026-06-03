import csv
import logging

from django.apps import apps
from django.core.exceptions import FieldError
from django.core.management import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Insert data from csv file into model'

    def add_arguments(self, parser):
        parser.add_argument('model_name', type=str, help='model name')
        parser.add_argument('csv_file', type=str, help='csv file name')

    def handle(self, *args, **options):
        # search and find model in all apps

        model = None
        for app in apps.get_app_configs():
            # first iterate to all app and with get_model and model_name check if it is return that model
            try:
                # if model is not inside that app raise LookupError
                model = app.get_model(options['model_name'].capitalize())
            except LookupError:
                continue
        # if there isn't model, mean cannot find model
        if model is None:
            self.stdout.write(self.style.ERROR('model not found'))
            return
            # open csv file and read data, if it's not exists or not scv handle error

        model_item = []  # use for bulk create
        try:
            with open(options['csv_file'], 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # if book in csv is already exist in model did not add
                    if not model.objects.filter(**row).exists():
                        model_item.append(model(**row))
                model.objects.bulk_create(model_item)
                self.stdout.write(self.style.SUCCESS(f'{len(model_item)} rows inserted'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('file not found'))
        except FieldError:
            self.stdout.write(self.style.ERROR('csv file is not properly formatted for model specified'))
