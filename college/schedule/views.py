from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import path, include
from super.models import College
from django.contrib import messages


# Create your views here.
def index(request):
    director_id = request.session['director_id']
    try:
        director = College.objects.get(id = director_id)
    except College.DoesNotExist:
        messages.error(request,'director not found')
        return redirect('open_director_login')
    
    return render(request, 'schedule/index.html')