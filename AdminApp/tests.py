from django.test import TestCase,override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from BookApp.models import Book,Category,UserComment,Author
from rest_framework import status
from rest_framework.test import APIClient

class AdminAPIAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', password='AdminPass123')
        self.regular_user = User.objects.create_user(username='regularuser', email='regular@example.com', password='RegularPass123')

        # Define admin endpoints
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
        
        Author.objects.create(
            id=10,
            name='Test Author'
        )
        Category.objects.create(
            id=25,
            name='Test Category'
        )
        # Create a book instance
        self.book = Book.objects.create(
            title='Test Book',
            author_id=10,  # Assuming an Author with ID 1 exists
            summary='Test Summary',
            cover='http://example.com/cover.jpg',
            category_id=25,  # Assuming a Category with ID 1 exists
            page_count=100,
            pdf_link='http://example.com/book.pdf'
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
        # Verify that the Category table still exists
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

        # Create an author instance
        self.author = Author.objects.create(name='Original Author Name')
        self.admin_authors_detail_url = reverse('admin-authors-detail', kwargs={'pk': self.author.pk})
        self.regular_authors_detail_url = reverse('admin-authors-detail', kwargs={'pk': self.author.pk})

    def test_admin_can_update_author(self):
        """
        Ensure that an admin user can successfully update an author's details.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Updated Author Name'}
        response = self.client.patch(self.admin_authors_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.author.refresh_from_db()
        self.assertEqual(self.author.name, 'Updated Author Name')

    def test_regular_user_cannot_update_author(self):
        """
        Ensure that a regular user cannot update an author's details and receives a 403 response.
        """
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

        # Create a category instance
        self.category = Category.objects.create(name='Original Category Name')
        self.admin_categories_detail_url = reverse('admin-categories-detail', kwargs={'pk': self.category.pk})
        self.regular_categories_detail_url = reverse('admin-categories-detail', kwargs={'pk': self.category.pk})

    def test_admin_can_update_category(self):
        """
        Ensure that an admin user can successfully update a category's details.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Updated Category Name'}
        response = self.client.patch(self.admin_categories_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category Name')

    def test_regular_user_cannot_update_category(self):
        """
        Ensure that a regular user cannot update a category's details and receives a 403 response.
        """
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'Hacked Category Name'}
        response = self.client.patch(self.admin_categories_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.category.refresh_from_db()
        self.assertNotEqual(self.category.name, 'Hacked Category Name')