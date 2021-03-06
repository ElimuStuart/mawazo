from django.test import TestCase
from django.shortcuts import reverse
from django.urls import resolve
from django.contrib.auth import get_user_model
from ..models import Post, Author
from ..forms import PostForm

User = get_user_model()

class PostCreateTests(TestCase):
    def setUp(self):
        author = User.objects.create_user(username="john", email="john@doe.com", password="12345")
        Author.objects.create(user=author)

    def test_csrf(self):
        url = reverse('blog:post_create')
        self.client.login(username='john', password='12345') # log the author in
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        url = reverse('blog:post_create')
        self.client.login(username='john', password='12345')
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm.__base__)


    def test_post_create_valid_post_data(self):
        url = reverse('blog:post_create')
        self.client.login(username='john', password='12345')
        data = {
            'title': 'Greeting',
            'content': 'Hello, world!',
        }
        response = self.client.post(url, data)
        self.assertTrue(Post.objects.exists())

    def test_post_create_invalid_post_data(self):
        # invalid post data should not redirect
        # the expected behavior is to show the form again with errors
        url = reverse('blog:post_create')
        self.client.login(username='john', password='12345')
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_post_create_invalid_post_data_empty_fields(self):
        # invalid post data should not redirect
        # the expected behavior is to show the form again with errors
        url = reverse('blog:post_create')
        self.client.login(username='john', password='12345')
        data = {
            'title': '',
            'content': ''
        }        
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Post.objects.exists())


class LoginRequiredPostCreateTests(TestCase):
    def setUp(self):
        self.url = reverse('blog:post_create')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))