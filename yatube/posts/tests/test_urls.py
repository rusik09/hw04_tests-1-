from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
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
        """Проверка доступности страниц для анонимного пользователя"""
        urls = (
            '/',
            '/profile/auth/',
            '/posts/1/',
        )
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_post_create(self):
        """Создание поста доступно авторизованному пользователю"""
        response = self.authorised_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_redirect_anonymous(self):
        """Страница создания поста перенаправляет анонимного пользователя"""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_post_edit(self):
        """Редактирование поста доступно автору"""
        url = f'/posts/{self.post.id}/edit/'
        response = self.authorised_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        """Проверка несуществующей страницы"""
        response = self.authorised_client.get('/pppppagge/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        template_url_names = {
            '': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in template_url_names.items():
            with self.subTest(address=address):
                respone = self.authorised_client.get(address)
                self.assertTemplateUsed(respone, template)
