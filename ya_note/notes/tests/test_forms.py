from notes.models import Note

from .base_test import (
    BaseTestCase,
    URLS_INSTANCE,
)


class TestNoteForm(BaseTestCase):
    def test_pages_contain_form_context(self):
        """Страницы содержат контекст с формой."""
        pages_with_form = (
            (URLS_INSTANCE.add_note, False),
            (URLS_INSTANCE.edit_note, True),
        )
        for url, has_obj in pages_with_form:
            with self.subTest(url=url):
                response = self.user_client.get(url)
                self.assertIn('form', response.context)

                if has_obj:
                    self.assertIn('object', response.context)
                    self.assertIsInstance(response.context['object'], Note)
                else:
                    self.assertNotIn('object', response.context)
