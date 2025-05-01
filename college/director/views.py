from django.shortcuts import render , redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django_tenants.utils import schema_context
from django.db import connection
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

        if not username or not password:
            messages.error(request, "Please enter both username and password")
            return render(request, 'director/login.html')

        # ✅ Query the College model from public schema
        with schema_context('public'):
            try:
                director = College.objects.get(admin_username=username)
            except College.DoesNotExist:
                messages.error(request, "Username not found")
                return render(request, 'director/login.html')

        # ❌ Prevent cross-tenant login
        from django.db import connection
        if director.schema_name != connection.schema_name:
            messages.error(request, "Access denied: cross-tenant login not allowed.")
            return render(request, 'director/login.html')

        from django.utils import timezone
        from django.contrib.auth.hashers import check_password

        if check_password(password, director.admin_password):
            if director.on_trial:
                if director.paid_until and timezone.now().date() > director.paid_until:
                    messages.error(request, "Your trial period has expired.")
                    return render(request, 'director/login.html')

            request.session['director_id'] = director.id
            return redirect('director_dashboard')
        else:
            messages.error(request, "Invalid password")
            return render(request, 'director/login.html')



    return render(request, 'director/login.html')

def create_hod_form(request):
    return render(request, 'director/create_hod_form.html')

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
    director_id = request.session['director_id']
    try:
        director = College.objects.get(id = director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found")
        return redirect('director_dashboard')
    
    # Logic for creating batch
    return render(request, 'director/create_batch_form.html', {'director': director})

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
    director_id = request.session['director_id']
    try:
        director = College.objects.get(id = director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found")
    return render(request, 'director/view_batch.html', {'batches': batches, 'director': director})

# View for managing Batches
def goto_manage_batch(request,batch_id):
    director_id = request.session['director_id']
    try:
        batch = Batch.objects.get(id=batch_id)
        branches = Branch.objects.filter(batch=batch)
        director = College.objects.get(id = director_id)
        return render(request, 'director/goto_manage_batch.html', {
            'batch': batch,
            'branches': branches,
            'director': director
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

# batch end 

# branch start

# View for assigning Branch
def create_branch_form(request):
    director_id = request.session.get('director_id')  # Use get to avoid KeyError if 'director_id' doesn't exist
    if not director_id:
        messages.error(request, "Director not found. Please log in again.")
        return redirect('open_login')  # Redirect to login if no director_id in session

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_login')

    # Fetch all batches for the director (assuming you want to show batches related to this director)
    batches = Batch.objects.all()  # Modify this query if batches are specific to the director

    # Fetch all branches (or modify as needed if you want only active branches)
    branches = Branch.objects.all()  # Adjust query if necessary

    return render(request, 'director/create_branch_form.html', {
        'director': director,
        'batches': batches,
        'branches': branches
    })

def create_branch(request):
    if request.method == 'POST':
        # Get the form data
        branch_name = request.POST.get('branch_name')
        batch_id = request.POST.get('batch')  # Optional, may be empty
        hod_id = request.POST.get('hod')  # Optional, may be empty
        
        # Validate that branch name is provided
        if not branch_name:
            messages.error(request, "Branch name is required.")
            return redirect('create_branch_form')  # Redirect back to the form with error message

        # Validate that a batch is selected
        if not batch_id:
            messages.error(request, "Batch is required. Please create a batch first.")
            return redirect('create_batch_form')  # Redirect to the create batch form if no batch is selected

        # Check if the branch already exists in the selected batch
        try:
            batch = Batch.objects.get(id=batch_id)
        except Batch.DoesNotExist:
            messages.error(request, "Selected batch does not exist.")
            return redirect('create_branch_form')  # Redirect back if batch is not valid

        if Branch.objects.filter(batch=batch, branch_name=branch_name).exists():
            messages.error(request, f"Branch '{branch_name}' already exists in the {batch.batch_name} batch.")
            return redirect('create_branch_form')  # Redirect back to the form if branch already exists

        # Create the Branch object
        branch = Branch(branch_name=branch_name, batch=batch)

        # If an HOD is selected, set it (optional)
        if hod_id:
            try:
                hod = HOD.objects.get(id=hod_id)
                branch.hod = hod
            except HOD.DoesNotExist:
                messages.error(request, "Selected HOD does not exist.")
                return redirect('create_branch_form')  # Redirect back if HOD is not valid

        # Save the Branch object
        branch.save()

        # Success message
        messages.success(request, "Branch created successfully!")

        # Redirect to the 'view_branch' page after successfully creating the branch
        return redirect('view_branch')  # Redirect to view branch after creation

    # If the request method is not POST, show the branch creation form
    return redirect('create_branch_form')


def view_branch(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Director not found. Please log in again.")
        return redirect('open_login')

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_login')

    try:
        branches = Branch.objects.select_related('batch', 'hod').order_by('branch_name')
    except Exception as e:
        messages.error(request, f"Error fetching branches: {str(e)}")
        branches = []

    try:
        batches = Batch.objects.all().order_by('-batch_name')
    except Exception as e:
        messages.error(request, f"Error fetching batches: {str(e)}")
        batches = []

    return render(request, 'director/view_branch.html', {
        'branches': branches,
        'batches': batches,
        'director': director
    })

# View for managing Branches
def goto_manage_branch(request, branch_id):
    # Logic for managing branches
    director_id = request.session.get('director_id')
    
    if not director_id:
        messages.error(request, "Director not found. Please log in again.")
        return redirect('open_login')  # Redirect to login if no director_id in session
    
    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_login')

    # Fetch the branch by ID, or return 404 if not found
    branch = get_object_or_404(Branch, id=branch_id)

    # Accessing the associated batch and HOD for the branch
    # batch = Batch.objects.all()
    # hod = HOD.objects.all()

    batches = Batch.objects.all().order_by('-batch_name')
    hods = HOD.objects.all().order_by('hod_name')

    return render(request, 'director/goto_manage_branch.html', {
        'branch': branch,
        'director': director,
        'batches': batches,  # <-- changed from 'batch'
        'hods': hods, 
    })

def manage_branch(request, branch_id):
     # Fetch the branch to manage
    branch = get_object_or_404(Branch, id=branch_id)
    batches = Batch.objects.all().order_by('-batch_name')  # Available batches
    hods = HOD.objects.all().order_by('hod_name')  # Available HODs

    if request.method == 'POST':
        # Get the form data
        branch_name = request.POST.get('branch_name')
        batch_id = request.POST.get('batch')
        hod_id = request.POST.get('hod')

        # Validate branch name
        if not branch_name:
            messages.error(request, "Branch name is required.")
            return render(request, 'director/manage_branch.html', {
                'branch': branch,
                'batches': batches,
                'hods': hods,
            })

        # Check if the branch already exists in the selected batch
        if batch_id:
            # Get the batch object
            batch = Batch.objects.get(id=batch_id)
            if Branch.objects.filter(batch=batch, branch_name=branch_name).exclude(id=branch.id).exists():
                messages.error(request, f"Branch '{branch_name}' already exists in the {batch.batch_name} batch.")
                return render(request, 'director/manage_branch.html', {
                    'branch': branch,
                    'batches': batches,
                    'hods': hods,
                })

        # Update branch details
        branch.branch_name = branch_name

        if batch_id:
            batch = Batch.objects.get(id=batch_id)
            branch.batch = batch

        if hod_id:
            hod = HOD.objects.get(id=hod_id)
            branch.hod = hod

        # Save updated branch
        branch.save()

        messages.success(request, "Branch updated successfully!")
        return redirect('view_branch')  # Redirect to the view_branch page after successful update

    return render(request, 'director/manage_branch.html', {
        'branch': branch,
        'batches': batches,
        'hods': hods,
    })

def delete_branch(request, branch_id):
    try:
        branch = get_object_or_404(Branch, id=branch_id)
        branch.delete()
        messages.success(request, "Branch deleted successfully.")
    except Branch.DoesNotExist:
        messages.error(request, "Branch not found.")

    return redirect('view_branch')



def director_logout(request):
    logout(request)
    return redirect('open_login')