from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from django.urls import path, include
from super.models import College
from django.contrib import messages
from .models import PeriodSlot, Day
from schedule.models import ClassSchedule2, ClassSchedule
from semester.models import ActiveClassSemester, SemesterSubject, SemesterTemplate, Subject, BranchSemester 
from director.models import Teacher
from django.db.models import ProtectedError
from collections import defaultdict

# Create your views here.
def index(request):
    director_id = request.session['director_id']
    try:
        director = College.objects.get(id = director_id)
    except College.DoesNotExist:
        messages.error(request,'director not found')
        return redirect('open_director_login')
    
    return render(request, 'schedule/index.html', {'director': director})

def create_periodSlots_form(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)
    periodslots = PeriodSlot.objects.all().order_by('start_time')

    return render(request, 'schedule/create_periodSlots_form.html', {
        'director': director,
        'periodslots': periodslots,
    })

def create_periodSlot(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if not name or not start_time or not end_time:
            messages.error(request, "All fields are required.")
            return redirect('create_periodSlots_form')

        if PeriodSlot.objects.filter(name__iexact=name).exists():
            messages.warning(request, f"Period slot '{name}' already exists.")
            return redirect('create_periodSlots_form')

        try:
            # Let Django handle the conversion and validation via the model
            PeriodSlot.objects.create(
                name=name,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, f"Period slot '{name}' created successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
        
    return redirect('create_periodSlots_form')

def goto_manage_periodSlot(request, period_id):
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
        period_slot = get_object_or_404(PeriodSlot, id=period_id)
    except PeriodSlot.DoesNotExist:
        messages.error(request, "Period slot not found.")
        return redirect('create_periodSlots_form')

    return render(request, 'schedule/goto_manage_periodSlots.html', {
        'period_slot': period_slot,
        'director': director,
    })

def manage_periodSlot(request, period_id):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)
    period = get_object_or_404(PeriodSlot, id=period_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        start_time = request.POST.get('start_time', '').strip()
        end_time = request.POST.get('end_time', '').strip()

        # Validate fields
        if not name or not start_time or not end_time:
            messages.error(request, "All fields (name, start time, end time) are required.")
            return render(request, 'schedule/periodslot/goto_manage_periodSlots.html', {'period_slot': period})

        # Check for uniqueness of name (optional)
        if PeriodSlot.objects.exclude(id=period.id).filter(name__iexact=name).exists():
            messages.error(request, f"A period with the name '{name}' already exists.")
            return render(request, 'schedule/periodslot/goto_manage_periodSlots.html', {'period_slot': period})

        # Update values
        period.name = name
        period.start_time = start_time
        period.end_time = end_time
        period.save()

        messages.success(request, "PeriodSlot updated successfully.")
        return redirect('create_periodSlots_form')

    return render(request, 'schedule/periodslot/goto_manage_periodSlots.html', {'period_slot': period})

def delete_periodSlot(request, period_id):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)
    period = get_object_or_404(PeriodSlot, id=period_id)

    try:
        period.delete()
        messages.success(request, f"PeriodSlot '{period.name}' deleted successfully.")
    except ProtectedError:
        messages.error(request, f"Cannot delete period slot '{period.name}' because it is referenced elsewhere.")
    except Exception as e:
        messages.error(request, f"Failed to delete period slot: {str(e)}")

    return redirect('create_periodSlots_form')



def days(request):
    days = Day.objects.all()
    return render(request, 'schedule/day_list.html', {'days': days})

def create_classSchedule_form(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)

    class_schedules2 = ClassSchedule2.objects.select_related(
        'active_semester2', 'day2', 'period2', 'subject2', 'teacher2',
        'active_semester2__class_group__branch',
        'active_semester2__class_group__batch'
    ).order_by('day2__id', 'period2__start_time')

    print(f"class_schedules type: {type(class_schedules2)}")   
    print(f"Count: {class_schedules2.count()}")
    print(f"class_schedules count: {class_schedules2.count()}")

    grouped_schedules = defaultdict(list)
    for sched in class_schedules2:
        grouped_schedules[sched.active_semester2].append(sched)

    active_semesters = ActiveClassSemester.objects.select_related(
        'class_group__branch', 'class_group__batch'
    ).all()

    # active_semesters = ActiveClassSemester.objects.all()

    periods = PeriodSlot.objects.all().order_by('start_time')
    days = Day.objects.all()
    subjects = SemesterSubject.objects.all()
    teachers = Teacher.objects.all()

    return render(request, 'schedule/create_classSchedule_form.html', {
        'director': director,
        'grouped_schedules': grouped_schedules.items(),
        'class_schedules2': class_schedules2,
        'active_semesters': active_semesters,
        'periods': periods,
        'days': days,
        'subjects': subjects,
        'teachers': teachers,
    })

def create_classSchedule(request):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)
    if request.method == 'POST':
            active_semester_id = request.POST.get('active_semester')
            day_id = request.POST.get('day')
            period_id = request.POST.get('period')
            subject_id = request.POST.get('subject')
            teacher_id = request.POST.get('teacher')

            # Validation
            if not all([active_semester_id, day_id, period_id]):
                messages.error(request, "Active semester, day, and period are required.")
                return redirect('create_classSchedule_form')

            try:
                active_semester = ActiveClassSemester.objects.get(id=active_semester_id)
                day = Day.objects.get(id=day_id)
                period = PeriodSlot.objects.get(id=period_id)
                subject = SemesterSubject.objects.get(id=subject_id) if subject_id else None
                teacher = Teacher.objects.get(id=teacher_id) if teacher_id else None

                # Prevent duplicate schedule entry
                if ClassSchedule2.objects.filter(active_semester2=active_semester, day2=day, period2=period).exists():
                    messages.warning(request, "A schedule for this class, day, and period already exists.")
                    return redirect('create_classSchedule_form')

                # Create new schedule
                ClassSchedule2.objects.create(
                    active_semester2=active_semester,
                    day2=day,
                    period2=period,
                    subject2=subject,
                    teacher2=teacher
                )
                messages.success(request, "Class schedule created successfully.")
            except Exception as e:
                messages.error(request, f"Error: {e}")

    return redirect('create_classSchedule_form')



