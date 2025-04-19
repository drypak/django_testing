from http import HTTPStatus

from .base_test import (
    BaseTestCase,
    URLS_INSTANCE,
    UPDATE_NOTE_DATA,
    PUBLIC_URLS,
)


class TestNoteRoutes(BaseTestCase):
    """Тестирование доступности роутов."""

    def test_public_routes_accessible_for_anonymous(self):
        """Публичные роуты доступны для анонимных пользователей."""
        for route in PUBLIC_URLS:
            with self.subTest(route=route):
                response = self.anonymous_client.get(route)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_protected_routes_redirect_for_anonymous(self):
        protected_routes = [
            URLS_INSTANCE.notes_list,
            URLS_INSTANCE.add_note,
        ]
        login_url = URLS_INSTANCE.login

        for route in protected_routes:
            with self.subTest(route=route):
                response = self.anonymous_client.get(route)
                expected_redirect = f'{login_url}?next={route}'
                self.assertRedirects(response, expected_redirect)

    def test_auth_user_routes_available(self):
        """Проверка доступности для авторизованных пользователей."""
        for name in [
            'notes_list',
            'add_note',
        ]:
            with self.subTest(name=name):
                response = self.user_client.get(getattr(URLS_INSTANCE, name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_other_user_gets_404_on_protected_routes(self):
        """Проверка доступности к чужим заметкам."""
        for name in ['note_detail', 'edit_note', 'delete_note']:
            route = getattr(URLS_INSTANCE, name)
            with self.subTest(name=name):
                response = self.reader_client.get(route)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_redirected_to_login(self):
        """Проверка редиректа для анонимных пользователей."""
        self.client.logout()
        login_url = URLS_INSTANCE.login
        protected = [
            'notes_list',
            'add_note',
            'success',
            'delete_note',
            'note_detail',
            'edit_note',
        ]
        for name in protected:
            with self.subTest(name=name):
                response = self.client.get(getattr(URLS_INSTANCE, name))
                self.assertRedirects(
                    response,
                    f'{login_url}?next={getattr(URLS_INSTANCE, name)}',
                )

    def test_auth_routes_available_to_all_users(self):
        """Проверка доступности для всех пользователей."""
        self.client.logout()
        for name in [
            'signup',
            'login',
            'logout',
        ]:
            with self.subTest(name=name):
                response = self.client.get(getattr(URLS_INSTANCE, name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_note_redirects_to_success_page(self):
        """Проверка редиректа после создания заметки."""
        response = self.user_client.post(
            URLS_INSTANCE.add_note,
            data=UPDATE_NOTE_DATA,
            follow=True
        )
        self.assertRedirects(response, URLS_INSTANCE.success)
