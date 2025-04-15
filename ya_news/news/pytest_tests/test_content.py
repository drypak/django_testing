import pytest
from news.models import Comment
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_on_main_page(client, new_list, home_url):
    """Проверяем, что на главной странице не более 10 новостей.

    Так же проверяем, что количество новостей совпадает с количеством
    Новостей в БД. Для главной страницы.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() <= NEWS_COUNT_ON_HOME_PAGE
    assert object_list.count() == len(new_list)


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


@pytest.mark.parametrize(
    'client_fixture, form_class',
    [
        ('anonymous_client', False),
        ('authenticated_client', True),
    ]
)
def test_comment_form(
    client_fixture,
    form_class,
    request,
    news_url
):
    """Проверяет, что форма комментария доступна для анонимных
    и авторизованных пользователей.
    """
    client = request.getfixturevalue(client_fixture)
    response = client.get(news_url)

    assert response.status_code == 200

    form = response.context.get('form', None)

    if form_class:
        assert form is not None
        assert isinstance(form, CommentForm)
    else:
        assert form is None
