from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    #path('login/', views.login_view, name='login'),
    #path('signup/', views.signup, name='signup'),
]