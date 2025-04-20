from collections import namedtuple
from django.urls import reverse


SLUG = 'sample_slug'

URL_NAMES = (
    'home',
    'login',
    'logout',
    'signup',
    'add_note',
    'success',
    'notes_list',
    'note_detail',
    'edit_note',
    'delete_note',
)

URLS = namedtuple('URLs', URL_NAMES)

URLS_INSTANCE = URLS(
    reverse('notes:home'),
    reverse('users:login'),
    reverse('users:logout'),
    reverse('users:signup'),
    reverse('notes:add'),
    reverse('notes:success'),
    reverse('notes:list'),
    reverse('notes:detail', args=(SLUG,)),
    reverse('notes:edit', args=(SLUG,)),
    reverse('notes:delete', args=(SLUG,)),
)

PUBLIC_URL_NAMES = ['home', 'login', 'signup', 'logout']
AUTH_URL_NAMES = [
    'add_note',
    'success',
    'notes_list',
    'note_detail',
    'edit_note',
    'delete_note'
]
AUTHOR_ONLY_URL_NAMES = ['note_detail', 'edit_note', 'delete_note']
