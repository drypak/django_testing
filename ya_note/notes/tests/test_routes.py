from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author_user',
            password='pass',
        )
        cls.other_user = User.objects.create_user(
            username='other_user',
            password='pass',
        )
        cls.note = Note.objects.create(
            title='Test',
            text='Text',
            slug='test-note',
            author=cls.author,
        )
        cls.routes = {
            'home': reverse('notes:home'),
            'notes_list': reverse('notes:list'),
            'note_detail': reverse(
                'notes:detail', kwargs={'slug': cls.note.slug}
            ),
            'note_add': reverse('notes:add'),
            'note_done': reverse('notes:success'),
            'note_edit': reverse('notes:edit', kwargs={'slug': cls.note.slug}),
            'note_delete': reverse(
                'notes:delete', kwargs={'slug': cls.note.slug}
            ),
            'login': reverse('users:login'),
            'logout': reverse('users:logout'),
            'signup': reverse('users:signup'),
        }

    def test_home_avilable_for_anonymous(self):
        response = self.client.get(self.routes['home'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user_routes_avilable(self):
        self.client.force_login(self.author)
        for name in [
            'notes_list',
            'note_add',
            'note_done',
        ]:
            with self.subTest(name=name):
                response = self.client.get(self.routes[name])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_other_user_gets_404_on_protected_routes(self):
        self.client.force_login(self.other_user)
        for name in [
            'note_detail',
            'note_edit',
            'note_delete',
        ]:
            with self.subTest(name=name):
                response = self.client.get(self.routes[name])
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_redirected_to_login(self):
        protected_routes = [
            'notes_list',
            'note_add',
            'note_done',
            'note_detail',
            'note_edit',
            'note_delete',
        ]
        login_url = self.routes['login']
        for name in protected_routes:
            with self.subTest(name=name):
                response = self.client.get(self.routes[name])
                self.assertRedirects(
                    response,
                    f'{login_url}?next={self.routes[name]}'
                )

    def test_auth_routes_avilable_to_all_users(self):
        for name in [
            'signup',
            'logout',
            'login',
        ]:
            with self.subTest(name=name):
                response = self.client.get(self.routes[name])
                self.assertEqual(response.status_code, HTTPStatus.OK)
