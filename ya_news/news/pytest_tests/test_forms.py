import pytest

from news.forms import CommentForm, BAD_WORDS


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_form_rejects_bad_words(bad_word):
    """
    Проверяет, что форма комментария
    Отклоняет слова, содержащие запрещенные слова/
    """
    form = CommentForm(data={'text': bad_word})
    assert not form.is_valid()
    assert 'text' in form.errors
