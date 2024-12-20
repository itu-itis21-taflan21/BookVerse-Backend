from rest_framework.views import APIView
from .models import Author,Category,Book,FavBook,UserComment,Rating
from rest_framework.response import Response
from .serializers import AuthorSerializer,UserSerializer,CategorySerializer,BookSerializer
from django.db.models import Count,Avg,Q
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound


class AuthorView(APIView):
    def get(self, request):
        
        id=request.query_params.get("id")
        limit=int(request.query_params.get("limit",5))  
        try:
            if id: 
                authors = Author.objects.annotate(
                    book_count=Count('book_books'),
                    average_rating=Avg('book_books__rating_books__rating'),
                    fav_book_count=Count(
                        'book_books__fav_books',
                        distinct=True
                    )
                ).filter(id=id) 
                if not authors.exists():
                    raise NotFound("Author not found")
            else:
                authors = Author.objects.annotate(
                    book_count=Count('book_books'),
                    average_rating=Avg('book_books__rating_books__rating'),
                    fav_book_count=Count(
                        'book_books__fav_books',
                        distinct=True
                    )
                ).order_by('-fav_book_count','name').all()
            authors=authors[:limit]
            data = AuthorSerializer(authors, many=True).data
            return Response({
                'data': data  
            }, status=status.HTTP_200_OK)
        except NotFound:
            return Response({'error': 'Author not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

        
class CategoryView(APIView):
    def get(self,request):
        try:
            categories = Category.objects.annotate(
                book_count = Count('book_category')
            ).all()
            data = CategorySerializer(categories,many=True).data
            return Response({
                'data': data  
            }, status=status.HTTP_200_OK) 
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Categories not found'}, status=404)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:      
            new_password = request.data.get('new_password')
            user = request.user
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class ProfileDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        try:
            user = request.user
            user.delete()
            return Response({"message": "User profile deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
        
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id):
        try:

            if request.user.id != id and not request.user.is_staff:
                return Response({'error': 'You are not allowed to access this user\'s data'}, status=status.HTTP_403_FORBIDDEN)
            user = User.objects.get(id=id)
            data = UserSerializer(user).data
            return Response({
                'data': data  
            }, status=status.HTTP_200_OK) 
        except:
            return Response({'error': 'User not found'}, status=404)


class BookView(APIView):
    def get(self, request):

        book_id = request.query_params.get("book_id")
        category = request.query_params.get("category_id")
        author = request.query_params.get("author_id")
        keyword = request.query_params.get("s")
        limit = int(request.query_params.get("limit", 10)) 


        books = Book.objects.all()
        if book_id:
            books = books.filter(id=book_id)
        if author:
            books = books.filter(author_id=author)
        if category:
            books = books.filter(category_id=category)
        if keyword:
            books = books.filter(Q(title__icontains=keyword) | Q(author__name__icontains=keyword))

        if not any([book_id, author, category, keyword]):
            books = books.annotate(favorite_count=Count('fav_books')).order_by('-favorite_count', 'title')

        books = books[:limit]
        if books.exists():
            books_data = BookSerializer(books, many=True).data
            return Response({'data': books_data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No books found matching the criteria.'}, status=status.HTTP_404_NOT_FOUND)
        
        
class AddBookToFav(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user
        book_id = request.data.get('book_id') 
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        if FavBook.objects.filter(user=user, book=book).exists():
            return Response({"error": "This book is already in your favorites"}, status=status.HTTP_400_BAD_REQUEST)

        FavBook.objects.create(user=user, book=book)
        return Response({"message": "Book added to favorites successfully"}, status=status.HTTP_201_CREATED)

class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user
        book_id = request.data.get('book_id')
        content = request.data.get('content')
        if not content:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        UserComment.objects.create(user=user, book=book, content=content)
        return Response({"message": "Comment added successfully"}, status=status.HTTP_201_CREATED)
        
class AddRatingToBook(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        book_id = request.data.get('book_id')
        rating = request.data.get('rating')

        if rating is None:
            return Response({"error": "Rating is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not (0 <= int(rating) <= 5):
            return Response({"error": "Rating must be between 0 and 5"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        existing_rating = Rating.objects.filter(user=user, book=book).first()
        if existing_rating:
            existing_rating.rating = rating
            existing_rating.save()
            return Response({"message": "Rating updated successfully"}, status=status.HTTP_200_OK)

        Rating.objects.create(user=user, book=book, rating=rating)

        return Response({"message": "Rating added successfully"}, status=status.HTTP_201_CREATED)