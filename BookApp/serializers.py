from .models import Author,Book,FavBook,Rating,UserComment,ReadList,Category
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Avg

class BookforAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title','cover','page_count']

class AuthorSerializer(serializers.ModelSerializer):
    book_books = BookforAuthorSerializer(many=True, read_only=True)
    book_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    fav_book_count = serializers.IntegerField(read_only=True)
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
        fields = ['id','username','email','is_superuser','date_joined','fav_user','read_user','comment_user','rating_user']


class CategorySerializer(serializers.ModelSerializer):
    book_count = serializers.IntegerField(read_only=True) 
    class Meta:
        model = Category
        fields = ['id', 'name','book_count'] 
        
class BasicAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Author
        fields=['id','name']
        
class BookSerializer(serializers.ModelSerializer):
    author=BasicAuthorSerializer(many=False,read_only=True)
    category=CategorySerializer(many=False,read_only=True)
    average_rating=serializers.SerializerMethodField()
    class Meta:
        model=Book
        fields=['id','title','cover','author','summary','category','page_count','average_rating']
    
    def get_average_rating(self, obj):
        average_rating = Rating.objects.filter(book=obj).aggregate(Avg('rating'))['rating__avg']
        return average_rating if average_rating is not None else 0 

class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username']

class BasicCommentSerializer(serializers.ModelSerializer):
    user=BasicUserSerializer(many=False,read_only=True)
    class Meta:
        model=UserComment
        fields=['id','content','book_id','user_id','user']


