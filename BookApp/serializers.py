from .models import Author,Book
from rest_framework import serializers

class BookforAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title','cover','page_count'] 


class AuthorSerializer(serializers.ModelSerializer):
    books = BookforAuthorSerializer(many=True, read_only=True)
    class Meta:
        model = Author
        fields = ['id', 'name','book_count','favorite_book_count','average_rating','books'] 