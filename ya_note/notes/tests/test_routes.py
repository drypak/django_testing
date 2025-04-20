from http import HTTPStatus

from .base_test import BaseTestCase, UPDATE_NOTE_DATA

from .urls_groups import (
    URLS_INSTANCE,
    PUBLIC_URL_NAMES,
    AUTH_URL_NAMES,
    AUTHOR_ONLY_URL_NAMES,
)


class TestNoteRoutes(BaseTestCase):
    """Тестирование доступности роутов."""

    def test_public_routes_accessible_for_anonymous(self):
        """Публичные роуты доступны для анонимных пользователей."""
        for name in PUBLIC_URL_NAMES:
            with self.subTest(route=name):
                url = getattr(URLS_INSTANCE, name)
                response = self.anonymous_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_protected_routes_redirect_for_anonymous(self):
        """Проверка редиректа для анонимных пользователей."""
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
        for name in AUTH_URL_NAMES:
            with self.subTest(name=name):
                response = self.user_client.get(getattr(URLS_INSTANCE, name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_other_user_gets_404_on_protected_routes(self):
        """Проверка доступности к чужим заметкам."""
        for name in AUTHOR_ONLY_URL_NAMES:
            route = getattr(URLS_INSTANCE, name)
            with self.subTest(name=name):
                response = self.reader_client.get(route)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_redirected_to_login(self):
        """Проверка редиректа для анонимных пользователей."""
        self.client.logout()
        login_url = URLS_INSTANCE.login

        for name in AUTH_URL_NAMES:
            with self.subTest(name=name):
                url = getattr(URLS_INSTANCE, name)
                response = self.client.get(url)
                self.assertRedirects(response, f'{login_url}?next={url}')

    def test_auth_routes_available_to_all_users(self):
        """Проверка доступности для всех пользователей."""
        self.client.logout()
        for name in PUBLIC_URL_NAMES:
            with self.subTest(name=name):
                url = getattr(URLS_INSTANCE, name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_note_redirects_to_success_page(self):
        """Проверка редиректа после создания заметки."""
        response = self.user_client.post(
            URLS_INSTANCE.add_note,
            data=UPDATE_NOTE_DATA,
            follow=True
        )
        self.assertRedirects(response, URLS_INSTANCE.success)
