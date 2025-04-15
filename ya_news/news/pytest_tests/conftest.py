import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

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
def news_with_comments(db):
    """
    Фикстура для создания новости с комментариями.

    Используется в тестах где требуется новость с комментариями.
    Создает новость с двумя комментариями.
    """
    news = News.objects.create(
        title='Тест',
        text='Тестовый текст',
    )
    user = User.objects.create_user(
        username='user',
        password='pass',
    )
    Comment.objects.create(
        news=news,
        author=user,
        text='коммент 1',
    )
    Comment.objects.create(
        news=news,
        author=user,
        text='коммент 2',
    )
    return news


@pytest.fixture
def new_list():
    new_objects = [
        News(
            title=f'Title {i}',
            text=f'Text {i}',
            date=timezone.now(),
        )
        for i in range(NEWS_COUNT_ON_HOME_PAGE)
    ]
    News.objects.bulk_create(new_objects)
    return new_objects


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
def anonymous_client(client):
    return client


@pytest.fixture
def authenticated_client(client):
    user = User.objects.create_user(
        username='testuser',
        password='testpass',
    )
    client.force_login(user)
    return client


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=[comment.id])


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=[comment.id])


@pytest.fixture
def author_client(client, author):
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
