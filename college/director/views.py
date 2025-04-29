from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
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
    if 'director_id' not in request.session:
        return redirect('open_login')
    
    director_id = request.session['director_id']

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_login')  # If director is not found, redirect to login
    return render(request, 'director/director_dashboard.html', {'director' : director})

def director_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            director = College.objects.get(admin_username=username)
        except College.DoesNotExist:
            messages.error(request, "Username not found")
            return render(request, 'director/login.html')

        # If username exists, check password
        if check_password(password, director.admin_password):
            request.session['director_id'] = director.id
            return redirect('director_dashboard')
        else:
            messages.error(request, "Invalid password")
            return render(request, 'director/login.html')

    return render(request, 'director/login.html')


def create_hod(request):
    # Logic for creating HOD
    return render(request, 'director/create_hod.html')

# View for managing HODs
def manage_hod(request):
    # Logic for managing HODs
    return render(request, 'director/manage_hod.html')

# View for creating Batch
def create_batch(request):
    # Logic for creating batch
    return render(request, 'director/create_batch.html')

# View for managing Batches
def manage_batch(request):
    # Logic for managing batches
    return render(request, 'director/manage_batch.html')

# View for assigning Branch
def create_branch(request):
    # Logic for assigning branch to HOD
    return render(request, 'director/create_branch.html')

# View for managing Branches
def manage_branch(request):
    # Logic for managing branches
    return render(request, 'director/manage_branch.html')


def director_logout(request):
    logout(request)
    return redirect('open_login')