from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User

def hello_world(request):
    jsondata={'name':'musti'}
    return JsonResponse(jsondata)



    
    
    

