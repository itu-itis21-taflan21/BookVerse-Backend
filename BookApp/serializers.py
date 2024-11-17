
from .models import Author,Book,FavBook,Rating,UserComment,ReadList

from rest_framework import serializers
from django.contrib.auth.models import User

class BookforAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title','cover','page_count']

class AuthorSerializer(serializers.ModelSerializer):
    book_books = BookforAuthorSerializer(many=True, read_only=True)
    class Meta:
        model = Author

        fields = ['id', 'name','book_count','fav_book_count','average_rating','book_books'] 
    
class CommentsforUser(serializers.ModelSerializer):
    class Meta:
        model=UserComment
        fields=['id','content']

class RatingforUser(serializers.ModelSerializer):
    class Meta:
        model=Rating
        fields=['id','rating']
        
class FavBookSerializer(serializers.ModelSerializer):
    book = BookforAuthorSerializer(read_only=True)

    class Meta:
        model = FavBook
        fields = ['id', 'book']

class ReadBooksSerializer(serializers.ModelSerializer):
    book =BookforAuthorSerializer(read_only=True)
    class Meta:
        model = ReadList
        fields=['id','book']
        
class UserSerializer(serializers.ModelSerializer):
    comment_user=CommentsforUser(many=True,read_only=True)
    fav_user=FavBookSerializer(many=True, read_only=True)
    read_user=ReadBooksSerializer(many=True, read_only=True)
    rating_user=RatingforUser(many=True,read_only=True)
    class Meta:
        model=User
        fields = ['id','username','email','date_joined','fav_user','read_user','comment_user','rating_user']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name','book_count'] 


