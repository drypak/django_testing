from django.utils.text import slugify

from notes.models import Note

from .base_test import BaseTestCase, UPDATE_NOTE_DATA, URLS_INSTANCE


class TestNoteLogic(BaseTestCase):
    """Тесты логики приложения."""
    def test_logged_in_user_can_create_note(self):
        """Пользователь может создать заметку."""
        initial_notes = set(Note.objects.all())
        self.user_client.post(
            URLS_INSTANCE.add_note,
            data=UPDATE_NOTE_DATA,
            follow=True
        )
        new_notes = set(Note.objects.all()) - initial_notes
        self.assertEqual(len(new_notes), 1)

        note = new_notes.pop()
        expected_slug = slugify(UPDATE_NOTE_DATA['title'])[:100]

        self.assertEqual(note.title, UPDATE_NOTE_DATA['title'])
        self.assertEqual(note.text, UPDATE_NOTE_DATA['text'])
        self.assertEqual(note.slug, expected_slug)
        self.assertEqual(note.author, self.user)
