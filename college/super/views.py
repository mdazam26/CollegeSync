from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from .models import College

from .forms import CollegeForm
from django.contrib import messages
# Create your views here.

def main(request):
    return render(request, 'super/main.html')

def open_create(request):
    return render(request, 'super/create.html')

def create(request):
    if request.method == "POST":
        institute_name = request.POST.get('institute_name')
        institute_address = request.POST.get('institute_address')
        institute_email = request.POST.get('institute_email')
        institute_number = request.POST.get('institute_number')

        admin_name = request.POST.get('admin_name')
        admin_number = request.POST.get('admin_number')
        admin_email = request.POST.get('admin_email')
        admin_username = request.POST.get('admin_username')
        admin_password = request.POST.get('admin_password')
        confirm_password = request.POST.get('confirm_password')

        if(College.objects.filter(admin_username = admin_username).exists()):
            messages.error(request, 'Username already exits!')

            return redirect('open_create')

        if admin_password != confirm_password:
            messages.error(request, 'Password do not match')
            return redirect('open_create')

        College.objects.create(
            institute_name = institute_name,
            institute_address = institute_address,
            institute_email = institute_email,
            institute_number = institute_number,

            admin_name = admin_name,
            admin_number = admin_number,
            admin_email = admin_email,
            admin_username = admin_username,
            admin_password = make_password(admin_password) ,
        )

        messages.success(request, "College created successfully!")  # Add a success message
        return redirect('view')  # Redirect to a page that shows the created college(s)
    
    else:
        return HttpResponse("User not created")

    

    # if request.method == 'POST':
    #     form = CollegeForm(request.POST)
    #     if form.is_valid():
    #         # Save the form data and create a new College instance
    #         college = form.save(commit=False)
    #         # Optionally, you can add any custom behavior like encrypting passwords here
    #         college.admin_password = make_password(college.admin_password)

    #         college.save()  # Save the college instance to the database
            
    #         messages.success(request, "College created successfully!")  # Add a success message
    #         return redirect('view')  # Redirect to a page that shows the created college(s)
    #     else:
    #         messages.error(request, "There was an error with your form submission.")  # Add an error message
    # else:
    #     form = CollegeForm()  # Initialize the form if the request is GET

    # return render(request, 'super/create.html', {'form': form})

def view(request):
    colleges = College.objects.all()
    return render(request, 'super/view.html', {'colleges': colleges})

def manage(request, college_id):
    # Retrieve the college object from the database
    college = get_object_or_404(College, id=college_id)

    if request.method == 'POST':
        # Get the form data from the request
        institute_name = request.POST.get('institute_name')
        institute_address = request.POST.get('institute_address')
        institute_email = request.POST.get('institute_email')
        institute_number = request.POST.get('institute_number')
        admin_name = request.POST.get('admin_name')
        admin_number = request.POST.get('admin_number')
        admin_email = request.POST.get('admin_email')
        admin_username = request.POST.get('admin_username')

        # Update the college object with the new data
        college.institute_name = institute_name
        college.institute_address = institute_address
        college.institute_email = institute_email
        college.institute_number = institute_number
        college.admin_name = admin_name
        college.admin_number = admin_number
        college.admin_email = admin_email
        college.admin_username = admin_username

        # Save the updated college object back to the database
        college.save()

        # Display a success message
        messages.success(request, 'College details updated successfully.')

        # Redirect to the 'view' page or wherever you'd like
        return redirect('view')

    return render(request, 'super/manage.html', {'college': college})

def manage_college(request, college_id):
    college = get_object_or_404(College, id=college_id)
    return render(request, 'super/manage.html', {'college': college})