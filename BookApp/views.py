from rest_framework.views import APIView
from .models import Author,Category,Book,FavBook,UserComment,Rating,ReadList
from rest_framework.response import Response
from .serializers import AuthorSerializer,UserSerializer,CategorySerializer,BasicCommentSerializer,BasicUserSerializer,BookSerializer
from django.db.models import Count,Avg,Q
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound
import torch
from transformers import AutoTokenizer, AutoModel
from supabase import create_client
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

model = AutoModel.from_pretrained("avsolatorio/NoInstruct-small-Embedding-v0")
tokenizer = AutoTokenizer.from_pretrained("avsolatorio/NoInstruct-small-Embedding-v0")

url = "https://dujnhstimlhkodtayygi.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR1am5oc3RpbWxoa29kdGF5eWdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE4NDI1NDgsImV4cCI6MjA0NzQxODU0OH0.8JpiFgmTtzwl1RS6xrz3npVog1XhjgqqhXQX6rvBvmE"
client = create_client(url, key)

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

# Tested      
class CategoryView(APIView):
    def get(self,request):
        try:
            category_id = request.query_params.get("category_id")
            if category_id: 
                categories = Category.objects.filter(id=category_id).annotate(
                    book_count=Count('book_category')
                )
            else:
                categories = Category.objects.annotate(
                    book_count=Count('book_category')
                ).all()
            data = CategorySerializer(categories,many=True).data
            return Response({
                'data': data  
            }, status=status.HTTP_200_OK) 
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Categories not found'}, status=404)

