from django.shortcuts import render, redirect
from django.http import HttpResponse


def start(request):
    return HttpResponse("This is in building phase")

