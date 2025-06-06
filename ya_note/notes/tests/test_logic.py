from http import HTTPStatus

from django.utils.text import slugify

from notes.models import Note

from .base_test import (
    BaseTestCase,
    UPDATE_NOTE_DATA,
    NOTE_DATA,
    CREATE_NOTE_DATA,
)

from .urls_groups import URLS_INSTANCE


class TestNoteLogiс(BaseTestCase):
    """Тесты логики приложения."""

    def test_logged_in_user_can_create_note(self):
        """Пользователь может создать заметку."""
        initial_notes = set(Note.objects.all())
        self.user_client.post(
            URLS_INSTANCE.add_note,
            data=CREATE_NOTE_DATA,
            follow=True
        )
        new_notes = set(Note.objects.all()) - initial_notes
        self.assertEqual(len(new_notes), 1)

        note = new_notes.pop()
        self.assertEqual(note.title, CREATE_NOTE_DATA['title'])
        self.assertEqual(note.text, CREATE_NOTE_DATA['text'])
        self.assertEqual(note.author, self.user)

    def test_anonymous_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        Note.objects.all().delete()
        notes_before = Note.objects.count()
        response = self.anonymous_client.post(
            URLS_INSTANCE.add_note,
            data=UPDATE_NOTE_DATA,
            follow=True
        )

        notes_after = Note.objects.count()
        self.assertEqual(notes_after, notes_before)

        self.assertRedirects(
            response,
            f'{URLS_INSTANCE.login}?next={URLS_INSTANCE.add_note}'
        )

    def test_slug_autogenerated(self):
        """Slug заметки должен быть автоматически сгенерирован."""
        form_data = {
            'title': 'Comment',
            'text': 'text-text-text',
        }
        response = self.user_client.post(
            URLS_INSTANCE.add_note,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, URLS_INSTANCE.success)
        note = Note.objects.get(title=form_data['title'])
        expected_slug = slugify(form_data['title'])
        self.assertEqual(note.slug, expected_slug)

    def test_slug_is_unique(self):
        """Slug заметки должен быть уникальным."""
        slug = 'sample-slug'

        Note.objects.create(
            title='Коммент 1',
            text='Текст',
            slug=slug,
            author=self.user,
        )
        initial_count = Note.objects.count()

        response = self.user_client.post(
            URLS_INSTANCE.add_note,
            data={
                'title': 'Второй комментарий',
                'text': 'Некоторый комментарий',
                'slug': slug,
            },
            follow=True
        )
        self.assertFormError(
            response, 'form', 'slug',
            f'{slug} - такой slug уже существует, '
            "придумайте уникальное значение!"
        )
        self.assertEqual(Note.objects.count(), initial_count)

    def test_user_cannot_edit_someone_elses_note(self):
        """Пользователь не может редактировать чужую заметку."""
        old_title = self.note.title
        old_text = self.note.text
        old_slug = self.note.slug
        old_author = self.note.author

        initial_note_count = Note.objects.count()

        response = self.reader_client.post(
            URLS_INSTANCE.edit_note,
            data=UPDATE_NOTE_DATA,
            follow=True
        )

        self.note = Note.objects.get(id=self.note.id)

        self.assertEqual(self.note.title, old_title)
        self.assertEqual(self.note.text, old_text)
        self.assertEqual(self.note.slug, old_slug)
        self.assertEqual(self.note.author, old_author)

        self.assertEqual(Note.objects.count(), initial_note_count)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_cannot_edit_note(self):
        """Анонимный пользователь не может редактировать заметку."""
        initial_note_count = Note.objects.count()

        response = self.anonymous_client.post(
            URLS_INSTANCE.edit_note,
            data=UPDATE_NOTE_DATA,
            follow=True
        )
        updated_note = Note.objects.get(id=self.note.pk)
        self.assertEqual(updated_note.title, NOTE_DATA['title'])
        self.assertEqual(updated_note.text, NOTE_DATA['text'])
        self.assertEqual(updated_note.slug, NOTE_DATA['slug'])
        self.assertEqual(updated_note.author, self.user)

        self.assertEqual(Note.objects.count(), initial_note_count)

        login_url = URLS_INSTANCE.login
        self.assertRedirects(
            response, f'{login_url}?next={URLS_INSTANCE.edit_note}'
        )

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

        response = self.reader_client.post(
            URLS_INSTANCE.delete_note,
            follow=True
        )

        self.assertEqual(Note.objects.count(), initial_note_count)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        updated_note = Note.objects.get(id=self.note.pk)
        self.assertEqual(updated_note.title, self.note.title)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.slug, self.note.slug)
        self.assertEqual(updated_note.author, self.note.author)
