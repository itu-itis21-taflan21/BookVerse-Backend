from django.urls import path

from .views import AuthorView,ProfileView,CategoryView,ProfileUpdateView,ProfileDeleteView,BookView,AddBookToFav,CommentView,AddRatingToBook

urlpatterns = [
    path('get-author/', AuthorView.as_view(), name='get-author'),
    path('get-user/<int:id>', ProfileView.as_view(), name='get-user'),
    path('get-categories/', CategoryView.as_view(), name='get-categories'),
    path('reset-password/', ProfileUpdateView.as_view(), name='reset-password'),
    path('delete-user/', ProfileDeleteView.as_view(), name='delete-user'),
    path('get-book/',BookView.as_view(),name='get-book'),
    path('add-to-fav/',AddBookToFav.as_view(),name='add-to-fav'),
    path('comment/',CommentView.as_view(),name='comment'),
    path('add-rating/',AddRatingToBook.as_view(),name='add-rating'),
]