from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.throttling import BaseThrottle
from django.template.loader import render_to_string

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 60 * 15
MIN_PASSWORD_LENGTH = 8


class SignupView(APIView):
    def post(self, request):
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')

        if not all([username, email, password]):
            return Response(
                {"error": "All fields are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"error": "Invalid email format"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(username) > 150:  
            return Response(
                {"error": "Username is too long"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(password)
        except ValidationError as e:
            return Response(
                {"error": list(e.messages)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"error": "Email already exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username__iexact=username).exists():
            return Response(
                {"error": "Username already exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.is_active = False
            user.save()
            self.send_verification_email(user)
            return Response(
                {"message": "User created. Please check your email to activate your account."}, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def send_verification_email(self, user):
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"
        
        send_mail(
            subject="Verify your email",
            message=f"Click the link to verify your email: {verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message = render_to_string('email/verify_email.html', {
                'user': user,
                'verification_link': verification_link
            })
        )
    
class VerifyEmailView(APIView):
    def get(self, request, uid, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            
            if user.is_active:
                return Response(
                    {"error": "Email is already verified"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not token_generator.check_token(user, token):
                return Response(
                    {"error": "Invalid or expired verification token"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.is_active = True
            user.save()
            
            # Generate tokens for automatic login after verification
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Email verified successfully",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            }, status=status.HTTP_200_OK)

        except (TypeError, ValueError, OverflowError):
            return Response(
                {"error": "Invalid verification link"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')

        if not email or not password:
            return Response(
                {"error": "Both email and password are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f'login_attempts_{email}'
        attempts = cache.get(cache_key, 0)

        if attempts >= MAX_LOGIN_ATTEMPTS:
            return Response(
                {
                    'error': 'Too many failed login attempts',
                    'wait_time': f'{LOCKOUT_TIME//60} minutes'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        try:
            user = User.objects.get(email=email)
            
            if not user.is_active:
                return Response(
                    {"error": "Please verify your email first"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.check_password(password):
                cache.delete(cache_key)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'username': user.username,
                    'email': user.email,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                cache.set(cache_key, attempts + 1, LOCKOUT_TIME)
                return Response(
                    {"error": "Invalid credentials"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except User.DoesNotExist:
            cache.set(cache_key, attempts + 1, LOCKOUT_TIME)
            return Response(
                {"error": "Invalid credentials"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
 
class RequestResetPassword(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            # Add check for inactive user
            if not user.is_active:
                return Response(
                    {"error": "Account is not active. Please verify your email first"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = token_generator.make_token(user)    
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            send_mail(
                "Password Reset",
                f"Click the link to reset your password: {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=render_to_string('email/password_reset.html', {
                    'user': user,
                    'reset_link': reset_link
                })
            )

            return Response(
                {"message": "Password reset link sent to your email"}, 
                status=status.HTTP_201_CREATED
            )
            
        except User.DoesNotExist:
            return Response(
                {"error": "No user found with this email"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    

class HandleResetPassword(APIView):
    def post(self, request, uid, token):
        if not request.data.get('new_password'):
            return Response(
                {"error": "New password is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)

            # Check token first
            if not token_generator.check_token(user, token):
                return Response(
                    {"error": "Invalid or expired reset link"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Then check if user is active
            if not user.is_active:
                return Response(
                    {"error": "Account is not active. Please verify your email first"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_password = request.data.get('new_password')
            
            try:
                validate_password(new_password)
            except ValidationError as e:
                return Response(
                    {"error": list(e.messages)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.check_password(new_password):
                return Response(
                    {"error": "New password must be different from current password"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()

            RefreshToken.for_user(user)

            # Send confirmation email
            send_mail(
                "Password Reset Successful",
                "Your password has been successfully reset. If you didn't make this change, please contact support immediately.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=render_to_string('email/password_reset_success.html', {
                    'user': user
                })
            )

            return Response({
                "message": "Password reset successful. You can now login with your new password."
            }, status=status.HTTP_200_OK)

        except (TypeError, ValueError, OverflowError):
            return Response(
                {"error": "Invalid reset link format"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_400_BAD_REQUEST
            )



