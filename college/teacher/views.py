from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from director.models import Teacher, ClassGroup, Batch, Branch
from student.models import Student
from django.contrib.auth.hashers import check_password
from semester.models import ActiveClassSemester
from django.contrib.auth.decorators import login_required
from schedule.models import ClassSchedule2, PeriodSlot, Day
from semester.models import SemesterSubject
from django.db.models import Q
from collections import defaultdict
from .models import AttendanceRecord
from datetime import date
from student.models import StudentClass



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
    
    class_schedules2 = ClassSchedule2.objects.select_related(
        'active_semester2', 'day2', 'period2', 'subject2', 'teacher2'
    ).filter(
        active_semester2__branch_semester__branch=branch
    ).order_by('day2__id', 'period2__start_time')


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
    
    periods = PeriodSlot.objects.all().order_by('start_time')
    days = Day.objects.all()
    grouped_schedules = defaultdict(list)
    for schedule in class_schedules2:
        grouped_schedules[schedule.active_semester2].append(schedule)

    context = {
        'teacher': teacher,
        'branch': branch,
        'active_semesters': active_semesters,
        'selected_active_id': selected_active_id,
        'selected_active': selected_active,
        'schedule_slots': schedule_slots,  # list of dicts with 'slot' and 'available_teachers'
        'semester_subjects': semester_subjects,
        'periods': periods,
        'days': days,
        'class_schedules2': class_schedules2,
        'grouped_schedules': grouped_schedules.items(),
    }
    return render(request, 'teacher/create_schedule_form.html', context)


