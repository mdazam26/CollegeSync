from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import path, include
from django.contrib import messages
from super.models import College
from django.db.models import ProtectedError
from director.models import Branch, Batch, ClassGroup
from .models import SemesterTemplate, BranchSemester, Subject, SemesterSubject, ActiveClassSemester
from student.models import StudentClass, Student
from collections import defaultdict

# Create your views here.
def index(request):
    director_id = request.session['director_id']
    try:
        director = College.objects.get(id = director_id)
    except College.DoesNotExist:
        messages.error(request,'director not found')
        return redirect('open_director_login')
    
    return render(request, 'semester/index.html', {'director' : director})

def create_semesterTemplate_form(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('open_director_login')

    try:
        director = College.objects.get(id=director_id)
    except College.DoesNotExist:
        messages.error(request, "Director not found.")
        return redirect('open_director_login')

    semester_templates = SemesterTemplate.objects.all().order_by('id')

    return render(request, 'semester/create_semesterTemplate_form.html', {
        'director': director,
        'semester_templates': semester_templates
    })

def create_semesterTemplate(request):
    if request.method == 'POST':
        semester_name = request.POST.get('semester_name', '').strip()

        if not semester_name:
            messages.error(request, "Semester name is required.")
            return redirect('create_semesterTemplate_form')

        if SemesterTemplate.objects.filter(semester_name__iexact=semester_name).exists():
            messages.warning(request, f"'{semester_name}' already exists.")
            return redirect('create_semesterTemplate_form')

        SemesterTemplate.objects.create(semester_name=semester_name)
        messages.success(request, f"Semester Template '{semester_name}' created successfully.")
        return redirect('create_semesterTemplate_form')

    return redirect('create_semesterTemplate_form')


def create_branchSemester_form(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)

    branches = Branch.objects.all()
    semester_templates = SemesterTemplate.objects.all()
    branch_semesters = BranchSemester.objects.select_related('branch', 'semester_template')

    return render(request, 'semester/create_branchSemester_form.html', {
        'director': director,
        'branches': branches,
        'semester_templates': semester_templates,
        'branch_semesters': branch_semesters,
    })

def create_branchSemester(request):
    if request.method == 'POST':
        branch_id = request.POST.get('branch_id')
        semester_template_id = request.POST.get('semester_template_id')

        if not branch_id or not semester_template_id:
            messages.error(request, "Please select both branch and semester.")
            return redirect('create_branchSemester_form')

        branch = get_object_or_404(Branch, id=branch_id)
        semester_template = get_object_or_404(SemesterTemplate, id=semester_template_id)

        if BranchSemester.objects.filter(branch=branch, semester_template=semester_template).exists():
            messages.warning(request, "This Branch-Semester pair already exists.")
            return redirect('create_branchSemester_form')

        BranchSemester.objects.create(branch=branch, semester_template=semester_template)
        messages.success(request, f"{branch.branch_name} - {semester_template.semester_name} mapped successfully.")
        return redirect('create_branchSemester_form')

    return redirect('create_branchSemester_form')

def create_subject_form(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)
    subjects = Subject.objects.all().order_by('name')

    return render(request, 'semester/create_subject_form.html', {
        'director': director,
        'subjects': subjects,
    })

def create_subject(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        credit = request.POST.get('credit')
        modules = request.POST.get('modules')

        if not name or not code:
            messages.error(request, "Name and code are required.")
            return redirect('create_subject_form')

        if Subject.objects.filter(name__iexact=name).exists():
            messages.warning(request, f"Subject '{name}' already exists.")
            return redirect('create_subject_form')

        if Subject.objects.filter(code__iexact=code).exists():
            messages.warning(request, f"Subject code '{code}' already exists.")
            return redirect('create_subject_form')

        try:
            credit = int(credit) if credit else None
            modules = int(modules) if modules else None
        except ValueError:
            messages.error(request, "Credit and modules must be integers.")
            return redirect('create_subject_form')

        Subject.objects.create(
            name=name,
            code=code,
            credit=credit,
            modules=modules
        )

        messages.success(request, f"Subject '{name}' created successfully.")
        return redirect('create_subject_form')

    return redirect('create_subject_form')

def goto_manage_subject(request, subject_id):
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
        subject = get_object_or_404(Subject, id=subject_id)
    except Subject.DoesNotExist:
        messages.error(request, "Subject not found.")
        return redirect('create_subject_form')

    return render(request, 'semester/goto_manage_subject.html', {
        'subject': subject,
        'director': director,
    })

def manage_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        credit = request.POST.get("credit", "").strip()
        modules = request.POST.get("modules", "").strip()

        # Validate name and code
        if not name or not code:
            messages.error(request, "Subject name and code are required.")
            return render(request, 'semester/goto_manage_subject.html', {'subject': subject})

        # Check uniqueness for name and code excluding the current subject
        if Subject.objects.exclude(id=subject.id).filter(name__iexact=name).exists():
            messages.error(request, f"A subject with the name '{name}' already exists.")
            return render(request, 'semester/goto_manage_subject.html', {'subject': subject})

        if Subject.objects.exclude(id=subject.id).filter(code__iexact=code).exists():
            messages.error(request, f"A subject with the code '{code}' already exists.")
            return render(request, 'semester/goto_manage_subject.html', {'subject': subject})

        # Update subject fields
        subject.name = name
        subject.code = code
        subject.credit = int(credit) if credit.isdigit() else None
        subject.modules = int(modules) if modules.isdigit() else None
        subject.save()

        messages.success(request, "Subject updated successfully.")
        return redirect('create_subject_form')

    return render(request, 'semester/goto_manage_subject.html', {'subject': subject})

def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    try:
        subject.delete()
        messages.success(request, f"Subject '{subject.name}' deleted successfully.")
    except ProtectedError:
        messages.error(request, f"Cannot delete subject '{subject.name}' because it is referenced elsewhere.")
    except Exception as e:
        messages.error(request, f"Failed to delete subject: {str(e)}")

    return redirect('create_subject_form')


def create_semesterSubject_form(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)

    branch_semesters = BranchSemester.objects.select_related('branch', 'semester_template')
    subjects = Subject.objects.all()
    semester_subjects = SemesterSubject.objects.select_related('branch_semester', 'subject')

    return render(request, 'semester/create_semesterSubject_form.html', {
        'director': director,
        'branch_semesters': branch_semesters,
        'subjects': subjects,
        'semester_subjects': semester_subjects,
    })


def create_semesterSubject(request):
    if request.method == 'POST':
        branch_semester_id = request.POST.get('branch_semester_id')
        subject_id = request.POST.get('subject_id')

        if not branch_semester_id or not subject_id:
            messages.error(request, "Please select both Branch Semester and Subject.")
            return redirect('create_semesterSubject_form')

        branch_semester = get_object_or_404(BranchSemester, id=branch_semester_id)
        subject = get_object_or_404(Subject, id=subject_id)

        if SemesterSubject.objects.filter(branch_semester=branch_semester, subject=subject).exists():
            messages.warning(request, "This Subject is already assigned to the selected Branch Semester.")
            return redirect('create_semesterSubject_form')

        SemesterSubject.objects.create(branch_semester=branch_semester, subject=subject)
        messages.success(request, f"Subject '{subject.name}' assigned to '{branch_semester}' successfully.")
        return redirect('create_semesterSubject_form')

    return redirect('create_semesterSubject_form')

def create_activeClassSemester_form(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)

    # Get unique class groups that have students
    student_class_groups = (
        StudentClass.objects
        .select_related('class_group')
        .values_list('class_group', flat=True)
        .distinct()
    )
    class_groups = ClassGroup.objects.filter(id__in=student_class_groups).select_related('batch', 'branch')

    branch_semesters = BranchSemester.objects.select_related('branch', 'semester_template')

    # Get existing ActiveClassSemester entries per class group
    active_semesters = ActiveClassSemester.objects.select_related(
        'class_group__batch',
        'class_group__branch',
        'branch_semester__branch',
        'branch_semester__semester_template',
    )

    return render(request, 'semester/create_activeClassSemester_form.html', {
        'director': director,
        'class_groups': class_groups,
        'branch_semesters': branch_semesters,
        'active_semesters': active_semesters,
    })


def create_activeClassSemester(request):
    if request.method == 'POST':
        class_group_id = request.POST.get('class_group_id')
        branch_semester_id = request.POST.get('branch_semester_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if not all([class_group_id, branch_semester_id, start_date, end_date]):
            messages.error(request, "All fields are required.")
            return redirect('create_activeClassSemester_form')

        class_group = get_object_or_404(ClassGroup, id=class_group_id)
        branch_semester = get_object_or_404(BranchSemester, id=branch_semester_id)

        # Avoid duplicate
        exists = ActiveClassSemester.objects.filter(
            class_group=class_group,
            branch_semester=branch_semester
        ).exists()

        if exists:
            messages.info(request, f"An active semester already exists for {class_group}.")
        else:
            ActiveClassSemester.objects.create(
                class_group=class_group,
                branch_semester=branch_semester,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            messages.success(request, f"Active semester created for {class_group}.")

        return redirect('create_activeClassSemester_form')

    return redirect('create_activeClassSemester_form')


def goto_manage_activeClassSemester(request, acs_id):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)
    acs = get_object_or_404(
        ActiveClassSemester.objects.select_related(
            'class_group__batch', 
            'class_group__branch',
            'branch_semester__branch', 
            'branch_semester__semester_template'
        ),
        id=acs_id
    )

    return render(request, 'semester/goto_manage_activeClassSemester.html', {
        'director': director,
        'acs': acs,
    })

def manage_activeClassSemester(request, acs_id):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)
    acs = get_object_or_404(ActiveClassSemester, id=acs_id)

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active') == 'on'

        acs.start_date = start_date or None
        acs.end_date = end_date or None
        acs.is_active = is_active
        acs.save()

        messages.success(request, "Semester status updated successfully.")
        return redirect('goto_manage_activeClassSemester', acs_id=acs.id)

    return render(request, 'semester/goto_manage_activeClassSemester.html', {
        'acs': acs,
        'director': director,
    })

def delete_activeClassSemester(request, acs_id):
    acs = get_object_or_404(ActiveClassSemester, id=acs_id)

    try:
        acs.delete()
        messages.success(request, "Active class semester deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting: {str(e)}")

    return redirect('create_activeClassSemester_form')
