from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from director.models import Teacher, ClassGroup, Batch, Branch
from student.models import Student
from django.contrib.auth.hashers import check_password
from semester.models import ActiveClassSemester
from django.contrib.auth.decorators import login_required
from schedule.models import ClassSchedule2
from semester.models import SemesterSubject
from django.db.models import Q

# Create your views here.

def professor_login_page(request):
    return render(request,'teacher/login.html')

def professor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        raw_password = request.POST.get('password')

        try:
            teacher = Teacher.objects.get(teacher_username=username)
            if check_password(raw_password, teacher.teacher_password):
                request.session['teacher_id'] = teacher.id
                return redirect('teacher_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        except Teacher.DoesNotExist:
            messages.error(request, "Invalid username or password.")

    return render(request, 'teacher/login.html')

def professor_logout(request):
    if 'teacher_id' in request.session:
        del request.session['teacher_id']
        messages.success(request, "Logged out successfully.")
    return redirect('professor_login')

def teacher_dashboard(request):
    teacher_id = request.session.get('teacher_id')
    if not teacher_id:
        messages.error(request, "You must log in first.")
        return redirect('teacher_login')

    teacher = get_object_or_404(Teacher, id=teacher_id)

    context = {
        'teacher': teacher
    }

    if teacher.is_hod:
        return render(request, 'teacher/hod_dashboard.html', context)
    else:
        return render(request, 'teacher/non_hod_dashboard.html', context)
    
def view_branch_students(request):
    teacher_id = request.session.get('teacher_id')
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if not teacher.is_hod:
        messages.error(request, "Unauthorized access.")
        return redirect('teacher_dashboard')

    # HOD's branch
    branch = Branch.objects.filter(branch_hod=teacher).first()

    selected_classgroup_id = request.GET.get('classgroup')
    classgroups = ClassGroup.objects.filter(branch=branch)

    students = []
    selected_classgroup = None
    if selected_classgroup_id:
        selected_classgroup = get_object_or_404(ClassGroup, id=selected_classgroup_id, branch=branch)
        students = Student.objects.filter(
            student_batch=selected_classgroup.batch,
            student_branch=branch
        ).order_by('student_enrollment_number')  # ✅ Sort here

    return render(request, 'teacher/branch_students.html', {
        'teacher': teacher,
        'students': students,
        'classgroups': classgroups,
        'selected_classgroup_id': selected_classgroup_id,
    })


def create_schedule_form(request):
    teacher_id = request.session.get('teacher_id')
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if not teacher.is_hod:
        messages.error(request, "Unauthorized access.")
        return redirect('teacher_dashboard')

    branch = Branch.objects.filter(branch_hod=teacher).first()
    active_semesters = ActiveClassSemester.objects.filter(branch_semester__branch=branch)

    selected_active_id = request.GET.get('active_semester')
    selected_active = None
    schedule_slots = []
    semester_subjects = []
    
    if selected_active_id:
        selected_active = get_object_or_404(
            ActiveClassSemester,
            id=selected_active_id,
            branch_semester__branch=branch
        )

        all_teachers = set(Teacher.objects.all())

        raw_slots = ClassSchedule2.objects.filter(
            active_semester2=selected_active
        ).order_by('day2', 'period2')

        schedule_slots = []
        for slot in raw_slots:
            busy_teacher_ids = ClassSchedule2.objects.filter(
                day2=slot.day2,
                period2=slot.period2
            ).exclude(id=slot.id).values_list('teacher2_id', flat=True)

            busy_teachers = set(Teacher.objects.filter(id__in=busy_teacher_ids))
            available_teachers = all_teachers - busy_teachers

            schedule_slots.append({
                'slot': slot,  # The ClassSchedule2 instance
                'available_teachers': available_teachers
            })

        semester_subjects = SemesterSubject.objects.filter(
            branch_semester=selected_active.branch_semester
        )

    context = {
        'teacher': teacher,
        'branch': branch,
        'active_semesters': active_semesters,
        'selected_active_id': selected_active_id,
        'selected_active': selected_active,
        'schedule_slots': schedule_slots,  # list of dicts with 'slot' and 'available_teachers'
        'semester_subjects': semester_subjects,
    }
    return render(request, 'teacher/create_schedule_form.html', context)


def create_schedule(request):
    return HttpResponse("create schedule")