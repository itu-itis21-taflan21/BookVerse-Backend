from django.urls import path
from .views import AuthorView,CategoryView,ProfileDeleteView,ProfileUpdateView

urlpatterns = [
    path('get-author/<int:id>', AuthorView.as_view(), name='get-author'),
    path('get-categories/', CategoryView.as_view(), name='get-categories'),
    path('reset-password/', ProfileUpdateView.as_view(), name='reset-password'),
    path('delete-user/', ProfileDeleteView.as_view(), name='delete-user')
]