#Tested
class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            new_password = request.data.get('new_password')
            user = request.user

            try:
                validate_password(new_password, user=user)
            except ValidationError as e:
                return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

            if user.check_password(new_password):
                return Response(
                    {"error": "New password must be different from the current password"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#Tested
class ProfileDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        try:
            user = request.user
            user.delete()
            return Response({"message": "User profile deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
#Tested     
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user_id=request.user.id
            
            user = User.objects.get(id=user_id)
            data = UserSerializer(user).data
            return Response({
                'data': data  
            }, status=status.HTTP_200_OK) 
        except:
            return Response({'error': 'User not found'}, status=404)

#Tested
class BookView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            book_id = request.query_params.get("book_id")
            author_id = request.query_params.get("author_id")
            category_id = request.query_params.get("category_id")
            keyword = request.query_params.get("s")
            limit = request.query_params.get("limit", 10)
            offset = request.query_params.get("offset", 0)

            if book_id:
                try:
                    book_id = int(book_id)
                except (ValueError, TypeError):
                    return Response({"error": "Invalid book_id format. It must be an integer."},
                                    status=status.HTTP_400_BAD_REQUEST)
                book = Book.objects.filter(id=book_id).first()
                if not book:
                    return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
                serializer = BookSerializer(book)
                return Response({"data": [serializer.data]}, status=status.HTTP_200_OK)

            try:
                limit = int(limit)
                if limit <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return Response({"error": "Limit must be a positive integer."},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                offset = int(offset)
                if offset < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return Response({"error": "Offset must be a non-negative integer."},
                                status=status.HTTP_400_BAD_REQUEST)

            books = Book.objects.all()

            if author_id:
                try:
                    author_id = int(author_id)
                except (ValueError, TypeError):
                    return Response({"error": "Invalid author_id format. It must be an integer."},
                                    status=status.HTTP_400_BAD_REQUEST)
                books = books.filter(author_id=author_id)
                if not books.exists():
                    return Response({"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND)

            if category_id:
                try:
                    category_id = int(category_id)
                except (ValueError, TypeError):
                    return Response({"error": "Invalid category_id format. It must be an integer."},
                                    status=status.HTTP_400_BAD_REQUEST)
                books = books.filter(category_id=category_id)
                if not books.exists():
                    return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

            if keyword:
                books = books.filter(Q(title__icontains=keyword) | Q(author__name__icontains=keyword))
                if not books.exists():
                    return Response({"error": "No books match the keyword."}, status=status.HTTP_404_NOT_FOUND)

            total_books = books.count()
            books = books.order_by('-id')[offset:offset + limit]
            serializer = BookSerializer(books, many=True)

            next_offset = offset + limit if (offset + limit) < total_books else None
            previous_offset = offset - limit if (offset - limit) >= 0 else None

            pagination = {
                "total": total_books,
                "limit": limit,
                "offset": offset,
                "next_offset": next_offset,
                "previous_offset": previous_offset
            }

            return Response({
                "data": serializer.data,
                "pagination": pagination
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class FavoriteView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user
        book_id = request.data.get('book_id') 
        if not book_id:
            return Response({"error": "Book ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(book_id, int):
            try:
                book_id = int(book_id)
            except (ValueError, TypeError):
                return Response({"error": "Invalid book_id format. It must be an integer."},
                                status=status.HTTP_400_BAD_REQUEST)
            
        book = get_object_or_404(Book, id=book_id)
        fav_entry = FavBook.objects.filter(user=user, book=book).first()
        if fav_entry:
            fav_entry.delete()
            return Response({"message": "Book removed from favorites successfully."}, status=status.HTTP_200_OK)
        else:
            FavBook.objects.create(user=user, book=book)
            return Response({"message": "Book added to favorites successfully."}, status=status.HTTP_201_CREATED)

    def get(self,request):
        user = request.user
        book_id = request.query_params.get("book_id")
        if not book_id:
            return Response({"error": "Book ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(book_id, int):
            try:
                book_id = int(book_id)
            except (ValueError, TypeError):
                return Response({"error": "Invalid book_id format. It must be an integer."},
                                status=status.HTTP_400_BAD_REQUEST)
        
        book = get_object_or_404(Book, id=book_id)
        is_favorite = FavBook.objects.filter(user=user, book=book).exists()
        return Response({'data': is_favorite}, status=status.HTTP_200_OK)
        
#Tested
class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        book_id=request.query_params.get('book_id')
        if not book_id:
            return Response({"error": "book_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(book_id, int):
            try:
                book_id = int(book_id)
            except (ValueError, TypeError):
                return Response({"error": "Invalid book_id format. It must be an integer."},
                                status=status.HTTP_400_BAD_REQUEST)
        book = get_object_or_404(Book, id=book_id)
        comments = UserComment.objects.filter(book=book)
        returndata = BasicCommentSerializer(comments, many=True).data

        if comments.exists():
            return Response({'data': returndata}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No comments found for the book.'}, status=status.HTTP_404_NOT_FOUND)
        
        
    def post(self,request):
        user = request.user
        book_id = request.data.get('book_id')
        content = request.data.get('content')
        if not book_id:
            return Response({"error": "book_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(book_id, int):
            try:
                book_id = int(book_id)
            except (ValueError, TypeError):
                return Response({"error": "Invalid book_id format. It must be an integer."},
                                status=status.HTTP_400_BAD_REQUEST)
        
        if not content:
            return Response({"error": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)
    
        book = get_object_or_404(Book, id=book_id)
        UserComment.objects.create(user=user, book=book, content=content)
        return Response({"message": "Comment added successfully."}, status=status.HTTP_201_CREATED)
        
        
class RatingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user=request.user

        book_id=request.query_params.get('book_id')
        if not book_id:
            return Response({"error": "book_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(book_id, int):
            try:
                book_id = int(book_id)
            except (ValueError, TypeError):
                return Response({"error": "Invalid book_id format. It must be an integer."},
                                status=status.HTTP_400_BAD_REQUEST)
    
        book = get_object_or_404(Book, id=book_id)
    
        try:
            user_rating = Rating.objects.get(book=book, user=user)
            return Response({'user_rating': user_rating.rating}, status=status.HTTP_200_OK)
        except Rating.DoesNotExist:
            return Response({'error': 'No ratings for user found for the book.'}, status=status.HTTP_404_NOT_FOUND)
    
    
    def post(self, request):
        user = request.user
        book_id = request.data.get('book_id')
        rating_value = request.data.get('rating')

        if not book_id:
            return Response({'error': 'book_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
        # Validate book_id is an integer
        if not isinstance(book_id, int):
            try:
                book_id = int(book_id)
            except (ValueError, TypeError):
                return Response({'error': 'Invalid book_id format. It must be an integer.'},
                                status=status.HTTP_400_BAD_REQUEST)
    
        book = get_object_or_404(Book, id=book_id)
        if rating_value is None:
            return Response({'error': 'rating is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            rating_value = int(rating_value)
        except (ValueError, TypeError):
            return Response({'error': 'Rating must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
    
        if rating_value < 0 or rating_value > 5:
            return Response({'error': 'Rating must be between 0 and 5.'}, status=status.HTTP_400_BAD_REQUEST)
    
        if Rating.objects.filter(user=user, book=book).exists():
            return Response({'error': 'You have already rated this book. Use PUT to update your rating.'},
                            status=status.HTTP_400_BAD_REQUEST)
    
        Rating.objects.create(user=user, book=book, rating=rating_value)
        return Response({'message': 'Rating added successfully.'}, status=status.HTTP_201_CREATED)

    def put(self, request):
        user = request.user
        book_id = request.data.get('book_id')
        new_rating = request.data.get('rating')

        if not book_id:
            return Response({'error': 'book_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(book_id, int):
            try:
                book_id = int(book_id)
            except (ValueError, TypeError):
                return Response({'error': 'Invalid book_id format. It must be an integer.'},
                                status=status.HTTP_400_BAD_REQUEST)
    
        book = get_object_or_404(Book, id=book_id)
    
        if new_rating is None:
            return Response({'error': 'rating is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            new_rating = int(new_rating)
        except (ValueError, TypeError):
            return Response({'error': 'Rating must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
    
        if new_rating < 0 or new_rating > 5:
            return Response({'error': 'Rating must be between 0 and 5.'}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            rating_instance = Rating.objects.get(user=user, book=book)
            rating_instance.rating = new_rating
            rating_instance.save()
            return Response({'message': 'Rating updated successfully.'}, status=status.HTTP_200_OK)
        except Rating.DoesNotExist:
            return Response({'error': 'Rating not found for this book by the user.'}, status=status.HTTP_404_NOT_FOUND)
            
class ReadListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        book_id = request.data.get('book_id')

        if not book_id:
            return Response({"error": "Book ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book_id = int(book_id)
        except ValueError:
            return Response({"error": "Invalid book ID format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        read_entry = ReadList.objects.filter(user=user, book=book).first()
        if read_entry:
            read_entry.delete()
            return Response({"message": "Book removed from readlist successfully"}, status=status.HTTP_200_OK)
        else:
            ReadList.objects.create(user=user, book=book)
            return Response({"message": "Book added to readlist successfully"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        user = request.user
        book_id = request.query_params.get('book_id')

        if not book_id:
            return Response({"error": "Book ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            book_id = int(book_id)
        except ValueError:
            return Response({"error": "Invalid book ID format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        is_in_readlist = ReadList.objects.filter(user=user, book=book).exists()
        return Response({'data': is_in_readlist}, status=status.HTTP_200_OK)

        

def get_embedding(sentences, model, tokenizer):
    inputs = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings


class SemanticSearchView(APIView):
    def post(self, request):
        try:
            query = request.data.get("key", "").strip()
            if not query:
                return Response(
                    {"status": "error", "message": "Query key is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                match_threshold = float(request.data.get("match_threshold", 0.7))
            except ValueError:
                return Response(
                    {"status": "error", "message": "Invalid match_threshold value."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                match_count = int(request.data.get("match_count", 10))
            except ValueError:
                return Response(
                    {"status": "error", "message": "Invalid match_count value."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            embedding = get_embedding(query, model, tokenizer).tolist()[0]
            response = client.rpc(
                "semantic_search",
                {
                    "query_embedding": embedding,
                    "match_threshold": match_threshold,
                    "match_count": match_count,
                },
            ).execute()

            if response.data:
                return Response(
                    {"status": "success", "recommendations": response.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": "error", "message": "No results found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RecommendBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_id = request.user.id
            if not user_id:
                return Response(
                    {"status": "error", "message": "User ID is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                top_n = int(request.data.get("top_n", 10))
            except ValueError:
                return Response(
                    {"status": "error", "message": "Invalid top_n value."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                similarity_threshold = float(
                    request.data.get("similarity_threshold", 0.8)
                )
            except ValueError:
                return Response(
                    {"status": "error", "message": "Invalid similarity_threshold value."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = client.rpc(
                "recommend_books",
                {
                    "get_user_id": user_id,
                    "top_n": top_n,
                    "similarity_threshold": similarity_threshold,
                },
            ).execute()

            if response.data:
                return Response(
                    {"status": "success", "recommendations": response.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": "error", "message": "No recommendations found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
