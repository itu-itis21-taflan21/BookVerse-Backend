from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import AdminUserSerializer,AdminAuthorSerializer,AdminCategorySerializer,AdminUserCommentSerializer
from BookApp.models import Book,Author,Category,UserComment
from .serializers import AdminBookSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from supabase import create_client, Client
import uuid
import torch
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModel
from rest_framework import status
from rest_framework.response import Response
from BookVerse.settings import supabase

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
    parser_classes = [MultiPartParser, FormParser]  # Support file uploads

    def create(self, request, *args, **kwargs):
        # Handle file upload
        cover_image = request.FILES.get('cover')  # Get the uploaded file
        title = request.POST.get('title')
        summary = request.POST.get('summary')
        author_id = request.POST.get('author')
        category_id = request.POST.get('category')
        author=Author.objects.get(id=author_id).name
        category=Category.objects.get(id=category_id).name
        if not cover_image:
            return Response({"error": "Cover image is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a unique filename and upload to Supabase
        bucket_name = "images"
        file_name = f"{uuid.uuid4()}-{cover_image.name}"  # Create unique filename
        
        file_content = cover_image.read()
        response = supabase.storage.from_(bucket_name).upload(file_name, file_content)
        
        response2 = supabase.storage.from_(bucket_name).create_signed_url(file_name, 31556926)
        public_url=response2["signedURL"]

        # Add the public_url to the request data for serialization
        data = request.data.copy()
        data['cover'] = public_url
        model = AutoModel.from_pretrained("avsolatorio/NoInstruct-small-Embedding-v0")
        tokenizer = AutoTokenizer.from_pretrained("avsolatorio/NoInstruct-small-Embedding-v0")


        book_info = title + " " + summary + " " + author + category
        



        inputs = tokenizer(book_info, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)

        embeddings_list = embeddings.squeeze().tolist()
        data['embedding'] = embeddings_list
        # Serialize and save the data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
 
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