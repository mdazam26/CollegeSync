from django.shortcuts import render , redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from super.models import College
from .models import Batch, Branch, HOD
from datetime import datetime

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

def view_hod(request):
    return render(request, 'director/view_hod.html')

# View for creating Batch
def create_batch_form(request):
    # Logic for creating batch
    return render(request, 'director/create_batch_form.html')

def create_batch(request):
    if 'director_id' not in request.session:
        return redirect('open_login')

    if request.method == "POST":
        batch_name = request.POST.get('batch_name')

        if batch_name:
            try:
                batch_year = int(batch_name)
                current_year = datetime.now().year
                min_year = current_year - 50

                if min_year <= batch_year <= current_year:
                    if not Batch.objects.filter(batch_name=batch_year).exists():
                        Batch.objects.create(batch_name=batch_year)
                        messages.success(request, "Batch created successfully.")
                    else:
                        messages.error(request, "Batch with this year already exists.")
                else:
                    messages.error(request, f"Batch year must be between {min_year} and {current_year}.")
            except ValueError:
                messages.error(request, "Invalid batch year. Please enter a valid number.")
        else:
            messages.error(request, "Please enter a batch year.")

    return redirect('create_batch_form')

def view_batch(request):
    batches = Batch.objects.all().order_by('-batch_name')  # Optional ordering
    return render(request, 'director/view_batch.html', {'batches': batches})

# View for managing Batches
def goto_manage_batch(request,batch_id):
    try:
        batch = Batch.objects.get(id=batch_id)
        branches = Branch.objects.filter(batch=batch)
        return render(request, 'director/goto_manage_batch.html', {
            'batch': batch,
            'branches': branches
        })
    except Batch.DoesNotExist:
        messages.error(request, "Batch not found.")
        return redirect('view_batch')

def manage_batch(request, batch_id):
    try:
        batch = Batch.objects.get(id=batch_id)
    except Batch.DoesNotExist:
        messages.error(request, "Batch not found.")
        return redirect('view_batch')  # Redirect to the batch view page if batch does not exist.

    branches = batch.branches.all()  # Get all branches associated with this batch.

    current_year = datetime.now().year  # Get the current year (e.g., 2025).
    min_year = current_year - 50  # The minimum valid batch year (e.g., 1975).
    
    if request.method == "POST":
        batch_name = request.POST.get("batch_name")
        
        # Validate the batch year: Ensure it is within the range of current_year and min_year
        try:
            batch_year = int(batch_name)
            if not (min_year <= batch_year <= current_year):
                messages.error(request, f"Batch year must be between {min_year} and {current_year}.")
                return render(request, 'director/goto_manage_batch.html', {'batch': batch, 'branches': branches})
        except ValueError:
            messages.error(request, "Invalid year. Please enter a valid number.")
            return render(request, 'director/goto_manage_batch.html', {'batch': batch, 'branches': branches})
        
        # Check if the new batch name already exists (excluding the current batch)
        if Batch.objects.exclude(id=batch.id).filter(batch_name=batch_name).exists():
            messages.error(request, "Batch name already exists. Please choose a different name.")
            return render(request, 'director/goto_manage_batch.html', {'batch': batch, 'branches': branches})

        # If unique, update the batch name
        batch.batch_name = batch_name
        batch.save()

        # Add a success message and redirect to the view_batch page
        messages.success(request, "Batch successfully updated!")
        return redirect('view_batch')  # Redirect to the view_batch page after updating the batch.

    return render(request, 'director/goto_manage_batch.html', {'batch': batch, 'branches': branches})

def delete_batch(request, batch_id):
    try:
        batch = Batch.objects.get(id=batch_id)
        batch.delete()
        # Add a success message for deletion
        messages.success(request, "Batch successfully deleted.")
    except Batch.DoesNotExist:
        messages.error(request, "Batch not found.")

    return redirect('view_batch')  # Redirect to the view_batch page after deletion.

# View for assigning Branch
def create_branch(request):
    # Logic for assigning branch to HOD
    return render(request, 'director/create_branch.html')

def view_branch(request):
    return render(request, 'director/view_branch.html')

# View for managing Branches
def goto_manage_branch(request):
    # Logic for managing branches
    return render(request, 'director/goto_manage_branch.html')


def director_logout(request):
    logout(request)
    return redirect('open_login')