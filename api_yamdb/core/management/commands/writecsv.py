import csv
import os
from pathlib import Path

import django
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_yamdb.api_yamdb.settings')
django.setup()


path = Path(__file__).resolve().parent.parent.parent.parent / 'static' / 'data'


class Command(BaseCommand):
    """Класс для записи данных из csv файлов в базу данных."""

    def add_arguments(self, parser):
        parser.add_argument(
            'model',
            help='Модель для которой записываются данные (appname.ModelName)',
        )
        parser.add_argument('csv_file', help='Имя csv файла')

    def handle(self, *args, **options):
        model_name = options['model']
        file_name = options['csv_file'] + '.csv'

        file_path = os.path.join(path, file_name)
        model = apps.get_model(model_name)

        try:
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)

                fields = next(reader)

                for row in reader:
                    obj = model()
                    for field_index, field in enumerate(fields):
                        if hasattr(obj, field + '_id'):
                            setattr(obj, field + '_id', row[field_index])
                        else:
                            setattr(obj, field, row[field_index])
                    obj.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Данные успешно записаны из {file_path} в {model_name}',
                ),
            )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл {file_name} не найден.'))
        except OperationalError:
            self.stdout.write(
                self.style.ERROR(
                    'Вы попытались заполнить таблицу со '
                    'связанным полем, но не заполнили внешнюю.',
                ),
            )
