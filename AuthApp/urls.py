from django.urls import path
from .views import SignupView,VerifyEmailView,LoginView,RequestResetPassword,HandleResetPassword
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-email/<str:uid>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-password/',RequestResetPassword.as_view(),name = 'request-reset-password'),
    path('reset-password/<str:uid>/<str:token>/',HandleResetPassword.as_view(),name='reset-password')
]