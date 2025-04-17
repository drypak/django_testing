import pytest
from http import HTTPStatus

from django.conf import settings

from news.models import Comment

COMMENT_TEXT = 'Текст комментария'

COMMENT_DATA = {'text': COMMENT_TEXT}

pytestmark = pytest.mark.django_db


def test_authenticated_user_can_create_comment(
        authenticated_client,
        news_url,
        news,
        user
):
    """
    Проверяет, что аутентифицированный пользователь
    Может создать комментарии.
    """
    comment_text = 'New comment text'
    comment_data = {'text': comment_text}

    coments_before = Comment.objects.count()
    response = authenticated_client.post(news_url, data=comment_data)

    comments_after = Comment.objects.count()

    # Проверяем редирект
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(news_url)

    # Проверяем что комментарий создан
    assert comments_after == coments_before + 1

    comment = Comment.objects.latest('created')
    assert comment.text == comment_text
    assert comment.news == news
    assert comment.author == user


def test_anonymous_user_cannot_create_comment(
        client,
        news_url,
        news,
):
    """
    Проверяет, что анонимный пользователь
    Не может создать комментарии.
    """
    response = client.post(news_url, COMMENT_DATA)

    assert not Comment.objects.filter(news=news, text=COMMENT_TEXT).exists()
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(str(settings.LOGIN_URL))


def test_comments_author_can_edit_comment(
        authenticated_client,
        comment,
        edit_comment_url
):
    """
    Проверяет, что автор комментария
    может редактировать его.
    """
    authenticated_client.force_login(comment.author)
    authenticated_client.post(
        edit_comment_url,
        {'text': 'Edited comment text'}
    )
    comment.refresh_from_db()
    assert comment.text == 'Edited comment text'


def test_other_user_cannot_edit_comment(
        authenticated_client,
        other_user, comment,
        edit_comment_url
):
    """Проверяет, что другой пользователь
    Не может редактировать комментарии.
    """
    authenticated_client.force_login(other_user)

    response = authenticated_client.post(
        edit_comment_url,
        {'text': 'Edited comment text'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()

    assert comment.text != 'Edited comment text'
