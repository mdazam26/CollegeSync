from django.shortcuts import render , redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password , make_password
from django.utils import timezone
from django_tenants.utils import schema_context
from django.db import connection
from django.db.models import ProtectedError
from super.models import College
from .models import Batch, Branch, Teacher, ClassGroup
from datetime import datetime

# Create your views here.
def index(request):
    return render(request, 'director/index.html')


def open_director_login(request):
    return render(request, 'director/login.html')

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

def director_dashboard(request):
    if 'director_id' not in request.session:
        return redirect('open_login')
    
    director_id = request.session['director_id']

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_director_login')  # If director is not found, redirect to login
    return render(request, 'director/director_dashboard.html', {'director' : director})

def director_logout(request):
    logout(request)
    return redirect('open_director_login')




# teacher start

def create_teacher_form(request):
    director_id = request.session['director_id']
    try:
        director = College.objects.get(id = director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found")
        return redirect('open_director_login')
    return render(request, 'director/create_teacher_form.html' , {'director' : director})

def create_teacher(request):
    if request.method == 'POST':
        teacher_name = request.POST.get('teacher_name').strip()
        teacher_username = request.POST.get('teacher_username').strip()
        teacher_password = request.POST.get('teacher_password').strip()
        teacher_email = request.POST.get('teacher_email').strip()
        teacher_phone = request.POST.get('teacher_phone').strip()
        is_hod = request.POST.get('is_hod', '').lower() == 'true'

        # Basic validation for required fields
        if not teacher_name or not teacher_username or not teacher_password:
            messages.error(request, "Name, Username, and Password are required fields.")
            return redirect('create_teacher_form')

        # Check if the teacher username already exists
        if Teacher.objects.filter(teacher_username=teacher_username).exists():
            messages.error(request, "Username already taken. Please choose a different username.")
            return redirect('create_teacher_form')

        # Optionally, check if the email is unique
        if teacher_email and Teacher.objects.filter(teacher_email=teacher_email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('create_teacher_form')

        # Hash the password before saving
        hashed_password = make_password(teacher_password)

        # Create Teacher object
        teacher = Teacher(
            teacher_name=teacher_name,
            teacher_username=teacher_username,
            teacher_password=hashed_password,
            teacher_email=teacher_email,
            teacher_phone=teacher_phone,
            is_hod=is_hod,
        )
        try:
            teacher.save()
        except Exception as e:
            messages.error(request, f"An error occured while creating the teacher: {e}")
            return redirect('create_teacher_form')
        messages.success(request, "Teacher created successfully!")
        return redirect('view_teacher')  # Redirect to the view teachers page or another page as needed

    else:
        return redirect('create_teacher_form')

def view_teacher(request):
    director_id = request.session.get('director_id')
    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found")
        return redirect('open_director_login')

    all_teachers = Teacher.objects.all()
    hods = all_teachers.filter(is_hod=True)
    normal_teachers = all_teachers.filter(is_hod=False)

    # Add branch info directly to each HOD object
    for hod in hods:
        branch = Branch.objects.filter(branch_hod = hod).first()
        hod.branch_name = branch.branch_name if branch else "Not Decided"

    return render(request, 'director/view_teacher.html', {
        'director': director,
        'hods': hods,
        'teachers': normal_teachers,
    })

    return HttpResponse("view teaher logic")
    
def goto_manage_teacher(request, teacher_id):
    director_id = request.session.get('director_id')

    if not director_id:
        messages.error(request, "Director not found. Please log in again.")
        return redirect('open_director_login')

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_director_login')

    teacher = get_object_or_404(Teacher, id=teacher_id)

    # Get branch name from reverse relation if teacher is a HOD
    branch = Branch.objects.filter(branch_hod=teacher).first()
    branch_name = branch.branch_name if branch else "Not Assigned"

    return render(request, 'director/goto_manage_teacher.html', {
        'teacher': teacher,
        'director': director,
        'branch_name': branch_name,
    })

def manage_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':
        # Update basic fields
        teacher.teacher_name = request.POST.get('teacher_name')
        teacher.teacher_username = request.POST.get('teacher_username')
        teacher.teacher_email = request.POST.get('teacher_email')
        teacher.teacher_phone = request.POST.get('teacher_phone')

        # Update is_hod checkbox (only present if checked)
        teacher.is_hod = 'is_hod' in request.POST

        # Handle password change if new password is provided
        new_password = request.POST.get('teacher_password')
        if new_password:
            teacher.set_password(new_password)  # securely hashes the password

        # Save changes
        teacher.save()

        messages.success(request, "Teacher updated successfully.")
        return redirect('view_teacher')

    # Fallback for non-POST (shouldn’t be hit under normal usage)
    messages.error(request, "Invalid request method.")
    return redirect('view_teacher')

def delete_teacher(request, teacher_id):
     # Try to fetch the teacher, if not found, it will raise a 404 error automatically
    try:
        teacher = get_object_or_404(Teacher, id = teacher_id)
        teacher.delete()
        messages.success(request, "Techer successfully deleted.")
        return redirect("view_teacher")
    except Exception as e:
        messages.error(request, f"An error occured while trying to delete the teacher {str(e)} ")
        return redirect("view_teacher")
   

# teaher end






# branch start

def create_branch_form(request):
    director_id = request.session.get('director_id')

    if not director_id:
        messages.error(request, "Director not found. Please log in again.")
        return redirect('open_director_login')

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_director_login')

    # Fetch teachers eligible to be selected as HODs
    teachers = Teacher.objects.filter(is_hod=True)

    return render(request, 'director/create_branch_form.html', {
        'director': director,
        'teachers': teachers,
    })

def create_branch(request):
    if request.method == 'POST':
        branch_name = request.POST.get('branch_name')
        teacher_id = request.POST.get('branch_hod')  # "None" if not selected

        # Validate branch name
        if not branch_name:
            messages.error(request, "Branch name is required.")
            return redirect('create_branch_form')

        # Check for duplicate branch name
        if Branch.objects.filter(branch_name=branch_name).exists():
            messages.error(request, f"Branch '{branch_name}' already exists.")
            return redirect('create_branch_form')

        # If no HOD selected, redirect to teacher form
        if not teacher_id:
            messages.error(request, "HOD is mandatory. Please create/select a teacher as HOD.")
            return redirect('create_teacher_form')

        # Validate the selected teacher
        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            messages.error(request, "Selected HOD does not exist.")
            return redirect('create_branch_form')

        # Check if this teacher is already assigned as HOD
        if Branch.objects.filter(branch_hod=teacher).exists():
            messages.error(request, f"{teacher.teacher_name} is already assigned as HOD to another branch.")
            return redirect('create_branch_form')

        # Create and save the branch
        branch = Branch(branch_name=branch_name, branch_hod=teacher)
        branch.save()

        messages.success(request, "Branch created successfully!")
        return redirect('view_branch')

    return redirect('create_branch_form')

def view_branch(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Director not found. Please log in again.")
        return redirect('open_director_login')

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_director_login')

    try:
        branches = Branch.objects.select_related('branch_hod').order_by('branch_name')
    except Exception as e:
        messages.error(request, f"Error fetching branches: {str(e)}")
        branches = []

    return render(request, 'director/view_branch.html', {
        'branches': branches,
        'director': director
    })

def goto_manage_branch(request, branch_id):
    director_id = request.session.get('director_id')

    if not director_id:
        messages.error(request, "Director not found. Please log in again.")
        return redirect('open_director_login')

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_director_login')

    branch = get_object_or_404(Branch, id=branch_id)

    # Get all HOD-eligible teachers
    hods = Teacher.objects.filter(is_hod=True).order_by('teacher_name')

    return render(request, 'director/goto_manage_branch.html', {
        'branch': branch,
        'director': director,
        'hods': hods
    })

def manage_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    if request.method == 'POST':
        branch_name = request.POST.get('branch_name')
        teacher_id = request.POST.get('branch_hod')  # Could be empty ("None")

        # Validate branch name
        if not branch_name:
            messages.error(request, "Branch name is required.")
            return redirect('goto_manage_branch', branch_id=branch.id)

        # Check if branch name is used by another branch
        if Branch.objects.exclude(id=branch.id).filter(branch_name=branch_name).exists():
            messages.error(request, f"Branch '{branch_name}' already exists.")
            return redirect('goto_manage_branch', branch_id=branch.id)

        # Check if HOD was not selected (None)
        if not teacher_id:
            messages.error(request, "HOD is mandatory. Please create/select a teacher as HOD.")
            return redirect('create_teacher_form')

        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            messages.error(request, "Selected HOD does not exist.")
            return redirect('goto_manage_branch', branch_id=branch.id)

        # Ensure the selected teacher is not already assigned as HOD to a different branch
        if Branch.objects.exclude(id=branch.id).filter(branch_hod=teacher).exists():
            messages.error(request, f"{teacher.teacher_name} is already assigned as HOD to another branch.")
            return redirect('goto_manage_branch', branch_id=branch.id)

        # Update the branch
        branch.branch_name = branch_name
        branch.branch_hod = teacher
        branch.save()

        messages.success(request, "Branch updated successfully!")
        return redirect('view_branch')

    return redirect('goto_manage_branch', branch_id=branch.id)

def delete_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    
    try:
        branch.delete()
        messages.success(request, f"Branch '{branch.branch_name}' deleted successfully.")
    except ProtectedError:
        messages.error(request, f"Cannot delete branch '{branch.branch_name}' because it is used in one or more classes.")
    except Exception as e:
        messages.error(request, f"Failed to delete branch: {str(e)}")

    return redirect('view_branch')


# branch end 



# View for creating Batch
def create_batch_form(request):
    director_id = request.session.get('director_id')

    if not director_id:
        messages.error(request, "Director not found. Please log in again.")
        return redirect('open_director_login')

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_director_login')

    return render(request, 'director/create_batch_form.html', {'director': director})

def create_batch(request):
    if request.method == "POST":
        batch_name = request.POST.get('batch_name', '').strip()

        # Validate input is present
        if not batch_name:
            messages.error(request, "Please enter a batch year.")
            return redirect('create_batch_form')

        try:
            batch_year = int(batch_name)
            current_year = datetime.now().year
            min_year = current_year - 50

            # Check if batch year is within valid range
            if not (min_year <= batch_year <= current_year):
                messages.error(request, f"Batch year must be between {min_year} and {current_year}.")
                return redirect('create_batch_form')

            # Check for duplicates
            if Batch.objects.filter(batch_name=batch_year).exists():
                messages.error(request, f"Batch '{batch_year}' already exists.")
                return redirect('create_batch_form')

            # Create the batch
            Batch.objects.create(batch_name=batch_year)
            messages.success(request, f"Batch '{batch_year}' created successfully.")
            return redirect('view_batch')

        except ValueError:
            messages.error(request, "Invalid batch year. Please enter a valid number.")
            return redirect('create_batch_form')

    return redirect('create_batch_form')

def view_batch(request):
    # Check if the director is logged in
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Director not found. Please log in again.")
        return redirect('open_director_login')

    try:
        # Fetch the director object
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_director_login')

    try:
        # Fetch all batches
        batches = Batch.objects.all().order_by('-batch_name')  # Optional: Change the ordering as needed
    except Exception as e:
        messages.error(request, f"Error fetching batches: {str(e)}")
        batches = []

    return render(request, 'director/view_batch.html', {
        'batches': batches,
        'director': director
    })

def goto_manage_batch(request,batch_id):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Director not found. Please log in again.")
        return redirect('open_director_login')

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_director_login')

    try:
        batch = get_object_or_404(Batch, id=batch_id)
    except Batch.DoesNotExist:
        messages.error(request, "Batch not found.")
        return redirect('view_batch')

    return render(request, 'director/goto_manage_batch.html', {
        'batch': batch,
        'director': director
    })

def manage_batch(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)

    current_year = datetime.now().year
    min_year = current_year - 50

    if request.method == "POST":
        batch_name = request.POST.get("batch_name")

        # Validate year format
        try:
            batch_year = int(batch_name)
            if not (min_year <= batch_year <= current_year):
                messages.error(request, f"Batch year must be between {min_year} and {current_year}.")
                return render(request, 'director/goto_manage_batch.html', {'batch': batch})
        except ValueError:
            messages.error(request, "Invalid batch year. Please enter a valid number.")
            return render(request, 'director/goto_manage_batch.html', {'batch': batch})

        # Prevent duplicate batch names
        if Batch.objects.exclude(id=batch.id).filter(batch_name=batch_year).exists():
            messages.error(request, "Batch with this year already exists.")
            return render(request, 'director/goto_manage_batch.html', {'batch': batch})

        # Save changes
        batch.batch_name = batch_year
        batch.save()
        messages.success(request, "Batch successfully updated.")
        return redirect('view_batch')

    return render(request, 'director/goto_manage_batch.html', {'batch': batch})

def delete_batch(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)

    try:
        batch.delete()
        messages.success(request, f"Batch '{batch.batch_name}' deleted successfully.")
    except ProtectedError:
        messages.error(request, f"Cannot delete batch '{batch.batch_name}' because it is used in one or more classes.")
    except Exception as e:
        messages.error(request, f"Failed to delete batch: {str(e)}")

    return redirect('view_batch')

# batch end 



# class group start
def create_class_form(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, 'Director not found please login again')
        return redirect('open_director_login')
    
    try:
        director = College.objects.get(id = director_id)
    except College.DoesNotExist:
        messages.error(request, 'Dirctor not found')
        return redirect('open_director_login')
    
    batches = Batch.objects.all().order_by('-batch_name')
    branches = Branch.objects.select_related('branch_hod').order_by('branch_name')
    
    return render(request, 'director/create_class_form.html', {
        'director' : director, 
        'batches': batches, 
        'branches': branches
        })

def create_class(request):
    if request.method == 'POST':
        batch_id = request.POST.get('batch')
        branch_id = request.POST.get('branch')

        batch = get_object_or_404(Batch, id = batch_id)
        branch = get_object_or_404(Branch, id = branch_id)

        if ClassGroup.objects.filter(batch = batch, branch = branch).exists():
            messages.error(request, f'Class group with {batch.batch_name} and {branch.branch_name} aleady exists.')
            return redirect('create_class_form')
        
        ClassGroup.objects.create(batch = batch, branch = branch)
        messages.success(request, f"Class for {batch.batch_name} and {branch.branch_name} created successfully")
        return redirect('view_class')
    
    return redirect('create_class_from')

def view_class(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Director not found. Please login again.")
        return redirect('open_director_login')

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_director_login')

    class_groups = ClassGroup.objects.select_related('batch', 'branch', 'branch__branch_hod').order_by('batch__batch_name', 'branch__branch_name')

    return render(request, 'director/view_class.html', {
        'director': director,
        'class_groups': class_groups,
    })
 

def delete_class(request, class_id):
    class_group = get_object_or_404(ClassGroup, id=class_id)

    try:
        class_group.delete()
        messages.success(request, f"Class '{class_group}' deleted successfully.")
    except ProtectedError:
        messages.error(request, "This class cannot be deleted because it is referenced by other data.")
    except Exception as e:
        messages.error(request, f"An error occurred while deleting the class: {str(e)}")

    return redirect('view_class')
