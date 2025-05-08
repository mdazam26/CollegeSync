from django.shortcuts import render, redirect, get_object_or_404
from super.models import College
from director.models import ClassGroup, Batch, Branch
from django.http import HttpResponse
from django.urls import path, include, reverse
from tenants.models import TenantDomain
from django.contrib import messages
from .models import Student, StudentClass
from datetime import datetime, date


def index(request):
    director_id = request.session['director_id']
    try:
        director = College.objects.get(id = director_id)
    except College.DoesNotExist:
        messages.error(request,'director not found')
        return redirect('open_director_login')
    
    return render(request, 'student/index.html', {'director': director})

def create_student_form(request):
    director_id = request.session['director_id']
    try:
        director = College.objects.get(id = director_id)
    except:
        messages.error(request, 'Director not found')
        return redirect('opem_director_login')
    try:
        batches = Batch.objects.all()
    except:
        messages.error(request, 'Batch not found')
        return redirect('create_student_form')
    try:
        branches = Branch.objects.all()
    except:
        messages.error(request, 'Branch not found')
    return render(request, 'student/create_student_form.html', {'director' : director, 'batches' : batches, 'branches' : branches})

def create_student(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name', '').strip()
        student_photo = request.FILES.get('student_photo')
        student_roll = request.POST.get('student_roll', '').strip()
        student_email = request.POST.get('student_email', '').strip()
        student_phone = request.POST.get('student_phone', '').strip()
        student_gender = request.POST.get('student_gender', '')
        student_dob_input = request.POST.get('student_dob')
        student_enrollment_number = request.POST.get('student_enrollment_number', '').strip()
        student_address = request.POST.get('student_address', '').strip()
        student_batch = request.POST.get('student_batch')
        student_branch = request.POST.get('student_branch')

    
        if not student_name or not student_enrollment_number:
            messages.error(request, "Student name and enrollment number are required.")
            return redirect('create_student_form')

        if not student_batch or not student_branch:
            messages.error(request, "Batch and Branch are both compulsory.")
            return redirect('director_dashboard')
        
        batch = get_object_or_404(Batch, id=student_batch)
        branch = get_object_or_404(Branch, id=student_branch)

        # remove unique feature in development

        # if student_email and Student.objects.filter(student_email=student_email).exists():
        #     messages.error(request, "Email is already registered.")
        #     return redirect('create_student_form')

        # if student_phone and Student.objects.filter(student_phone=student_phone).exists():
        #     messages.error(request, "Phone number is already registered.")
        #     return redirect('create_student_form')

        # if student_enrollment_number and Student.objects.filter(student_enrollment_number=student_enrollment_number).exists():
        #     messages.error(request, "Enrollment number already exists.")
        #     return redirect('create_student_form')

        if student_dob_input:
            try:
                student_dob = datetime.strptime(student_dob_input, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
                return redirect('create_student_form')
        else:
            student_dob = date.today() 
     
        student = Student(
            student_name=student_name,
            student_photo=student_photo,
            student_roll=student_roll,
            student_email=student_email,
            student_phone=student_phone,
            student_gender=student_gender,
            student_dob=student_dob,
            student_enrollment_number=student_enrollment_number,
            student_address=student_address,
            student_batch=batch,
            student_branch=branch
        )

        try:
            student.save()
        except Exception as e:
            messages.error(request, f"An error occurred while creating the student: {e}")
            return redirect('create_student_form')

        messages.success(request, "Student created successfully!")
        return redirect('view_student')  

    else:
        return redirect('create_student_form')

def view_student(request):
    director_id = request.session.get('director_id')
    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found")
        return redirect('open_director_login')

    all_students = Student.objects.all().order_by('student_enrollment_number')

    return render(request, 'student/view_student.html', {
        'director': director,
        'students': all_students,
    })

def goto_manage_student(request, student_id):
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
        batches = Batch.objects.all()
    except:
        messages.error(request, "Batch not found")
        return redirect('view_student')
    try:
        branches = Branch.objects.all()
    except:
        messages.error(request, 'Branch not found')
        return redirect('view_student')
    

    student = get_object_or_404(Student, id=student_id)

    return render(request, 'student/goto_manage_student.html', {
        'student': student,
        'director': director,
        'batches' : batches,
        'branches' : branches

    })

def manage_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        name = request.POST.get('student_name')
        roll = request.POST.get('student_roll')
        email = request.POST.get('student_email')
        phone = request.POST.get('student_phone')
        gender = request.POST.get('student_gender')
        dob_input = request.POST.get('student_dob')
        enrollment_number = request.POST.get('student_enrollment_number')
        address = request.POST.get('student_address')
        student_batch_id = request.POST.get('student_batch')
        student_branch_id = request.POST.get('student_branch')

        # remove uniquness feature for development
        
        # if Student.objects.exclude(id=student.id).filter(student_email=email).exists():
        #     messages.error(request, "Email already exists for another student.")
        #     return redirect('goto_manage_student', student_id=student.id)

        # if Student.objects.exclude(id=student.id).filter(student_phone=phone).exists():
        #     messages.error(request, "Phone number already exists for another student.")
        #     return redirect('goto_manage_student', student_id=student.id)

        if Student.objects.exclude(id=student.id).filter(student_enrollment_number=enrollment_number).exists():
            messages.error(request, "Enrollment number already exists for another student.")
            return redirect('goto_manage_student', student_id=student.id)

        if dob_input:
            try:
                student_dob = datetime.strptime(dob_input, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
                return redirect('create_student_form')
        else:
            student_dob = date.today()


        student.student_name = name
        student.student_roll = roll
        student.student_email = email
        student.student_phone = phone
        student.student_gender = gender
        student.student_dob = student_dob
        student.student_enrollment_number = enrollment_number
        student.student_address = address
        # student_batch = student_batch
        # student_branch = student_branch

        if student_batch_id:
            try:
                batch = Batch.objects.get(id=student_batch_id)
                student.student_batch = batch
            except Batch.DoesNotExist:
                messages.error(request, "Invalid batch selected.")
                return redirect('goto_manage_student', student_id=student.id)

        if student_branch_id:
            try:
                branch = Branch.objects.get(id=student_branch_id)
                student.student_branch = branch
            except Branch.DoesNotExist:
                messages.error(request, "Invalid branch selected.")
                return redirect('goto_manage_student', student_id=student.id)

        # Update photo if uploaded
        if 'student_photo' in request.FILES:
            student.student_photo = request.FILES['student_photo']

        # Save changes
        student.save()
        messages.success(request, "Student updated successfully.")
        return redirect('view_student')

    messages.error(request, "Invalid request method.")
    return redirect('view_student')

def delete_student(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id)
        student.delete()
        messages.success(request, "Student successfully deleted.")
        return redirect("view_student")
    except Exception as e:
        messages.error(request, f"An error occurred while trying to delete the student: {str(e)}")
        return redirect("view_student")
    


# assign student
def existing_students_form(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, 'Session expired or director not logged in.')
        return redirect('opem_director_login')

    director = get_object_or_404(College, id=director_id)

    # Get list of classgroups for dropdown
    classgroups = ClassGroup.objects.all()

    classgroup_id = request.GET.get('classgroup_id')
    class_group = None
    unlinked_students = []
    linked_students = []

    if classgroup_id:
        class_group = get_object_or_404(ClassGroup, id=classgroup_id)
        linked_student_ids = list(
            StudentClass.objects.filter(class_group=class_group)
            .values_list('student_id', flat=True).distinct()
        )
        print("Linked student IDs:", list(linked_student_ids))

        unlinked_students = Student.objects.filter(
            student_branch=class_group.branch,
            student_batch=class_group.batch
        ).exclude(id__in=linked_student_ids)

        print("Unlinked students:", list(unlinked_students))

        linked_students = StudentClass.objects.filter(class_group=class_group).select_related('student')

    return render(request, 'student/existing_student_form.html', {
        'director': director,
        'classgroups': classgroups,
        'selected_classgroup': class_group,
        'unlinked_students': unlinked_students,
        'linked_students': linked_students
    })


def add_existing_student(request, classgroup_id):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        if not student_id:
            messages.error(request, "No student selected.")
            return redirect(f"{reverse('existing_students_form')}?classgroup_id={classgroup_id}")
        
        # Validate existence of student and class group
        student = get_object_or_404(Student, id=student_id)
        class_group = get_object_or_404(ClassGroup, id=classgroup_id)

        # Create link only if it doesn't exist
        student_class, created = StudentClass.objects.get_or_create(
            student=student,
            class_group=class_group
        )

        if created:
            messages.success(request, f"Student '{student.student_name}' assigned to class group successfully.")
        else:
            messages.info(request, f"Student '{student.student_name}' is already assigned to this class group.")

    return redirect(f"{reverse('existing_students_form')}?classgroup_id={classgroup_id}")

def classgroup_create_student_form(request, classgroup_id):
    return HttpResponse(f"Form to create a new student for ClassGroup ID: {classgroup_id}")

def classgroup_create_student(request, classgroup_id):
    return HttpResponse(f"Create and link new student to ClassGroup ID: {classgroup_id}")

def classgroup_view_student(request, classgroup_id):
    return HttpResponse(f"View all students linked to ClassGroup ID: {classgroup_id}")

def goto_manage_classgroup_student(request, studentclass_id):
    return HttpResponse(f"Open edit form for StudentClass ID: {studentclass_id}")

def manage_classgroup_student(request, studentclass_id):
    return HttpResponse(f"Update StudentClass entry with ID: {studentclass_id}")

def delete_classgroup_student(request, studentclass_id):
    return HttpResponse(f"Delete StudentClass entry with ID: {studentclass_id}")