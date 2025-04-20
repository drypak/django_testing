import pytest
from http import HTTPStatus

from django.contrib.auth import get_user_model
from news.models import Comment


User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_name',
    ['home_url', 'news_url']
)
def test_pages_available_for_anonymous_user(
    client,
    request,
    url_name,
):
    """
    Проверяет, что страницы должны быть доступны
    Для анонимных пользователей.
    """
    url = request.getfixturevalue(url_name)

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


def test_edit_delete_pages_for_comment_author(
        author_client,
        delete_comment_url,
        edit_comment_url,
        comment
):
    """
    Проверяет, что страницы редактирования и удаления
    Доступны только автору комментария.
    """
    assert Comment.objects.filter(pk=comment.pk).exists()

    response_edit = author_client.get(edit_comment_url)
    response_delete = author_client.get(delete_comment_url)

    assert response_edit.status_code == HTTPStatus.NOT_FOUND
    assert response_delete.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_fixture_name',
    ['edit_comment_url', 'delete_comment_url']
)
def test_redirects_anonymous_user_to_login(
    client,
    request,
    login_url,
    url_fixture_name,
):
    """
    Проверяет, что анонимный пользователь
    Перенаправляется на страницу входа
    При попытке доступа к страницам редактирования и удаления комментариев.
    """
    protected_url = request.getfixturevalue(url_fixture_name)
    response = client.get(protected_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(login_url)


@pytest.mark.parametrize(
    'url_fixture_name',
    ['edit_comment_url', 'delete_comment_url']
)
def test_cannot_edit_or_delete_foreign_comment(
        request,
        reader_client,
        url_fixture_name,
):
    """
    Проверяет, что пользователь
    Не может редактировать или удалять
    Комментарии другого пользователя.
    """
    url = request.getfixturevalue(url_fixture_name)
    response = reader_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_name',
    ['login', 'logout', 'signup']
)
def test_auth_pages_accessible_for_anonymous_user(
        client,
        url_name,
        auth_urls
):
    """
    Проверяет, что страницы аутентификации (вход, выход, регистрация)
    Доступны для анонимных пользователей.
    """
    url = auth_urls[url_name]
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
