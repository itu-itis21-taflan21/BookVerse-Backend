from rest_framework import serializers
from django.contrib.auth.models import User
from BookApp.models import Author, Category, Book, UserComment, Rating, FavBook, ReadList

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_staff', 'is_superuser']

class AdminBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class AdminAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class AdminUserCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    book = serializers.StringRelatedField()

    class Meta:
        model = UserComment
        fields = ['id', 'content', 'date', 'user', 'book']