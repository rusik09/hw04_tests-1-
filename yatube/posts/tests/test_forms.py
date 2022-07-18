from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class FormsTest(TestCase):
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
            text='Тестовый текст для поста',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_form_is_valid(self):
        """Валидная форма создает запись в базе данных"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }

        response = self.authorised_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': self.user.username},)
        )
        last_post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group, self.group)
        self.assertEqual(last_post.author, self.user)

    def test_post_is_editing(self):
        """Валидная форма производит изменение поста в базе данных."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }

        response = self.authorised_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        first_post = Post.objects.get(id=self.group.id)
        self.assertEqual(first_post.text, form_data['text'])
        self.assertEqual(first_post.group, self.group)
        self.assertEqual(first_post.author, self.user)

    def test_post_create_anonymous(self):
        """Неавторизованный пользователь не может создать пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст'
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_create_url = reverse('posts:post_create')
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={post_create_url}')
        self.assertEqual(Post.objects.count(), posts_count)
