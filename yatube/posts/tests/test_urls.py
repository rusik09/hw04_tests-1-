from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_guest_client_status_code(self):
        urls = (
            '/',
            '/profile/<str:username>/',
            '/posts/<int:post_id>/',
            '/create/',
        )
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_post_create(self):
        response = self.authorised_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_redirect_anonymous(self):
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_post_edit(self):
        url = f'/posts/{self.post.id}/edit/'
        response = self.authorised_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        response = self.authorised_client.get('/pppppagge/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        template_url_names = {
            '': '/',
            'group/<slug:slug>/': '/group/<slug:slug>/',
            'profile/<str:username>/': '/profile/<str:username>/',
            'posts/<int:post_id>/': '/posts/<int:post_id>/',
            'create/': '/create/',
            'posts/<int:post_id>/edit/': '/posts/<int:post_id>/edit/',
        }
        for template, address in template_url_names.items():
            with self.subTest(address=address):
                respone = self.authorised_client.get(address)
                self.assertTemplateUsed(respone, template)
