import csv

from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    """
    Импорт тегов из csv файла tags.csv
    Замещает все ранее созданные теги.
    Запуск команды: python manage.py import_tags
    """
    help = 'Import tags from tags.csv file'

    def handle(self, *args, **options) -> None:
        self.stdout.write(self.style.WARNING('Загрузка тегов'))
        Tag.objects.all().delete()
        csv_file_path = 'data/tags.csv'
        tags = []
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                new_tag = Tag()
                new_tag.name = row['name']
                new_tag.color = row['color']
                new_tag.slug = row['slug']
                tags.append(new_tag)
        Tag.objects.bulk_create(tags)

        self.stdout.write(self.style.SUCCESS('Теги загружены'))
