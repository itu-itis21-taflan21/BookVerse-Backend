from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from .serializers import AdminUserSerializer,AdminAuthorSerializer,AdminCategorySerializer,AdminUserCommentSerializer
from BookApp.models import Book,Author,Category,UserComment
from .serializers import AdminBookSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class AdminUserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    Only accessible by admin users.
    """
    serializer_class = AdminUserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

class AdminBookViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing book instances.
    Only accessible by admin users.
    """
    serializer_class = AdminBookSerializer
    queryset = Book.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

class AdminCategoryViewSet(viewsets.ModelViewSet):
    """
    Admin API for managing categories.
    """
    queryset = Category.objects.all()
    serializer_class = AdminCategorySerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

class AdminUserCommentViewSet(viewsets.ModelViewSet):
    """
    Admin API for managing user comments.
    Allows viewing, editing, and deleting inappropriate comments.
    """
    queryset = UserComment.objects.select_related('user', 'book').all()
    serializer_class = AdminUserCommentSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user__username', 'book__title', 'date']
    search_fields = ['content', 'user__username', 'book__title']
    ordering_fields = ['date', 'user__username', 'book__title']
    ordering = ['-date']

class AdminAuthorViewSet(viewsets.ModelViewSet):
    """
    Admin API for managing authors.
    """
    queryset = Author.objects.all()
    serializer_class = AdminAuthorSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']