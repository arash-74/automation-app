import csv
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

from dataentry.models import Book


@pytest.fixture
def csv_file(tmp_path):
    file = tmp_path / 'book.csv'
    file.write_text('title,author\n'
                    'Clean Code,Robert Martin'
                    )
    return file


def test_insert_data_required_arguments():
    with pytest.raises(CommandError) as e:
        call_command('insertdata')
    assert str(e.value) == 'Error: the following arguments are required: model_name, csv_file'


def test_insert_data_argument_model_name(csv_file):
    out = StringIO()
    call_command('insertdata', 'test_model', csv_file, stdout=out)
    assert 'model not found' in out.getvalue(), 'error message for invalid model is not "model not found"'


@pytest.mark.django_db
def test_insert_data_argument_csv_file_not_found(csv_file):
    out = StringIO()
    call_command('insertdata', 'book', 'test', stdout=out)
    assert 'file not found' in out.getvalue(), 'error message for invalid file is not "file not found"'


def test_insert_data_argument_csv_file_not_proper(csv_file):
    csv_file.write_text('title,author,test\n'
                        'Clean Code,Robert Martin,third column')
    out = StringIO()
    call_command('insertdata', 'book', csv_file, stdout=out)
    assert 'csv file is not properly formatted for model specified' in out.getvalue(), 'error message for invalid file is not "csv file is not properly formatted"'


@pytest.mark.django_db
def test_insert_data_add_into_database(csv_file):
    out = StringIO()
    call_command('insertdata', 'book', csv_file, stdout=out)
    assert '1 rows inserted' in out.getvalue(), 'message for add a row is not "1 rows inserted"'
    out = StringIO()
    call_command('insertdata', 'book', csv_file, stdout=out)
    assert '0 rows inserted' in out.getvalue(), 'message for add a existed row is not "0 rows inserted"'
    assert Book.objects.count() == 1, 'create data in model is not working properly'


def test_export_data_required_arguments():
    with pytest.raises(CommandError) as e:
        call_command('exportdata')
    assert str(e.value) == 'Error: the following arguments are required: model_name'


def test_export_data_model_not_found():
    out = StringIO()
    call_command('exportdata', 'test_model', stdout=out)
    assert 'No model found for test_model' in out.getvalue()


@pytest.mark.django_db
def test_export_data_csv_header(tmp_path, settings):
    settings.BASE_DIR = tmp_path
    call_command('exportdata', 'Book')
    with open(tmp_path / f'export_Book_{timezone.now().strftime('%Y-%m-%d')}.csv', 'r') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ['title', 'author']


@pytest.mark.django_db
def test_export_data_csv_data(tmp_path, settings):
    settings.BASE_DIR = tmp_path
    Book.objects.create(title='test_title', author='test_author')
    call_command('exportdata', 'Book')
    with open(tmp_path / f'export_Book_{timezone.now().strftime('%Y-%m-%d')}.csv', 'r') as f:
        reader = csv.DictReader(f)
        reader = list(reader)
        assert len(reader) == 1
