import pytest
from django.conf import settings
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_news_count_on_main_page(client, home_url, many_news):
    """На главной странице ровно NEW_COUNT_ON_HOME_PAGE новостей."""
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
