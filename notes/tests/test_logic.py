from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.form_data = {'title': 'Заголовок', 'text': 'Текст'}

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        self.auth_client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_check_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        for _ in '11':
            self.auth_client.post(self.url, data={'title': 'Заголовок',
                                                  'text': 'Текст',
                                                  'slug': 'slug'})
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)


class TestPostEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст заметки'

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователя-автора заметки.
        cls.author = User.objects.create(username='Автор заметки')
        # Создаём клиент для пользователя-автора.
        cls.author_client = Client()
        # "Логиним" пользователя-автора в клиенте.
        cls.author_client.force_login(cls.author)
        # Делаем всё то же самое для пользователя-читателя.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Создаём объект заметки.
        cls.note = Note.objects.create(title='Заголовок',
                                       text=cls.NOTE_TEXT,
                                       author=cls.author)
        # URL для редактирования заметки.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        # URL для удаления заметки.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        # Формируем данные для POST-запроса по обновлению заметки.
        cls.form_data = {'text': cls.NEW_NOTE_TEXT}
        cls.url_to_note = reverse('notes:success')

    def test_author_can_delete_comment(self):
        """Пользователь может редактировать и удалять свои заметки."""
        # От имени автора заметки отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к разделу.
        # Заодно проверим статус-коды ответов.
        self.assertRedirects(response, self.url_to_note)
        # Считаем количество заметок в системе.
        notes_count = Note.objects.count()
        # Ожидаем ноль заметок в системе.
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_comment_of_another_user(self):
        """Пользователь не может редактировать или удалять чужие."""
        # Выполняем запрос на удаление от пользователя-читателя.
        response = self.reader_client.delete(self.delete_url)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что заметка по-прежнему на месте.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