def create_schedule(request):
    if request.method == 'POST':
        teacher_id = request.session.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)

        if not teacher.is_hod:
            messages.error(request, "Unauthorized access.")
            return redirect('teacher_dashboard')

        active_semester_id = request.POST.get('active_semester')
        if not active_semester_id:
            messages.error(request, "No active semester selected.")
            return redirect('create_schedule_form')

        try:
            active_semester = ActiveClassSemester.objects.get(id=active_semester_id)
            updated = False  # Track if anything changed

            for key, value in request.POST.items():
                if key.startswith('subject_'):
                    slot_id = key.split('_')[1]
                    subject_id = value
                    teacher_id = request.POST.get(f'teacher_{slot_id}')

                    if not subject_id or not teacher_id:
                        continue  # Skip incomplete rows

                    try:
                        slot = ClassSchedule2.objects.get(id=slot_id)
                        subject = SemesterSubject.objects.get(id=subject_id)
                        teacher_obj = Teacher.objects.get(id=teacher_id)

                        slot.subject2 = subject
                        slot.teacher2 = teacher_obj
                        slot.save()
                        updated = True
                    except Exception as e:
                        messages.warning(request, f"Could not update slot {slot_id}: {e}")

            if updated:
                messages.success(request, "Schedule updated successfully.")
            else:
                messages.info(request, "No changes were made to the schedule.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect('create_schedule_form')
    

def goto_manage_schedule(request, schedule_id):
    teacher_id = request.session.get('teacher_id')
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if not teacher.is_hod:
        messages.error(request, "Unauthorized access.")
        return redirect('teacher_dashboard')

    # Fetch the schedule
    schedule = get_object_or_404(ClassSchedule2, id=schedule_id)

    # Get the branch from the HOD
    branch = Branch.objects.filter(branch_hod=teacher).first()

    # Get all periods and days
    periods = PeriodSlot.objects.all().order_by('start_time')
    days = Day.objects.all()

    # Active semester to which this schedule belongs
    active_semester = schedule.active_semester2

    # Get semester subjects linked to this semester
    semester_subjects = SemesterSubject.objects.filter(
        branch_semester=active_semester.branch_semester
    )

    # Get available teachers for this slot
    all_teachers = set(Teacher.objects.all())
    busy_teacher_ids = ClassSchedule2.objects.filter(
        day2=schedule.day2,
        period2=schedule.period2
    ).exclude(id=schedule.id).values_list('teacher2_id', flat=True)
    busy_teachers = set(Teacher.objects.filter(id__in=busy_teacher_ids))
    available_teachers = all_teachers - busy_teachers

    context = {
        'teacher': teacher,
        'branch': branch,
        'schedule': schedule,
        'active_semester': active_semester,
        'semester_subjects': semester_subjects,
        'periods': periods,
        'days': days,
        'available_teachers': available_teachers,
    }

    return render(request, 'teacher/goto_manage_schedule.html', context)

def manage_schedule(request, schedule_id):
    teacher_id = request.session.get('teacher_id')
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if not teacher.is_hod:
        messages.error(request, "Unauthorized access.")
        return redirect('teacher_dashboard')

    schedule = get_object_or_404(ClassSchedule2, id=schedule_id)

    if request.method == 'POST':
        try:
            # Required fields
            day_id = request.POST.get('day')
            period_id = request.POST.get('period')

            # Optional fields
            subject_id = request.POST.get('subject')
            teacher_input_id = request.POST.get('teacher')

            # Update schedule with validated input
            schedule.day2 = get_object_or_404(Day, id=day_id)
            schedule.period2 = get_object_or_404(PeriodSlot, id=period_id)

            if subject_id:
                schedule.subject2 = get_object_or_404(SemesterSubject, id=subject_id)
            else:
                schedule.subject2 = None

            if teacher_input_id:
                schedule.teacher2 = get_object_or_404(Teacher, id=teacher_input_id)
            else:
                schedule.teacher2 = None

            schedule.save()
            messages.success(request, "Schedule updated successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while updating: {e}")

    return redirect('create_schedule_form')

def delete_schedule(request, schedule_id):
    teacher_id = request.session.get('teacher_id')
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if not teacher.is_hod:
        messages.error(request, "Unauthorized access.")
        return redirect('teacher_dashboard')

    schedule = get_object_or_404(ClassSchedule2, id=schedule_id)

    try:
        schedule.delete()
        messages.success(request, "Schedule deleted successfully.")
    except Exception as e:
        messages.error(request, f"Failed to delete schedule: {e}")

    return redirect('create_schedule_form')


def teacher_schedule_view(request):
    teacher_id = request.session.get('teacher_id')
    teacher = get_object_or_404(Teacher, id=teacher_id)

    schedule_qs = ClassSchedule2.objects.filter(teacher2=teacher).select_related(
        'subject2__subject', 'active_semester2', 'day2', 'period2'
    )

    timetable = {}
    for schedule in schedule_qs:
        day_name = schedule.day2.name
        period_name = schedule.period2.name  # ✅ corrected
        timetable[(day_name, period_name)] = schedule

    all_days = Day.objects.all()
    all_periods = PeriodSlot.objects.values_list('name', flat=True)  # ✅ corrected

    return render(request, 'teacher/teacher_schedule.html', {
        'teacher': teacher,
        'timetable': timetable,
        'all_days': all_days,
        'all_periods': all_periods,
    })



def take_class(request, schedule_id):
    schedule = get_object_or_404(ClassSchedule2.objects.select_related(
        'active_semester2__class_group',
        'subject2__subject',
        'teacher2',
        'day2'
    ), id=schedule_id)

    active_class_semester = schedule.active_semester2
    class_group = active_class_semester.class_group

    student_classes = StudentClass.objects.select_related('student').filter(
        class_group=class_group
    ).order_by('student__student_enrollment_number')
    students = [sc.student for sc in student_classes]

    context = {
        'schedule': schedule,
        'subject': schedule.subject2.subject,
        'teacher': schedule.teacher2,
        'active_class_semester': active_class_semester,
        'students': students,
        'day': schedule.day2.name,
        # Optional: pass today if you want it as a default
        'today': date.today().isoformat(),
    }

    return render(request, 'teacher/take_class.html', context)

def mark_attendance(request, schedule_id):
    return HttpResponse('save attendance')