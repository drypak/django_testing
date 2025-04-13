import pytest
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def new_list():
    new_objects = []
    for i in range(10):
        news = News.objects.create(
            title=f'Title {i}',
            text=f'Text {i}',
            date=timezone.now(),
        )
        new_objects.append(news)

    return new_objects


@pytest.mark.django_db
def test_news_count_on_main_page(client, new_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) <= 10
    assert len(object_list) == len(new_list)


@pytest.mark.django_db
def test_news_sorted_by_date(client, new_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_ordered_by_created(news_with_comments, client):
    url = reverse('news:detail', args=[news_with_comments.id])
    client.get(url)
    comments = Comment.objects.filter(news=news_with_comments).all()
    created_times = [comment.created for comment in comments]
    assert created_times == sorted(created_times)


@pytest.mark.django_db
def test_comments_form(client, user, news):
    url = reverse('news:detail', args=[news.id])

    # anonymous user
    anonym = client.get(url)
    assert 'form' not in anonym.context

    # authenticated user
    client.force_login(user)
    auth = client.get(url)
    assert 'form' in auth.context
