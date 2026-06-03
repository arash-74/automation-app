from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from dataentry.models import Book


@pytest.fixture
def csv_file(tmp_path):
    file = tmp_path / 'book.csv'
    file.write_text('title,author\n'
                    'Clean Code,Robert Martin'
                    )
    return file


def test_required_arguments():
    with pytest.raises(CommandError) as e:
        call_command('insertdata')
    assert str(e.value) == 'Error: the following arguments are required: model_name, csv_file'


def test_argument_model_name(csv_file):
    out = StringIO()
    call_command('insertdata', 'test_model', csv_file, stdout=out)
    assert 'model not found' in out.getvalue(), 'error message for invalid model is not "model not found"'


@pytest.mark.django_db
def test_argument_csv_file_not_found(csv_file):
    out = StringIO()
    call_command('insertdata', 'book', 'test', stdout=out)
    assert 'file not found' in out.getvalue(), 'error message for invalid file is not "file not found"'
def test_argument_csv_file_not_proper(csv_file):
    csv_file.write_text('title,author,test\n'
                    'Clean Code,Robert Martin,third column')
    out = StringIO()
    call_command('insertdata', 'book', csv_file, stdout=out)
    assert 'csv file is not properly formatted for model specified' in out.getvalue(), 'error message for invalid file is not "csv file is not properly formatted"'


@pytest.mark.django_db
def test_add_into_database(csv_file):
    out = StringIO()
    call_command('insertdata', 'book', csv_file, stdout=out)
    assert '1 rows inserted' in out.getvalue(), 'message for add a row is not "1 rows inserted"'
    out = StringIO()
    call_command('insertdata', 'book', csv_file, stdout=out)
    assert '0 rows inserted' in out.getvalue(), 'message for add a existed row is not "0 rows inserted"'
    assert Book.objects.count() == 1, 'create data in model is not working properly'
