from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache

class AuthViewsTest(TestCase):
    # Override 
    # Called before each test case.
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.request_reset_password_url = reverse('request-reset-password')
        
        # Test user save it to use later
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='MySecurePass1'
        )
        self.test_user.is_active = True
        self.test_user.save()
        cache.clear()  
  
    def test_signup_success(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'MySecurePass1'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # It doesnt send an email
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_signup_missing_fields(self):
        data = {'username': 'newuser'}
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_duplicate_email(self):
        data = {
            'username': 'another',
            'email': 'test@example.com',
            'password': 'MySecurePass1'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_invalid_email(self):
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'MySecurePass1'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_weak_password(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': '123'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_duplicate_username(self):
        data = {
            'username': 'testuser',  
            'email': 'unique@example.com',
            'password': 'MySecurePass1'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_signup_empty_fields(self):
        data = {
            'username': '',
            'email': '',
            'password': ''
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_extra_fields(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'MySecurePass1',
            'extra_field': 'extra_value'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_signup_long_username(self):
        data = {
            'username': 'a' * 300, 
            'email': 'new@example.com',
            'password': 'MySecurePass1'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_verify_email_success(self):
        user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',
            password='MySecurePass1'
        )
        user.is_active = False
        user.save()

        # Simulate this token generation.
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        verify_url = reverse('verify-email', kwargs={'uid': uid, 'token': token})
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_verify_email_invalid_token(self):
        user = User.objects.create_user(
            username='unverified1',
            email='unverified1@example.com',
            password='MySecurePass1'
        )
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token = "invalidtoken"

        verify_url = reverse('verify-email', kwargs={'uid': uid, 'token': invalid_token})
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_verify_email_invalid_uid(self):
        user = User.objects.create_user(
            username='unverified2',
            email='unverified2@example.com',
            password='MySecurePass1'
        )
        user.is_active = False
        user.save()

        invalid_uid = urlsafe_base64_encode(force_bytes(99999))  
        token = default_token_generator.make_token(user)

        verify_url = reverse('verify-email', kwargs={'uid': invalid_uid, 'token': token})
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_verify_email_already_active(self):
        user = User.objects.create_user(
            username='verified',
            email='verified@example.com',
            password='MySecurePass1'
        )
        user.is_active = True 
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        verify_url = reverse('verify-email', kwargs={'uid': uid, 'token': token})
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        data = {
            'email': 'test@example.com',
            'password': 'MySecurePass1'
        }

        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_inactive_user(self):
        user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='MySecurePass1'
        )
        user.is_active = False
        user.save()

        data = {
            'email': 'inactive@example.com',
            'password': 'MySecurePass1'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

    def test_login_invalid_credentials(self):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        data = {'email': 'test@example.com'}  
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        data = {
            'email': 'nonexistent@example.com',
            'password': 'pass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_login_invalid_email_format(self):
        data = {
            'email': 'invalidemail',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_password_reset_success(self):
        data = {'email': 'test@example.com'}
        response = self.client.post(self.request_reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        
    def test_request_password_reset_nonexistent_email(self):
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.request_reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_request_password_reset_invalid_email_format(self):
        data = {'email': 'invalid-email'}
        response = self.client.post(self.request_reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_request_password_reset_missing_email(self):
        data = {}
        response = self.client.post(self.request_reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_request_password_reset_inactive_user(self):
        self.test_user.is_active = False
        self.test_user.save()
        data = {'email': 'test@example.com'}
        response = self.client.post(self.request_reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_handle_password_reset_success(self):
        user = self.test_user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = reverse('reset-password', kwargs={'uid': uid, 'token': token})
        
        data = {'new_password': 'newpassword123'}
        response = self.client.post(reset_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        login_data = {
            'email': 'test@example.com',
            'password': 'newpassword123'
        }
        login_response = self.client.post(self.login_url, login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_handle_password_reset_invalid_token(self):
        user = self.test_user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = reverse('reset-password', kwargs={'uid': uid, 'token': 'invalid-token'})
        
        data = {'new_password': 'newpassword123'}
        response = self.client.post(reset_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_handle_password_reset_invalid_uid(self):
        user = self.test_user
        token = default_token_generator.make_token(user)
        invalid_uid = urlsafe_base64_encode(force_bytes(99999))
        reset_url = reverse('reset-password', kwargs={'uid': invalid_uid, 'token': token})
        
        data = {'new_password': 'newpassword123'}
        response = self.client.post(reset_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_handle_password_reset_weak_password(self):
        user = self.test_user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = reverse('reset-password', kwargs={'uid': uid, 'token': token})
        
        data = {'new_password': '123'}  
        response = self.client.post(reset_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_handle_password_reset_missing_password(self):
        user = self.test_user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = reverse('reset-password', kwargs={'uid': uid, 'token': token})
        
        data = {}  
        response = self.client.post(reset_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_handle_password_reset_inactive_user(self):
        user = self.test_user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        user.is_active = False
        user.save()
        
        reset_url = reverse('reset-password', kwargs={'uid': uid, 'token': token})
        data = {'new_password': 'newpassword123'}
        response = self.client.post(reset_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_handle_password_reset_same_password(self):
        user = self.test_user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = reverse('reset-password', kwargs={'uid': uid, 'token': token})
        data = {'new_password': 'MySecurePass1'} 
        response = self.client.post(reset_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_max_attempts(self):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        for _ in range(5):
            response = self.client.post(self.login_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        data['password'] = 'testpass123'
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_login_attempts_reset_after_success(self):
        for _ in range(3):
            response = self.client.post(self.login_url, {
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'MySecurePass1'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
