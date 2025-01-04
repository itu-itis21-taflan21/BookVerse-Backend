from django.test import TestCase,override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from BookApp.models import Book,Category,UserComment,Author
from rest_framework import status
from rest_framework.test import APIClient
from .serializers import (
    AdminUserSerializer,
    AdminBookSerializer,
    AdminAuthorSerializer,
    AdminCategorySerializer,
    AdminUserCommentSerializer,
)
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class AdminAPIAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', password='AdminPass123')
        self.regular_user = User.objects.create_user(username='regularuser', email='regular@example.com', password='RegularPass123')

        self.admin_users_url = reverse('admin-users-list')
        self.admin_books_url = reverse('admin-books-list')

    def test_admin_user_can_access_admin_endpoints(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.admin_users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.admin_books_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_access_admin_endpoints(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.admin_users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(self.admin_books_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_cannot_access_admin_endpoints(self):
        response = self.client.get(self.admin_users_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.admin_books_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ObjectLevelPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', password='AdminPass123')
        self.regular_user = User.objects.create_user(username='regularuser', email='regular@example.com', password='RegularPass123')

        Author.objects.create(id=10, name='Test Author')
        Category.objects.create(id=25, name='Test Category')

        self.book = Book.objects.create(
            title='Test Book',
            author_id=10,  
            summary='Test Summary',
            cover='http://example.com/cover.jpg',
            category_id=25,  
            page_count=100
        )

        self.admin_books_detail_url = reverse('admin-books-detail', kwargs={'pk': self.book.pk})
        self.regular_books_detail_url = reverse('admin-books-detail', kwargs={'pk': self.book.pk})

    def test_admin_can_update_book(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'title': 'Updated Test Book'}
        response = self.client.patch(self.admin_books_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Updated Test Book')

    def test_regular_user_cannot_update_book(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {'title': 'Hacked Title'}
        response = self.client.patch(self.admin_books_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.book.refresh_from_db()
        self.assertNotEqual(self.book.title, 'Hacked Title')



class SQLInjectionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='adminuser', email='adminsql@example.com', password='AdminPass123')
        self.category_url = reverse('admin-categories-list')

    def test_sql_injection_in_category_name(self):
        self.client.force_authenticate(user=self.admin_user)
        malicious_input = "New Category'); DROP TABLE BookApp_category;--"
        data = {'name': malicious_input}
        response = self.client.post(self.category_url, data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
        try:
            Category.objects.all()
            table_exists = True
        except:
            table_exists = False
        self.assertTrue(table_exists)


class SensitiveDataExposureTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', password='AdminPass123')
        self.user = User.objects.create_user(username='safeguarduser', email='safeguard@example.com', password='SafePass123')
        self.admin_users_url = reverse('admin-users-list')

    def test_admin_user_response_does_not_expose_passwords(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.admin_users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user_data in response.data:
            self.assertNotIn('password', user_data)
            self.assertNotIn('password1', user_data)
            self.assertNotIn('password2', user_data)


class AdminAPIAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', password='AdminPass123')
        self.regular_user = User.objects.create_user(username='regularuser', email='regular@example.com', password='RegularPass123')

        self.author = Author.objects.create(name='Original Author Name')
        self.admin_authors_detail_url = reverse('admin-authors-detail', kwargs={'pk': self.author.pk})
        self.regular_authors_detail_url = reverse('admin-authors-detail', kwargs={'pk': self.author.pk})

    def test_admin_can_update_author(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Updated Author Name'}
        response = self.client.patch(self.admin_authors_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.author.refresh_from_db()
        self.assertEqual(self.author.name, 'Updated Author Name')

    def test_regular_user_cannot_update_author(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'Hacked Author Name'}
        response = self.client.patch(self.admin_authors_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.author.refresh_from_db()
        self.assertNotEqual(self.author.name, 'Hacked Author Name')

class AdminAPIAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', password='AdminPass123')
        self.regular_user = User.objects.create_user(username='regularuser', email='regular@example.com', password='RegularPass123')

        self.category = Category.objects.create(name='Original Category Name')
        self.admin_categories_detail_url = reverse('admin-categories-detail', kwargs={'pk': self.category.pk})
        self.regular_categories_detail_url = reverse('admin-categories-detail', kwargs={'pk': self.category.pk})

    def test_admin_can_update_category(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Updated Category Name'}
        response = self.client.patch(self.admin_categories_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category Name')

    def test_regular_user_cannot_update_category(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'Hacked Category Name'}
        response = self.client.patch(self.admin_categories_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.category.refresh_from_db()
        self.assertNotEqual(self.category.name, 'Hacked Category Name')

class AdminSerializersTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.author = Author.objects.create(name="Author Name")
        self.category = Category.objects.create(name="Category Name")
        self.book = Book.objects.create(title="Book Title", author=self.author, category=self.category, summary="Test summary", page_count=200)
        self.comment = UserComment.objects.create(user=self.user, book=self.book, content="Great book!")

    def test_admin_user_serializer_valid(self):
        serializer = AdminUserSerializer(self.user)
        self.assertEqual(serializer.data['username'], 'testuser')
        self.assertEqual(serializer.data['email'], 'test@example.com')
        self.assertTrue(serializer.data['is_active'])

    def test_admin_user_serializer_invalid(self):
        data = {'username': '', 'email': 'invalidemail'}
        serializer = AdminUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertIn('email', serializer.errors)

    def test_admin_book_serializer_valid(self):
        serializer = AdminBookSerializer(self.book)
        self.assertEqual(serializer.data['title'], 'Book Title')
        self.assertEqual(serializer.data['author'], self.author.id)
        self.assertEqual(serializer.data['category'], self.category.id)

    def test_admin_book_serializer_invalid(self):
        data = {'title': '', 'author': 'invalid_author_id', 'category': 'invalid_category_id'}
        serializer = AdminBookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        self.assertIn('author', serializer.errors)
        self.assertIn('category', serializer.errors)

    def test_admin_author_serializer_valid(self):
        serializer = AdminAuthorSerializer(self.author)
        self.assertEqual(serializer.data['name'], 'Author Name')

    def test_admin_author_serializer_invalid(self):
        data = {'name': ''}
        serializer = AdminAuthorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_admin_category_serializer_valid(self):
        serializer = AdminCategorySerializer(self.category)
        self.assertEqual(serializer.data['name'], 'Category Name')

    def test_admin_category_serializer_invalid(self):
        data = {'name': ''}
        serializer = AdminCategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_admin_user_comment_serializer_valid(self):
        serializer = AdminUserCommentSerializer(self.comment)
        self.assertEqual(serializer.data['content'], 'Great book!')
        self.assertEqual(serializer.data['user'], self.user.username)
        self.assertEqual(serializer.data['book'], self.book.title)

    def test_admin_user_comment_serializer_invalid(self):
        data = {'content': '', 'user': 'invalid_user_id', 'book': 'invalid_book_id'}
        serializer = AdminUserCommentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)
        self.assertIn('user', serializer.errors)
        self.assertIn('book', serializer.errors)