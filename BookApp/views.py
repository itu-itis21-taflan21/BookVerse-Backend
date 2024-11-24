from rest_framework.views import APIView
from .models import Author,Category,Book
from rest_framework.response import Response
from .serializers import AuthorSerializer,UserSerializer,CategorySerializer,BookSerializer
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated


class AuthorView(APIView):
    def get(self,request,id):
        try:
            author = Author.objects.get(id=id)
            print(author)
            data = AuthorSerializer(author).data
            return Response({
                'data': data  
            }, status=status.HTTP_200_OK) 
        except:
            return Response({'error': 'Author not found'}, status=404)

        
class CategoryView(APIView):
    def get(self,request):
        try:
            catgories = Category.objects.get()
            data = CategorySerializer(catgories).data
            return Response({
                'data': data  
            }, status=status.HTTP_200_OK) 
        except:
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
    def get(self,request):
        book_id=request.query_params.get("book_id")
        category=request.query_params.get("category")
        author=request.query_params.get("author")
        keyword=request.query_params.get("keyword")

        books = Book.objects.all()
        if book_id:
             books = books.get(id=book_id)
         
        if author:
             books = books.get(author_id=author)
         
        if category:
             books = books.get(category_id=category)
         
        if keyword:
            books = books.get(title=keyword)
        print(books)
         #Check if any books match the filters
        if books:
            # Serialize the matching books
            books_data = BookSerializer(books).data
            return Response({'data': books_data}, status=status.HTTP_200_OK)
        else:
            # No books found
            return Response({'error': 'No books found matching the criteria.'}, status=status.HTTP_404_NOT_FOUND)
        
        
            