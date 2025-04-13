import pytest
from django.utils import timezone
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def news_list():
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
def test_news_count_on_main_page(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def news_with_comments(news):
    Comment.objects.create(
        news=news,
        text='Comment text',
        created=timezone.now(),
    )
    Comment.objects.create(
        news=news,
        text='Comment text',
        created=timezone.now(),
    )

    return news


@pytest.mark.django_db
def test_comments_ordered_by_created(news_with_comments, client):
    url = reverse('news:detail', args=[news_with_comments.id])
    response = client.get(url)
    comments = response.context['news'].comment_set.all()
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
