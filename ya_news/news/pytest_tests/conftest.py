import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='user',
        password='pass',
    )


@pytest.fixture
def author():
    return User.objects.create_user(
        username='author',
        password='pass',
    )


@pytest.fixture
def reader(db):
    return User.objects.create_user(
        username='reader',
        password='pass',
    )


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Тест',
        text='Тестовый текст',
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Комментарий',
    )


@pytest.fixture
def news_with_comments(news, user):
    Comment.objects.create(
        news=news,
        author=user,
        text='Comment text',
        created=timezone.now(),
    )
    return news
