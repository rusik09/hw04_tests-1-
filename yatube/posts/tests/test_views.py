from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostViewTests(TestCase):
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
            group=cls.group,
        )

    def setUp(self):
        self.user = User.objects.create(username='HasNoName')
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list': reverse(
                'posts:group_list', kwargs={'slug': 'Тестовый слаг'}),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': f'{self.user}'}),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}),
            'posts/create_post.html': reverse(
                'posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_uses_correct_template(self):
        response = self.authorised_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_home_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorised_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый пост')

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorised_client.get(
            reverse('posts:group_list', kwargs={'slug': 'Тестовый слаг'})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_group_0, self.group_1)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorised_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, self.user)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorised_client.get(
            reverse('posts:post_detail', kwargs={'username': 'auth'})
        )
        first_object = response.context['post'].text
        self.assertEqual(first_object, 'Тестовый пост')

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorised_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorised_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostViewTests.post_id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post_appears_on_pages(self):
        """Новый пост отображается на страницах group_list, profile, index"""
        template_pages_names = {
            reverse('post:index'): self.post.text,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): self.post.text,
            reverse('posts:profile',
                    kwargs={'usernsme': self.user.username}): self.post.text,
        }
        for value, expected in template_pages_names.items():
            with self.subTest(value=value):
                response = self.authorised_client.get(value)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.text, expected)

    def test_new_post_appears_in_correct_group(self):
        """Новый пост оторажается в нужной группе"""
        response = self.authorised_client.get(
            reverse('posts:group_list', kwargs={'slug': 'Тестовый слаг'})
        )
        form_fields = {
            'group': self.post.group
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.id, expected)

    def test_paginator(self):
        """Проверка паджинатоора"""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list': reverse(
                'posts:group_list', kwargs={'slug': 'Тестовый слаг'}),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': f'{self.user}'}),
        }
        for reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)
