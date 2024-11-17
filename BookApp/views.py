from rest_framework.views import APIView
from .models import Author
from rest_framework.response import Response
from .serializers import AuthorSerializer,UserSerializer
from rest_framework import status
from django.contrib.auth.models import User
 
class AuthorView(APIView):
    def get(self,request,id):
        try:
            author = Author.objects.get(id=id)
            data = AuthorSerializer(author).data
            return Response({
                'data': data  
            }, status=status.HTTP_200_OK) 
        except:
            return Response({'error': 'Author not found'}, status=404)
        
class ProfileView(APIView):
    def get(self,request,id):
        try:
            user = User.objects.get(id=id)
            data = UserSerializer(user).data
            return Response({
                'data': data  
            }, status=status.HTTP_200_OK) 
        except:
            return Response({'error': 'User not found'}, status=404)

