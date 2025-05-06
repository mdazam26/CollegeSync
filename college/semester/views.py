from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import path, include


# Create your views here.
def index(request):
    return render(request, 'semester/index.html')