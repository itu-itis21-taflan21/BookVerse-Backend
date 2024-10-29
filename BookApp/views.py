from rest_framework.views import APIView
from .models import Author
from rest_framework.response import Response
from .serializers import AuthorSerializer
from rest_framework import status
 
class AuthorView(APIView):
    def get(self,request,id):
        try:
            author = Author.objects.get(id=id)
            data = AuthorSerializer(author).data
            return Response({
                'data': data  
            }, status=status.HTTP_200_OK) 
        except:
            return Response({'error': 'Book not found'}, status=404)
        
        

