import csv

from django.core.management.base import BaseCommand

from core.models import Ingredient


class Command(BaseCommand):
    """Команда для загрузки ингредиентов из scv файла в базу данных"""
    help = 'load ingredients from scv-file to db'

    def add_arguments(self, parser):
        parser.add_argument('path_to_file')

    def handle(self, *args, **options):
        with open(options['path_to_file'], encoding='utf8') as csvfile:
            data = csv.reader(csvfile)
            for row in data:
                Ingredient.objects.create(name=row[0], measurement_unit=row[1])

        self.stdout.write('ingredients successfully upload')
