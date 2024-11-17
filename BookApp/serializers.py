from .models import Author,Book,Category
from rest_framework import serializers

class BookforAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title','cover','page_count']

class AuthorSerializer(serializers.ModelSerializer):
    books = BookforAuthorSerializer(many=True, read_only=True)
    class Meta:
        model = Author
        fields = ['id', 'name','book_count','fav_book_count','average_rating','books']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name','book_count'] 

