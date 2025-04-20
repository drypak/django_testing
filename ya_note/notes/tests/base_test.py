from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note

from .urls_groups import SLUG


User = get_user_model()

AUTHOR_USERNAME = 'test_author'
READER_USERNAME = 'test_reader'
PASSWORD = 'test_password'

NEW_SLUG = 'new_slug'

CREATE_NOTE_DATA = {
    'title': 'text comment',
    'text': 'Тестовый текст комментария',
}

NOTE_DATA = {
    'title': 'Комментарий',
    'text': 'Содержание комментария',
    'slug': SLUG
}

UPDATE_NOTE_DATA = {
    'title': 'Updated comment',
    'text': 'Обновлённый текст комментария',
}


class BaseTestCase(TestCase):
    """Базовый тест для всех тестов. Настройка пользователей и заметок."""

    @classmethod
    def setUpTestData(cls):
        cls.anonymous_client = Client()

        cls.user = User.objects.create_user(
            username=AUTHOR_USERNAME,
            password=PASSWORD,
        )
        cls.reader = User.objects.create_user(
            username=READER_USERNAME,
            password=PASSWORD,
        )
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=NOTE_DATA['title'],
            text=NOTE_DATA['text'],
            slug=NOTE_DATA['slug'],
            author=cls.user,
        )
