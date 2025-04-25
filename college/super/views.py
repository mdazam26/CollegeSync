from django.shortcuts import render, redirect
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
            return HttpResponse("Username already exits")

        if admin_password != confirm_password:
            return HttpResponse("Password do not match")

        College.objects.create(
            institute_name = institute_name,
            institute_address = institute_address,
            institute_email = institute_email,
            institute_number = institute_number,

            admin_name = admin_name,
            admin_number = admin_number,
            admin_email = admin_email,
            admin_username = admin_username,
            admin_password = admin_password,
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

def manage(request):
    return render(request, 'super/manage.html')