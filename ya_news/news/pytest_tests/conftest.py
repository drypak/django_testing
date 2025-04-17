import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.test import Client

from news.models import Comment, News

User = get_user_model()

pytestmark = pytest.mark.django_db


# --- Пользователи ---
@pytest.fixture
def user(db, request):
    """
    Фикстура для создания пользователя.
    Создает пользователя с уникальным именем.
    Используется в тестах где требуется уникальный пользователь для тестов.
    Имя генерируется на основе названия теста.
    """
    username = f'user-{request.node.name}'

    return User.objects.create_user(
        username=username,
        password='pass',
    )


@pytest.fixture
def author():
    """
    Фикстура для создания автора.
    Используется в тестах где требуется автор комментариев или новостей.
    """
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


# ---Объекты---
@pytest.fixture
def news(db):
    return News.objects.create(
        title='Тест',
        text='Тестовый текст',
    )


@pytest.fixture
def comment(news, user):
    return Comment.objects.create(
        news=news,
        author=user,
        text='initial comment text',
    )


@pytest.fixture
def news_with_comments(news, user):
    """Фикстура создаёт новость с 15 комментариями."""
    comments = [
        Comment(
            news=news,
            author=user,
            text=f'Comment {i}',
        )
        for i in range(1, 16)
    ]
    Comment.objects.bulk_create(comments)
    return news


@pytest.fixture
def new_list():
    News.objects.bulk_create(
        News(
            title=f'title{i}',
            text=f'text{i}',
            date=timezone.now(),
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    )


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_url(news):
    return reverse('news:detail', args=[news.id])


@pytest.fixture
def multi_comments(news_with_comments, user):
    comments = [
        Comment.objects.create(
            news=news_with_comments,
            text=f'Comment {i}',
            author=user,
            created=timezone.now(),
        )
        for i in range(1, 4)
    ]

    return comments


@pytest.fixture
def anonymous_client():
    client = Client()
    client.logout()
    return client


@pytest.fixture
def authenticated_client(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=[comment.id])


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=[comment.id])


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def auth_urls():
    return {
        'login': reverse('users:login'),
        'logout': reverse('users:logout'),
        'signup': reverse('users:signup'),
    }


@pytest.fixture
def other_user():
    return User.objects.create_user(
        username='otheruser',
        password='password'
    )
