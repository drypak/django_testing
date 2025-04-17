from http import HTTPStatus
from notes.models import Note
from .base_test import (
    BaseTestCase,
    UPDATE_NOTE_DATA,
    URLS_INSTANCE,
    NOTE_DATA,
)


class TestPermissions(BaseTestCase):
    def test_user_cannot_edit_someone_elses_note(self):
        """Пользователь не может редактировать чужую заметку."""
        self.client.force_login(self.reader)

        old_title = self.note.title
        old_text = self.note.text
        old_slug = self.note.slug
        old_author = self.note.author

        initital_note_count = Note.objects.count()

        response = self.client.post(
            URLS_INSTANCE.edit_note,
            data=UPDATE_NOTE_DATA,
            follow=True
        )

        self.note = Note.objects.get(id=self.note.id)

        self.assertEqual(self.note.title, old_title)
        self.assertEqual(self.note.text, old_text)
        self.assertEqual(self.note.slug, old_slug)
        self.assertEqual(self.note.author, old_author)

        self.assertEqual(Note.objects.count(), initital_note_count)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_can_delete_own_note(self):
        """Пользователь может удалить свою заметку."""
        initital_note_count = Note.objects.count()
        note_id = self.note.id
        response = self.user_client.post(
            URLS_INSTANCE.delete_note,
            follow=True
        )

        self.assertEqual(Note.objects.count(), initital_note_count - 1)
        self.assertFalse(Note.objects.filter(id=note_id).exists())

        self.assertRedirects(response, URLS_INSTANCE.success)

    def test_user_cannot_delete_others_note(self):
        """Пользователь не может удалить чужую заметку."""
        initial_note_count = Note.objects.count()

        note_data = self.note
        self.client.logout()
        self.client.force_login(self.reader)

        response = self.client.post(URLS_INSTANCE.delete_note, follow=True)

        self.assertEqual(Note.objects.count(), initial_note_count)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_data.refresh_from_db()

        self.assertEqual(note_data.title, self.note.title)
        self.assertEqual(note_data.text, self.note.text)
        self.assertEqual(note_data.slug, self.note.slug)
        self.assertEqual(note_data.author, self.note.author)

    def test_anonymous_cannot_edit_note(self):
        """Анонимный пользователь не может редактировать заметку."""
        self.client.logout()
        initial_note_count = Note.objects.count()
        response = self.client.post(
            URLS_INSTANCE.edit_note,
            data=UPDATE_NOTE_DATA,
            follow=True
        )
        self.note.refresh_from_db
        self.assertEqual(self.note.title, NOTE_DATA['title'])
        self.assertEqual(self.note.text, NOTE_DATA['text'])
        self.assertEqual(self.note.slug, NOTE_DATA['slug'])
        self.assertEqual(self.note.author, self.user)

        self.assertEqual(Note.objects.count(), initial_note_count)

        login_url = URLS_INSTANCE.login
        self.assertRedirects(
            response, f'{login_url}?next={URLS_INSTANCE.edit_note}'
        )

    def test_anonymous_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        Note.objects.all().delete()

        initial_count_before = Note.objects.count()
        self.assertEqual(initial_count_before, 0)

        response = self.anonymous_client.post(
            URLS_INSTANCE.add_note,
            data=UPDATE_NOTE_DATA,
            follow=True
        )
        self.assertEqual(Note.objects.count(), 0)
        self.assertRedirects(
            response,
            f'{URLS_INSTANCE.login}?next={URLS_INSTANCE.add_note}'
        )
