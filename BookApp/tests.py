from django.test import TestCase
from django.contrib.auth.models import User
from .models import Book, Category, Author, FavBook, ReadList, UserComment, Rating
from .serializers import BookSerializer, CategorySerializer, AuthorSerializer, UserSerializer, RatingforUser,CommentsforUser, FavBookSerializer, ReadBooksSerializer,BasicUserSerializer,BasicAuthorSerializer,BasicCommentSerializer
from .models import Book, Category, Author, FavBook, UserComment, Rating, ReadList
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from unittest.mock import patch
from rest_framework.test import APITestCase
from unittest.mock import patch, Mock


class CategoryViewTests(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")
        self.author1 = Author.objects.create(name="Author 1")
        self.author2 = Author.objects.create(name="Author 2")
        self.book1 = Book.objects.create(
            title="Book 1", category=self.category1, author_id=self.author1.id, page_count=200, summary="Summary 1"
        )
        self.book2 = Book.objects.create(
            title="Book 2", category=self.category1, author_id=self.author2.id, page_count=300, summary="Summary 2"
        )

    def test_retrieve_all_categories(self):
        response = self.client.get(reverse('get-categories'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 2)  
        for category in response.json()['data']:
            self.assertIn('book_count', category)  

    def test_retrieve_category_by_id(self):
        response = self.client.get(reverse('get-categories'), {'category_id': self.category1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 1) 
        self.assertEqual(response.json()['data'][0]['name'], self.category1.name)

    def test_retrieve_category_with_no_books(self):
        response = self.client.get(reverse('get-categories'), {'category_id': self.category2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data'][0]['book_count'], 0) 

    def test_retrieve_nonexistent_category(self):
        response = self.client.get(reverse('get-categories'), {'category_id': 999})
        self.assertEqual(response.status_code, 200)  
        self.assertEqual(response.json()['data'], [])

    def test_retrieve_category_invalid_query(self):
        response = self.client.get(reverse('get-categories'), {'invalid_param': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 2) 


class ProfileUpdateViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='oldpassword')
        self.client.force_authenticate(user=self.user)

    def test_update_password_success(self):
        response = self.client.post(reverse('reset-password'), {'new_password': 'newpassword123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Password has been reset successfully.', response.data['message'])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_update_password_no_data(self):
        response = self.client.post(reverse('reset-password'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_password_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse('reset-password'), {'new_password': 'newpassword123'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_password_same_as_old(self):
        response = self.client.post(reverse('reset-password'), {'new_password': 'oldpassword'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('New password must be different from the current password', response.data['error'])

    def test_update_password_invalid_format(self):
        response = self.client.post(reverse('reset-password'), {'new_password': 'short'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data) 

    def test_update_password_complexity(self):
        response = self.client.post(reverse('reset-password'), {'new_password': 'simple'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)  


class ProfileDeleteViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

    def test_delete_profile_success(self):
        response = self.client.delete(reverse('delete-user'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('User profile deleted successfully.', response.data['message'])
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_delete_profile_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(reverse('delete-user'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# LGTM
class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

    def test_get_profile_success(self):
        response = self.client.get(reverse('get-user'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'], UserSerializer(self.user).data)

    def test_get_profile_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('get-user'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)     

# LGTM
class BookViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.author1 = Author.objects.create(name="Author One")
        self.author2 = Author.objects.create(name="Author Two")

        self.category1 = Category.objects.create(name="Category One")
        self.category2 = Category.objects.create(name="Category Two")

        self.book1 = Book.objects.create(
            title="Django for Beginners",
            author=self.author1,
            summary="A book for Django beginners.",
            cover="http://example.com/django.jpg",
            category=self.category1,
            page_count=300
        )
        self.book2 = Book.objects.create(
            title="Advanced Django",
            author=self.author1,
            summary="An advanced guide to Django.",
            cover="http://example.com/advanced_django.jpg",
            category=self.category1,
            page_count=500
        )
        self.book3 = Book.objects.create(
            title="Python Essentials",
            author=self.author2,
            summary="Essential Python programming concepts.",
            cover="http://example.com/python.jpg",
            category=self.category2,
            page_count=250
        )

    def test_get_book_by_valid_id(self):
        response = self.client.get(reverse('get-book'), {'book_id': self.book1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 1)
        self.assertEqual(response.json()['data'][0]['title'], self.book1.title)

    def test_get_book_by_invalid_id(self):
        response = self.client.get(reverse('get-book'), {'book_id': -1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.json())

    def test_get_books_with_valid_limit_and_offset(self):
        response = self.client.get(reverse('get-book'), {'limit': 2, 'offset': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 2)

    def test_get_books_with_invalid_limit(self):
        response = self.client.get(reverse('get-book'), {'limit': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

    def test_get_books_with_negative_offset(self):
        response = self.client.get(reverse('get-book'), {'offset': -1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

    def test_get_books_filtered_by_author(self):
        response = self.client.get(reverse('get-book'), {'author_id': self.author1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 2)

    def test_get_books_filtered_by_category(self):
        response = self.client.get(reverse('get-book'), {'category_id': self.category2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 1)

    def test_get_books_filtered_by_keyword(self):
        response = self.client.get(reverse('get-book'), {'s': 'Django'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 2)

    def test_get_books_with_invalid_author_id(self):
        response = self.client.get(reverse('get-book'), {'author_id': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

    def test_get_books_with_invalid_category_id(self):
        response = self.client.get(reverse('get-book'), {'category_id': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

    def test_get_books_with_no_parameters(self):
        response = self.client.get(reverse('get-book'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 3)

    def test_pagination_details_in_response(self):
        response = self.client.get(reverse('get-book'), {'limit': 2, 'offset': 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pagination = response.json().get('pagination', {})
        self.assertEqual(pagination['limit'], 2)
        self.assertEqual(pagination['offset'], 0)
        self.assertEqual(pagination['total'], 3)

    def test_get_books_with_multiple_filters(self):
        response = self.client.get(reverse('get-book'), {
            'author_id': self.author1.id,
            'category_id': self.category1.id,
            's': 'Advanced'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 1)
        self.assertEqual(response.json()['data'][0]['title'], self.book2.title)

    def test_get_books_with_invalid_pagination(self):
        response = self.client.get(reverse('get-book'), {'limit': -1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

class FavoriteViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='favoriteuser', email='favorite@example.com', password='favoritepass')
        self.author = Author.objects.create(name='Favorite Author')
        self.category = Category.objects.create(name='Favorite Category')
        self.book = Book.objects.create(
            id=1,
            title='Test Favorite Book',
            author=self.author,
            summary='A book for testing favorites.',
            cover='http://example.com/favorite.jpg',
            category=self.category,
            page_count=150
        )
        self.client.force_authenticate(user=self.user)

    def test_add_book_to_favorites_success(self):
        response = self.client.post(reverse('add-to-fav'), {'book_id': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertTrue(FavBook.objects.filter(user=self.user, book=self.book).exists())

    def test_remove_book_from_favorites_success(self):
        FavBook.objects.create(user=self.user, book=self.book)
        response = self.client.post(reverse('add-to-fav'), {'book_id': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertFalse(FavBook.objects.filter(user=self.user, book=self.book).exists())

    def test_add_book_already_in_favorites(self):
        FavBook.objects.create(user=self.user, book=self.book)
        response = self.client.post(reverse('add-to-fav'), {'book_id': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(FavBook.objects.filter(user=self.user, book=self.book).exists())

    def test_add_book_invalid_id(self):
        response = self.client.post(reverse('add-to-fav'), {'book_id': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_add_book_nonexistent_id(self):
        response = self.client.post(reverse('add-to-fav'), {'book_id': 9999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'No Book matches the given query.')

    def test_get_favorite_status_true(self):
        FavBook.objects.create(user=self.user, book=self.book)
        response = self.client.get(reverse('get-fav'), {'book_id': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['data'])

    def test_get_favorite_status_false(self):
        response = self.client.get(reverse('get-fav'), {'book_id': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['data'])

    def test_get_favorite_invalid_id(self):
        response = self.client.get(reverse('get-fav'), {'book_id': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_favorite_nonexistent_id(self):
        response = self.client.get(reverse('get-fav'), {'book_id': 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No Book matches the given query.')

    def test_add_favorite_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse('add-to-fav'), {'book_id': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_favorite_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('get-fav'), {'book_id': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CommentViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='commentuser', email='comment@example.com', password='commentpass')
        self.author = Author.objects.create(name='Comment Author')
        self.category = Category.objects.create(name='Comment Category')
        self.book = Book.objects.create(
            title='Test Comment Book',
            author=self.author,
            summary='A book for testing comments.',
            cover='http://example.com/comment.jpg',
            category=self.category,
            page_count=200
        )
        self.client.force_authenticate(user=self.user)

    def test_add_comment_success(self):
        data = {
            'book_id': self.book.id,
            'content': 'This is a test comment.'
        }
        response = self.client.post(reverse('make-comment'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserComment.objects.filter(user=self.user, book=self.book, content='This is a test comment.').exists())

    def test_add_comment_missing_content(self):
        data = {
            'book_id': self.book.id
        }
        response = self.client.post(reverse('make-comment'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_comment_invalid_book_id(self):
        data = {
            'book_id': 'invalid',
            'content': 'This is a test comment.'
        }
        response = self.client.post(reverse('make-comment'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_comment_nonexistent_book_id(self):
        data = {
            'book_id': 999,
            'content': 'This is a test comment.'
        }
        response = self.client.post(reverse('make-comment'), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_success(self):
        UserComment.objects.create(user=self.user, book=self.book, content='First comment')
        UserComment.objects.create(user=self.user, book=self.book, content='Second comment')
        response = self.client.get(reverse('get-comment'), {'book_id': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 2)

    def test_get_comments_no_comments(self):
        response = self.client.get(reverse('get-comment'), {'book_id': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_invalid_book_id(self):
        response = self.client.get(reverse('get-comment'), {'book_id': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_comments_nonexistent_book_id(self):
        response = self.client.get(reverse('get-comment'), {'book_id': 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'book_id': self.book.id,
            'content': 'This is a test comment.'
        }
        response = self.client.post(reverse('make-comment'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_comments_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('get-comment'), {'book_id': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RatingViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='ratinguser', email='rating@example.com', password='ratingpass')
        self.another_user = User.objects.create_user(username='anotheruser', email='another@example.com', password='anotherpass')
        
        self.author = Author.objects.create(name='Rating Author')
        self.category = Category.objects.create(name='Rating Category')
        
        self.book1 = Book.objects.create(
            title='Rating Book 1',
            author=self.author,
            summary='First rating book.',
            cover='http://example.com/rating1.jpg',
            category=self.category,
            page_count=150
        )
        self.book2 = Book.objects.create(
            title='Rating Book 2',
            author=self.author,
            summary='Second rating book.',
            cover='http://example.com/rating2.jpg',
            category=self.category,
            page_count=250
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_add_rating_success(self):
        data = {
            'book_id': self.book1.id,
            'rating': 4
        }
        response = self.client.post(reverse('add-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Rating added successfully.')
        self.assertTrue(Rating.objects.filter(user=self.user, book=self.book1, rating=4).exists())

    def test_add_rating_already_exists(self):
        Rating.objects.create(user=self.user, book=self.book1, rating=3)
        data = {
            'book_id': self.book1.id,
            'rating': 4
        }
        response = self.client.post(reverse('add-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_rating_success(self):
        Rating.objects.create(user=self.user, book=self.book1, rating=3)
        data = {
            'book_id': self.book1.id,
            'rating': 5
        }
        response = self.client.put(reverse('update-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Rating.objects.filter(user=self.user, book=self.book1, rating=5).exists())

    def test_update_rating_nonexistent(self):
        data = {
            'book_id':999999,
            'rating': 4
        }
        response = self.client.post(reverse('update-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_rating_invalid_book_id_format(self):
        data = {
            'book_id': 'invalid',
            'rating': 4
        }
        response = self.client.post(reverse('add-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_rating_invalid_rating_value_type(self):
        data = {
            'book_id': self.book1.id,
            'rating': 'five'
        }
        response = self.client.post(reverse('add-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_rating_out_of_range_low(self):
        data = {
            'book_id': self.book1.id,
            'rating': -1
        }
        response = self.client.post(reverse('add-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_rating_out_of_range_high(self):
        data = {
            'book_id': self.book1.id,
            'rating': 6
        }
        response = self.client.post(reverse('add-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_rating_invalid_rating_value_type(self):
        Rating.objects.create(user=self.user, book=self.book1, rating=3)
        data = {
            'book_id': self.book1.id,
            'rating': 'five'
        }
        response = self.client.post(reverse('update-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_rating_out_of_range_low(self):
        Rating.objects.create(user=self.user, book=self.book1, rating=3)
        data = {
            'book_id': self.book1.id,
            'rating': -2
        }
        response = self.client.post(reverse('update-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_rating_out_of_range_high(self):
        Rating.objects.create(user=self.user, book=self.book1, rating=3)
        data = {
            'book_id': self.book1.id,
            'rating': 10
        }
        response = self.client.post(reverse('update-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_rating_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'book_id': self.book1.id,
            'rating': 4
        }
        response = self.client.post(reverse('add-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_rating_unauthenticated(self):
        Rating.objects.create(user=self.user, book=self.book1, rating=3)
        self.client.force_authenticate(user=None)
        data = {
            'book_id': self.book1.id,
            'rating': 5
        }
        response = self.client.post(reverse('update-rating'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReadListViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='readlistuser', email='readlist@example.com', password='readlistpass')
        self.another_user = User.objects.create_user(username='anotheruser', email='another@example.com', password='anotherpass')
        
        self.author = Author.objects.create(name='ReadList Author')
        self.category = Category.objects.create(name='ReadList Category')
        
        self.book1 = Book.objects.create(
            title='ReadList Book 1',
            author=self.author,
            summary='First readlist book.',
            cover='http://example.com/readlist1.jpg',
            category=self.category,
            page_count=180
        )
        self.book2 = Book.objects.create(
            title='ReadList Book 2',
            author=self.author,
            summary='Second readlist book.',
            cover='http://example.com/readlist2.jpg',
            category=self.category,
            page_count=220
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_add_book_to_readlist_success(self):
        data = {'book_id': self.book1.id}
        response = self.client.post(reverse('add-to-readlist'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Book added to readlist successfully')
        self.assertTrue(ReadList.objects.filter(user=self.user, book=self.book1).exists())
    
    def test_remove_book_from_readlist_success(self):
        ReadList.objects.create(user=self.user, book=self.book1)
        data = {'book_id': self.book1.id}
        response = self.client.post(reverse('add-to-readlist'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Book removed from readlist successfully')
        self.assertFalse(ReadList.objects.filter(user=self.user, book=self.book1).exists())
    
    def test_add_book_to_readlist_invalid_book_id_format(self):
        data = {'book_id': 'invalid'}
        response = self.client.post(reverse('add-to-readlist'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid book ID format.')

    def test_add_book_to_readlist_nonexistent_book(self):
        data = {'book_id': 999}
        response = self.client.post(reverse('add-to-readlist'), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Book not found.')
    
    def test_add_book_to_readlist_missing_book_id(self):
        data = {}
        response = self.client.post(reverse('add-to-readlist'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Book ID is required.')

    def test_get_readlist_status_true(self):
        ReadList.objects.create(user=self.user, book=self.book1)
        response = self.client.get(reverse('get-readlist'), {'book_id': self.book1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertTrue(response.data['data'])

    def test_get_readlist_status_invalid_book_id_format(self):
        response = self.client.get(reverse('get-readlist'), {'book_id': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid book ID format.')

    def test_get_readlist_status_nonexistent_book_id(self):
        response = self.client.get(reverse('get-readlist'), {'book_id': 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Book not found.')
    
    def test_add_readlist_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {'book_id': self.book1.id}
        response = self.client.post(reverse('add-to-readlist'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_readlist_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('get-readlist'), {'book_id': self.book1.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class SemanticSearchViewTests(APITestCase):
    def test_semantic_search_invalid_input(self):
        response = self.client.post(reverse("semantic-search"), {"match_threshold": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("BookApp.views.client.rpc")
    def test_semantic_search_no_results(self, mock_rpc):
        mock_rpc.return_value.execute.return_value = Mock(data=[])
        
        response = self.client.post(reverse("semantic-search"), {"key": "test query"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("BookApp.views.client.rpc")
    def test_semantic_search_exception(self, mock_rpc):
        mock_rpc.return_value.execute.side_effect = Exception("Test exception")
        
        response = self.client.post(reverse("semantic-search"), {"key": "test query"})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecommendBooksViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.force_authenticate(user=self.user)
        
    def test_recommend_books_invalid_top_n(self):
        response = self.client.get(reverse("recommend-books"), {"top_n": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recommend_books_invalid_similarity_threshold(self):
        response = self.client.get(
            reverse("recommend-books"), {"similarity_threshold": "invalid"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("BookApp.views.client.rpc")
    def test_recommend_books_no_recommendations(self, mock_rpc):
        mock_rpc.return_value.execute.return_value = Mock(data=[])
        response = self.client.get(reverse("recommend-books"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("BookApp.views.client.rpc")
    def test_recommend_books_exception(self, mock_rpc):
        mock_rpc.return_value.execute.side_effect = Exception("Test exception")
        response = self.client.get(reverse("recommend-books"))
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

class ModelsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Fiction')
        self.author = Author.objects.create(name='John Doe')
        self.book = Book.objects.create(
            title='Sample Book',
            author=self.author,
            summary='A sample book summary.',
            cover='http://example.com/cover.jpg',
            category=self.category,
            page_count=300
        )

    def test_category_creation(self):
        category = Category.objects.create(name='Non-Fiction')
        self.assertEqual(str(category), 'Non-Fiction')

    def test_author_creation(self):
        author = Author.objects.create(name='Jane Smith')
        self.assertEqual(str(author), 'Jane Smith')

    def test_book_creation(self):
        self.assertEqual(str(self.book), 'Sample Book')
        self.assertEqual(self.book.page_count, 300)
        self.assertIsNone(self.book.embedding)

    def test_favbook_unique_constraint(self):
        FavBook.objects.create(user=self.user, book=self.book)
        with self.assertRaises(Exception):
            FavBook.objects.create(user=self.user, book=self.book)

    def test_readlist_unique_constraint(self):
        ReadList.objects.create(user=self.user, book=self.book)
        with self.assertRaises(Exception):
            ReadList.objects.create(user=self.user, book=self.book)

    def test_rating_unique_constraint(self):
        Rating.objects.create(user=self.user, book=self.book, rating=4)
        with self.assertRaises(Exception):
            Rating.objects.create(user=self.user, book=self.book, rating=5)

    def test_usercomment_creation(self):
        comment = UserComment.objects.create(user=self.user, book=self.book, content='Great book!')
        self.assertEqual(str(comment), 'Comment by testuser on Sample Book')


class SerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="serializeruser", password="testpass")
        self.category = Category.objects.create(name="Science Fiction")
        self.author = Author.objects.create(name="Isaac Asimov")
        self.book = Book.objects.create(
            title="Foundation",
            author=self.author,
            summary="A science fiction novel.",
            cover="http://example.com/foundation.jpg",
            category=self.category,
            page_count=255,
        )
        self.rating = Rating.objects.create(user=self.user, book=self.book, rating=5)
        self.comment = UserComment.objects.create(user=self.user, book=self.book, content="Excellent read.")
        self.category.book_count = Book.objects.filter(category=self.category).count()
        self.author.book_count = Book.objects.filter(author=self.author).count()
        self.author.average_rating = 5.0

    def test_book_serializer(self):
        serializer = BookSerializer(self.book)
        expected_data = {
            'id': self.book.id,
            'title': 'Foundation',
            'cover': 'http://example.com/foundation.jpg',
            'author': {
                'id': self.author.id,
                'name': 'Isaac Asimov'
            },
            'summary': 'A science fiction novel.',
            'category': {
                'id': self.category.id,
                'name': 'Science Fiction',
                'book_count': 1
            },
            'page_count': 255,
            'average_rating': 5.0
        }
        self.assertEqual(serializer.data, expected_data)

    def test_author_serializer(self):
        serializer = AuthorSerializer(self.author)
        expected_data = {
            "id": self.author.id,
            "name": "Isaac Asimov",
            "book_count": 1,
            "average_rating": 5.0,
            "book_books": [
                {
                    "id": self.book.id,
                    "title": "Foundation",
                    "cover": "http://example.com/foundation.jpg",
                    "page_count": 255,
                }
            ],
        }
        self.assertEqual(serializer.data, expected_data)

    def test_favbook_serializer(self):
        fav_book = FavBook.objects.create(user=self.user, book=self.book)
        serializer = FavBookSerializer(fav_book)
        expected_data = {
            "id": fav_book.id,
            "book": {
                "id": self.book.id,
                "title": "Foundation",
                "cover": "http://example.com/foundation.jpg",
                "page_count": 255,
            },
        }
        self.assertEqual(serializer.data, expected_data)

    def test_readbooks_serializer(self):
        read_list = ReadList.objects.create(user=self.user, book=self.book)
        serializer = ReadBooksSerializer(read_list)
        expected_data = {
            "id": read_list.id,
            "book": {
                "id": self.book.id,
                "title": "Foundation",
                "cover": "http://example.com/foundation.jpg",
                "page_count": 255,
            },
        }
        self.assertEqual(serializer.data, expected_data)

    def test_user_serializer(self):
        serializer = UserSerializer(self.user)
        expected_data = {
            "id": self.user.id,
            "username": "serializeruser",
            "email": "",
            "is_superuser": False,
            "date_joined": self.user.date_joined.isoformat().replace("+00:00", "Z"),
            "fav_user": [],
            "read_user": [],
            "comment_user": [{"id": self.comment.id, "content": "Excellent read."}],
            "rating_user": [{"id": self.rating.id, "rating": 5}],
        }
        self.assertEqual(serializer.data, expected_data)

    def test_category_serializer(self):
        serializer = CategorySerializer(self.category)
        expected_data = {
            'id': self.category.id,
            'name': 'Science Fiction',
            'book_count': 1
        }
        self.assertEqual(serializer.data, expected_data)

    def test_basic_author_serializer(self):
        serializer = BasicAuthorSerializer(self.author)
        expected_data = {
            "id": self.author.id,
            "name": "Isaac Asimov",
        }
        self.assertEqual(serializer.data, expected_data)

    def test_basic_user_serializer(self):
        serializer = BasicUserSerializer(self.user)
        expected_data = {
            "id": self.user.id,
            "username": "serializeruser",
        }
        self.assertEqual(serializer.data, expected_data)

    def test_commentsforuser_serializer(self):
        serializer = CommentsforUser(self.comment)
        expected_data = {
            "id": self.comment.id,
            "content": "Excellent read.",
        }
        self.assertEqual(serializer.data, expected_data)

    def test_ratingforuser_serializer(self):
        serializer = RatingforUser(self.rating)
        expected_data = {
            "id": self.rating.id,
            "rating": 5,
        }
        self.assertEqual(serializer.data, expected_data)

    def test_basic_comment_serializer(self):
        serializer = BasicCommentSerializer(self.comment)
        expected_data = {
            "id": self.comment.id,
            "content": "Excellent read.",
            "book_id": self.book.id,
            "user_id": self.user.id,
            "user": {"id": self.user.id, "username": "serializeruser"},
            "date": self.comment.date.isoformat().replace("+00:00", "Z"),
        }
        self.assertEqual(serializer.data, expected_data)