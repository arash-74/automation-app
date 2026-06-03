import pytest

from dataentry.models import Book

pytestmark = pytest.mark.django_db


@pytest.fixture
def create_init_book():
    info = {'title': 'test title', 'author': 'test author'}
    return Book.objects.create(**info)


def test_create_book(create_init_book):
    assert create_init_book is not None, 'object didn\'t exist'
    assert create_init_book.title == 'test title', 'title should be equal to test title'
    assert create_init_book.author == 'test author', 'author should be equal to test author'

