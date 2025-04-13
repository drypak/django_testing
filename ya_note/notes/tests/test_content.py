from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='author',
            password='pass',
        )
        cls.other_user = User.objects.create_user(
            username='other',
            password='pass',
        )
        cls.author_note = Note.objects.create(
            title='Note by author',
            text='Text by author',
            slug='note-by-author',
            author=cls.user,
        )
        cls.other_note = Note.objects.create(
            title='Note by other',
            text='Text by other',
            slug='note-by-other',
            author=cls.other_user,
        )
        cls.urls = {
            'list': reverse('notes:list'),
            'add': reverse('notes:add'),
            'edit': reverse(
                'notes:edit', kwargs={'slug': cls.author_note.slug}),
        }

    def setUp(self):
        self.client = Client()
        self.author = self.__class__.user
        self.client.force_login(self.author)

    def test_author_sees_only_own_notes(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.urls['list'])
        notes = response.context['object_list']
        self.assertNotIn(self.author_note, notes)
        self.assertIn(self.other_note, notes)

    def test_note_passed_in_context(self):
        response = self.client.get(self.urls['add'])
        self.assertIn('form', response.context)
        self.assertNotIn('object', response.context)

    def test_edit_note_page_has_form(self):
        response = self.client.get(self.urls['edit'])
        self.assertIn('form', response.context)
