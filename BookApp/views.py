from rest_framework.views import APIView
from .models import Author,Category
from rest_framework.response import Response
from django.db.models import Count
from .serializers import AuthorSerializer,UserSerializer,CategorySerializer
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
    def get(self,request,id):
        try:
            if str(request.user.id) != str(id):
                return Response({'error': 'You cannot view other users\' profiles.'}, status=status.HTTP_403_FORBIDDEN)
            
            user = User.objects.get(id=id)
            data = UserSerializer(user).data
            return Response({
                'data': data  
            }, status=status.HTTP_200_OK) 
        except:
            return Response({'error': 'User not found'}, status=404)