def goto_manage_classSchedule(request, schedule_id):
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
        schedule = get_object_or_404(ClassSchedule2, id=schedule_id)
    except ClassSchedule2.DoesNotExist:
        messages.error(request, "Class schedule not found.")
        return redirect('create_classSchedule_form')

    # Fetch necessary dropdown data
    active_semesters = ActiveClassSemester.objects.all()
    days = Day.objects.all()
    periods = PeriodSlot.objects.all()
    subjects = SemesterSubject.objects.all()
    teachers = Teacher.objects.all()

    return render(request, 'schedule/goto_manage_classSchedule.html', {
        'schedule': schedule,
        'director': director,
        'active_semesters': active_semesters,
        'days': days,
        'periods': periods,
        'subjects': subjects,
        'teachers': teachers,
    })

def manage_classSchedule(request, schedule_id):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)

    schedule = get_object_or_404(ClassSchedule2, id=schedule_id)

    # Dropdown data for rendering
    active_semesters = ActiveClassSemester.objects.all()
    days = Day.objects.all()
    periods = PeriodSlot.objects.all()
    subjects = SemesterSubject.objects.all()
    teachers = Teacher.objects.all()

    if request.method == 'POST':
        active_semester_id = request.POST.get('active_semester')
        day_id = request.POST.get('day')
        period_id = request.POST.get('period')
        subject_id = request.POST.get('subject')
        teacher_id = request.POST.get('teacher')

        # Validation
        if not active_semester_id or not day_id or not period_id:
            messages.error(request, "Active semester, day, and period are required.")
            return render(request, 'schedule/goto_manage_classSchedule.html', {
                'schedule': schedule,
                'active_semesters': active_semesters,
                'days': days,
                'periods': periods,
                'subjects': subjects,
                'teachers': teachers,
            })

        try:
            active_semester = ActiveClassSemester.objects.get(id=active_semester_id)
            day = Day.objects.get(id=day_id)
            period = PeriodSlot.objects.get(id=period_id)
            subject = SemesterSubject.objects.get(id=subject_id) if subject_id else None
            teacher = Teacher.objects.get(id=teacher_id) if teacher_id else None

            # Prevent duplicate schedule
            if ClassSchedule2.objects.exclude(id=schedule.id).filter(
                active_semester2=active_semester,
                day2=day,
                period2=period
            ).exists():
                messages.warning(request, "A schedule for this semester, day, and period already exists.")
                return render(request, 'schedule/goto_manage_classSchedule.html', {
                    'schedule': schedule,
                    'active_semesters': active_semesters,
                    'days': days,
                    'periods': periods,
                    'subjects': subjects,
                    'teachers': teachers,
                })

            # Save updates
            schedule.active_semester2 = active_semester
            schedule.day2 = day
            schedule.period2 = period
            schedule.subject2 = subject
            schedule.teacher2 = teacher
            schedule.save()

            messages.success(request, "Class schedule updated successfully.")
            return redirect('create_classSchedule_form')

        except Exception as e:
            messages.error(request, f"Error while updating: {e}")
            return render(request, 'schedule/goto_manage_classSchedule.html', {
                'schedule': schedule,
                'active_semesters': active_semesters,
                'days': days,
                'periods': periods,
                'subjects': subjects,
                'teachers': teachers,
            })

    # GET fallback (shouldn’t happen under normal flow)
    return render(request, 'schedule/goto_manage_classSchedule.html', {
        'schedule': schedule,
        'active_semesters': active_semesters,
        'days': days,
        'periods': periods,
        'subjects': subjects,
        'teachers': teachers,
        'director': director
    })

def delete_classSchedule(request, schedule_id):
    director_id = request.session.get('director_id')
    if not director_id:
        messages.error(request, "Please log in again.")
        return redirect('open_director_login')

    director = get_object_or_404(College, id=director_id)
    schedule = get_object_or_404(ClassSchedule2, id=schedule_id)

    try:
        schedule.delete()
        messages.success(request, "Class schedule deleted successfully.")
    except ProtectedError:
        messages.error(request, "Cannot delete this schedule because it is referenced elsewhere.")
    except Exception as e:
        messages.error(request, f"Failed to delete class schedule: {str(e)}")

    return redirect('create_classSchedule_form')