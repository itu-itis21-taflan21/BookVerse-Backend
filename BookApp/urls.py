from django.urls import path
from .views import AuthorView

urlpatterns = [
    path('get-author/<int:id>', AuthorView.as_view(), name='get-author'),

]