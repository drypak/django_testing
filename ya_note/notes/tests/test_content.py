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

    def test_pages_contain_form_context(self):
        """Страницы содержат контекст с формой."""
        pages_with_form = (
            (URLS_INSTANCE.add_note, False),
            (URLS_INSTANCE.edit_note, True),
        )
        for url, has_obj in pages_with_form:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                if has_obj:
                    self.assertIn('object', response.context)
                else:
                    self.assertNotIn('object', response.context)
