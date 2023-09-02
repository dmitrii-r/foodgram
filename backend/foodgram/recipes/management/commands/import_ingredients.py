import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Импорт ингредиентов из csv файла ingredients.csv
    Замещает все ранее созданные ингредиенты.
    Запуск команды: python manage.py import_ingredients
    """
    help = 'Import ingredients from ingredients.csv file'

    def handle(self, *args, **options) -> None:
        self.stdout.write(self.style.WARNING('Загрузка ингредиентов'))
        Ingredient.objects.all().delete()
        csv_file_path = 'data/ingredients.csv'
        ingredients = []
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                new_ingredient = Ingredient()
                new_ingredient.name = row['name']
                new_ingredient.measurement_unit = row['measurement_unit']
                ingredients.append(new_ingredient)
        Ingredient.objects.bulk_create(ingredients)

        self.stdout.write(self.style.SUCCESS('Ингредиенты загружены'))
