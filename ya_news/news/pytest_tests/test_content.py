import pytest

from django.conf import settings
from django.utils import timezone

from news.models import Comment, News
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_on_main_page(client, home_url):
    """На главной странице ровно NEW_COUNT_ON_HOME_PAGE новостей."""
    News.objects.bulk_create([
        News(
            title=f'title{i}',
            text=f'text{i}',
            date=timezone.now(),
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])

    response = client.get(home_url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_by_date(client, new_list, home_url):
    """Проверяет, что новости отсортированы по дате в порядке убывания."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


def test_comments_ordered_by_created(
    news_with_comments, client,
    news_url,
    multi_comments,
):
    """Проверяет, что комментарии отсортированы по времени создания."""
    client.get(news_url)

    comments = Comment.objects.filter(
        news=news_with_comments).order_by('created')

    created_times = list(comments.values_list('created', flat=True))

    assert created_times == sorted(created_times)


def test_comment_form_anonymous_user(anonymous_client, news_url):
    """Проверяет, что форма комментария
    НЕ доступна для анонимных пользователей.
    """
    response = anonymous_client.get(news_url)
    assert response.status_code == 200
    form = response.context.get('form', None)

    assert form is None


def test_comment_form_for_authenticated_user(authenticated_client, news_url):
    """Проверяет, что форма комментария
    доступна для аутентифицированных пользователей
    """
    response = authenticated_client.get(news_url)
    assert response.status_code == 200
    form = response.context.get('form', None)

    assert form is not None
    assert isinstance(form, CommentForm)
