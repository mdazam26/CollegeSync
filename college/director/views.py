from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from super.models import College

# Create your views here.
def index(request):
    return render(request, 'director/index.html')


def open_login(request):
    return render(request, 'director/login.html')


def director_dashboard(request):
    return render(request, 'director/dashboard.html')

def director_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            director = College.objects.get(admin_username = username)
            if check_password(password, director.admin_password):
                request.session['director_id'] = director.id
                return redirect('director_dashboard')
            else:
                messages.error(request, "invalid password.")
        except College.DoesNotExist:
            messages.error(request, "Username not found")

    return render(request, 'director/login.html')