import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from news.models import Comment


User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(
        username='author',
        password='pass',
    )


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(
        username='reader',
        password='pass',
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Comment text',
    )


@pytest.mark.django_db
def test_home_and_detail_avilable_for_anonymous_user(client, news):
    home_url = reverse('news:home')
    detail_url = reverse('news:detail', args=[news.id])

    assert client.get(home_url).status_code == 200
    assert client.get(detail_url).status_code == 200


@pytest.mark.django_db
def test_edit_delete_pages_for_comment_author(client, comment, author):
    client.force_login(author)
    edit_url = reverse('news:edit', args=[comment.id])
    delete_url = reverse('news:delete', args=[comment.id])

    assert client.get(edit_url).status_code == 200
    assert client.get(delete_url).status_code == 200


@pytest.mark.django_db
def test_edit_delete_redirects_anonymous_user(client, comment):
    edit_url = reverse('news:edit', args=[comment.id])
    delete_url = reverse('news:delete', args=[comment.id])
    login_url = reverse('users:login')

    edit_response = client.get(edit_url)
    delete_response = client.get(delete_url)

    assert edit_response.status_code == 302
    assert delete_response.status_code == 302

    assert edit_response.url.startswith(login_url)
    assert delete_response.url.startswith(login_url)


@pytest.mark.django_db
def test_cannot_edit_or_delete_foreign_comment(client, comment, reader):
    client.force_login(reader)

    edit_url = reverse('news:edit', args=[comment.id])
    delete_url = reverse('news:delete', args=[comment.id])

    assert client.get(edit_url).status_code == 404
    assert client.get(delete_url).status_code == 404


@pytest.mark.parametrize(
    'url',
    [
        'users:login',
        'users:logout',
        'users:signup',
    ]

)
@pytest.mark.django_db
def test_auth_pages_accessible_for_anonymous_user(client, url):
    url_name = reverse(url)
    response = client.get(url_name)
    assert response.status_code == 200
