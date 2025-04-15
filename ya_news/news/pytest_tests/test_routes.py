import pytest
from django.contrib.auth import get_user_model
from http import HTTPStatus

from news.forms import CommentForm

from news.forms import BAD_WORDS

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_home_and_detail_avilable_for_anonymous_user(
        client,
        home_url,
        news_url
):
    """
    Проверяет, что главная и детальная страницы
    Доступны для анонимных пользователей.
    """
    assert client.get(home_url).status_code == HTTPStatus.OK
    assert client.get(news_url).status_code == HTTPStatus.OK


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_form_rejects_bad_words(bad_word):
    """
    Проверяет, что форма комментария
    Отклоняет слова, содержащие запрещенные слова/
    """
    form_data = {'text': bad_word}
    form = CommentForm(data=form_data)
    assert not form.is_valid()
    assert 'text' in form.errors


def test_edit_delete_pages_for_comment_author(
        authenticated_client,
        delete_comment_url,
        edit_comment_url,
):
    """
    Проверяет, что страницы редактирования и удаления
    Доступны только автору комментария.
    """
    response_edit = authenticated_client.get(edit_comment_url)
    response_delete = authenticated_client.get(delete_comment_url)

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
        reader,
        client,
        url_fixture_name,
):
    """
    Проверяет, что пользователь
    Не может редактировать или удалять
    Комментарии другого пользователя.
    """
    client.force_login(reader)
    url = request.getfixturevalue(url_fixture_name)

    response = client.get(url)
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
