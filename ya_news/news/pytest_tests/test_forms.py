import pytest
from django.urls import reverse
from news.models import Comment
from news.forms import BAD_WORDS
from http import HTTPStatus


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_form_rejects_bad_words(authenticated_client, news, bad_word):
    """Система отклоняет комментарии с запрещенными словами."""
    url = reverse('news:detail', args=[news.id])
    data = {'text': bad_word}

    response = authenticated_client.post(url, data=data)

    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    form = response.context['form']
    assert not form.is_valid()
    assert 'text' in form.errors
    assert Comment.objects.filter(text=bad_word).count() == 0
