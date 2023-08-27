from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.list_url = reverse('notes:list')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author)

    def test_add_note_to_list(self):
        """"Заметка передаётся на страницу со списком."""
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_filter_notes_by_user(self):
        """в список заметок одного пользователя
        не попадают заметки другого пользователя."""
        self.client.force_login(self.reader)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        list_len = len(object_list)
        self.assertEqual(list_len, 0)

    def test_authorized_client_has_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, slug in urls:
            with self.subTest(name=name):
                url = reverse(name, args=slug)
                response = self.client.get(url)
                self.assertIn('form', response.context)
