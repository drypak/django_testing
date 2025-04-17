from notes.models import Note

from .base_test import BaseTestCase, URLS_INSTANCE


class TestNoteContent(BaseTestCase):
    """Тесты контента заметок."""
    def test_author_sees_only_own_notes(self):
        """Пользователь видит только свои заметки."""
        Note.objects.create(
            title='Reader note',
            text='Reader note text',
            slug='reader-note',
            author=self.reader,
        )
        response = self.reader_client.get(URLS_INSTANCE.notes_list)
        notes = response.context['object_list']
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].author, self.reader)
