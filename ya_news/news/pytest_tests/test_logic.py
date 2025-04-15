import pytest
from http import HTTPStatus
from news.models import Comment
from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from django.conf import settings

pytestmark = pytest.mark.django_db


def test_news_count_on_main_page(client, new_list, home_url):
    """Проверяем, что на главной странице не более 10 новостей.
    И что новости отсортированы по дате в порядке убывания.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert object_list.count() == NEWS_COUNT_ON_HOME_PAGE
    assert dates == sorted(dates, reverse=True)


@pytest.mark.parametrize('news_with_comments', ['news'])
def test_comments_ordered_by_created(
    news_with_comments,
    authenticated_client,
    news_url
):
    """Проверяет, что комментарии отсортированы по времени создания."""
    response = authenticated_client.get(news_url)
    comments = response.context['news'].comment_set.all()

    created_times = [comment.created for comment in comments]

    assert created_times == sorted(created_times)


@pytest.mark.parametrize(
    'client_fixture, form_class',
    [
        ('anonymous_client', False),
        ('authenticated_client', True),
    ]
)
def test_comments_form(
    client_fixture,
    form_class,
    request,
    news_url
):
    """
    Проверяет, что форма комментария доступна для анонимных
    И авторизованных пользователей.
    """
    client = request.getfixturevalue(client_fixture)
    response = client.get(news_url)
    form = response.context.get('form')

    assert response.status_code == 200

    form = response.context.get('form')

    if form_class:
        assert form is not None
        assert isinstance(form, CommentForm)
    else:
        assert form is None


def test_authenticated_user_can_create_comment(
        authenticated_client,
        news_url,
        news
):
    """
    Проверяет, что аутентифицированный пользователь
    Может создать комментарии.
    """
    data = {'text': 'Comment text'}
    response = authenticated_client.post(news_url, data)

    assert Comment.objects.filter(news=news, text=data['text']).exists()
    assert response.status_code == 302


def test_anonymous_user_cannot_create_comment(
        client,
        news_url,
        news,
):
    """
    Проверяет, что анонимный пользователь
    Не может создать комментарии.
    """
    data = {'text': 'Comment text'}
    response = client.post(news_url, data)

    assert not Comment.objects.filter(news=news, text=data['text']).exists()
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
