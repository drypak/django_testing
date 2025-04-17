import pytest

from django.conf import settings
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_on_main_page(client, new_list, home_url):
    """Проверяем, что на главной странице не более 10 новостей.
    И что новости отсортированы по дате в порядке убывания.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]

    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE
    assert dates == sorted(dates, reverse=True)


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


def test_comments_form_for_authenticated_user(
    authenticated_client,
    news_url
):
    """Форма комментария доступна для аутентифицированных пользователей."""
    response = authenticated_client.get(news_url)
    form = response.context.get('form')

    assert response.status_code == 200
    assert form is not None
    assert isinstance(form, CommentForm)


def test_comments_form_anonymous_user(
    anonymous_client,
    news_url
):
    """Форма комментария НЕ доступна для анонимных пользователей."""
    response = anonymous_client.get(news_url)
    form = response.context.get('form')

    assert response.status_code == 200
    assert form is None
