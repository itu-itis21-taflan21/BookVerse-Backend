from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminUserViewSet,
    AdminBookViewSet,
    AdminAuthorViewSet,
    AdminCategoryViewSet,
    AdminUserCommentViewSet,
    # Add other Admin ViewSets here
)

router = DefaultRouter()
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')
router.register(r'admin/books', AdminBookViewSet, basename='admin-books')
router.register(r'admin/categories', AdminCategoryViewSet, basename='admin-categories')
router.register(r'admin/user-comments', AdminUserCommentViewSet, basename='admin-user-comments')

router.register(r'admin/authors', AdminAuthorViewSet, basename='admin-authors')

urlpatterns = [
    path('api/', include(router.urls)),
]