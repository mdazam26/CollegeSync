from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import path, include
from django.contrib import messages
from super.models import College

# Create your views here.
def index(request):
    director_id = request.session['director_id']
    try:
        director = College.objects.get(id = director_id)
    except College.DoesNotExist:
        messages.error(request,'director not found')
        return redirect('open_director_login')
    
    return render(request, 'semester/index.html', {'director' : director})