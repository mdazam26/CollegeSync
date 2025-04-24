from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password


from .forms import CollegeForm
from django.contrib import messages
# Create your views here.

def main(request):
    return render(request, 'super/main.html')

def create(request):
    if request.method == 'POST':
        form = CollegeForm(request.POST)
        if form.is_valid():
            # Save the form data and create a new College instance
            college = form.save(commit=False)
            # Optionally, you can add any custom behavior like encrypting passwords here
            college.admin_password = make_password(college.admin_password)

            college.save()  # Save the college instance to the database
            
            messages.success(request, "College created successfully!")  # Add a success message
            return redirect('view')  # Redirect to a page that shows the created college(s)
        else:
            messages.error(request, "There was an error with your form submission.")  # Add an error message
    else:
        form = CollegeForm()  # Initialize the form if the request is GET

    return render(request, 'super/create.html', {'form': form})

def view(request):
    return render(request, 'super/view.html')

def manage(request):
    return render(request, 'super/manage.html')