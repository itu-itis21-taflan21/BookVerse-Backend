from django.urls import path

from .views import AuthorView,ProfileView,CategoryView,ProfileUpdateView,ProfileDeleteView,BookView,FavoriteView,CommentView,RatingView,ReadListView

urlpatterns = [
    path('get-author/', AuthorView.as_view(), name='get-author'),
    path('get-user/', ProfileView.as_view(), name='get-user'),
    path('get-categories/', CategoryView.as_view(), name='get-categories'),
    path('reset-password/', ProfileUpdateView.as_view(), name='reset-password'),
    path('delete-user/', ProfileDeleteView.as_view(), name='delete-user'),
    path('get-book/',BookView.as_view(),name='get-book'),
    path('add-to-fav/',FavoriteView.as_view(),name='add-to-fav'),
    path('make-comment/',CommentView.as_view(),name='make-comment'),
    path('get-comment/',CommentView.as_view(),name='get-comment'),
    path('add-rating/',RatingView.as_view(),name='add-rating'),
    path('get-rating/',RatingView.as_view(),name='get-rating'),
    path('update-rating/',RatingView.as_view(),name='update-rating'),
    path('add-to-readlist/',ReadListView.as_view(),name='add-to-readlist'),
    path('get-fav/',FavoriteView.as_view(),name='get-fav'),
    path('get-readlist/',ReadListView.as_view(),name='get-readlist'),
]