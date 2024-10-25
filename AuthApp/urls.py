from django.urls import path
from .views import SignupView,VerifyEmailView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email/<str:uid>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
]