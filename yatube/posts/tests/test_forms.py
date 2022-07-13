from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class FormsTest(TestCase):
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
            text='Тестовый текст для поста',
            group=cls.group,
        )

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(FormsTest.user)

    def test_form_is_valid(self):
        """Валидная форма создает запись в базе данных"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': 'Тестовая группа',
        }

        response = self.authorised_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username},)
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group
            )
        )

    def test_post_is_editing(self):
        """Валидная форма производит изменение поста в базе данных."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': 'Тестовая группа',
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
        first_post = Post.objects.first()
        self.assertEqual(
            first_post.text,
            'Тестовый текст'
        )
        self.assertEqual(
            first_post.group.title,
            'Тестовая группа'
        )
