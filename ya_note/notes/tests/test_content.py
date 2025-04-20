from notes.forms import NoteForm
from notes.models import Note

from .base_test import BaseTestCase

from .urls_groups import URLS_INSTANCE


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

    def test_edit_note_page_contains_form(self):
        """Страница редактирования заметки содержит форму."""
        response = self.user_client.get(URLS_INSTANCE.edit_note)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
        self.assertEqual(response.context['form'].instance, self.note)

    def test_edit_note_page_contains_object(self):
        """Страница редактирования заметки содеержит объект."""
        response = self.user_client.get(URLS_INSTANCE.edit_note)
        self.assertIn('object', response.context)
        self.assertIsInstance(response.context['object'], Note)
