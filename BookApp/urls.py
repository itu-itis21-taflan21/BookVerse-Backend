from django.urls import path
from .views import AuthorView,ProfileView

urlpatterns = [
    path('get-author/<int:id>', AuthorView.as_view(), name='get-author'),
    path('get-user/<int:id>', ProfileView.as_view(), name='get-user'),
    

]