from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from .models import College 
from tenants.models import TenantDomain, Tenant
from django_tenants.utils import get_tenant_model, get_public_schema_name
from datetime import datetime
from .forms import CollegeForm
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.

def main(request):
    # return HttpResponse("super")
    return render(request, 'super/main.html')

def open_create(request):
    return render(request, 'super/create.html')

def create(request):
    if request.method == "POST":
        # Retrieve and clean form data
        schema_name = request.POST.get('schema_name', '').strip()
        domain = request.POST.get('domain', '').strip()
        institute_name = request.POST.get('institute_name', '').strip()
        institute_address = request.POST.get('institute_address', '').strip()
        institute_email = request.POST.get('institute_email', '').strip()
        institute_number = request.POST.get('institute_number', '').strip()

        admin_name = request.POST.get('admin_name', '').strip()
        admin_number = request.POST.get('admin_number', '').strip()
        admin_email = request.POST.get('admin_email', '').strip()
        admin_username = request.POST.get('admin_username', '').strip()
        admin_password = request.POST.get('admin_password')
        confirm_password = request.POST.get('confirm_password')

        # Handle trial and paid_until
        paid_until = request.POST.get('paid_until')
        on_trial = request.POST.get('on_trial') == 'True'

        if paid_until:
            try:
                paid_until = datetime.strptime(paid_until, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format for paid_until (expected YYYY-MM-DD).")
                return redirect('open_create')
        else:
            paid_until = None

        # Check for duplicates and validation
        if College.objects.filter(admin_username=admin_username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('open_create')

        if Tenant.objects.filter(schema_name=schema_name).exists():
            messages.error(request, 'Schema already exists!')
            return redirect('open_create')

        if admin_password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('open_create')

        # Attempt to create tenant and domain
        try:
            tenant = Tenant.objects.create(
                schema_name=schema_name,
                name=institute_name,
                paid_until=paid_until,
                on_trial=on_trial,
            )
            TenantDomain.objects.create(
                domain=domain,
                tenant=tenant,
                is_primary=True
            )
        except Exception as e:
            messages.error(request, f"Failed to create tenant: {str(e)}")
            return redirect('open_create')

        # Save College record only if tenant creation succeeds
        College.objects.create(
            schema_name=schema_name,
            domain=domain,
            institute_name=institute_name,
            institute_address=institute_address,
            institute_email=institute_email,
            institute_number=institute_number,
            admin_name=admin_name,
            admin_number=admin_number,
            admin_email=admin_email,
            admin_username=admin_username,
            admin_password=make_password(admin_password),
            paid_until=paid_until,
            on_trial=on_trial,
        )

        messages.success(request, "College created successfully!")
        return redirect('view')

    return HttpResponse("User not created")

    


def view(request):
    colleges = College.objects.all()
    return render(request, 'super/view.html', {'colleges': colleges})

def manage(request, college_id):
    # Retrieve the college object from the database
    college = get_object_or_404(College, id=college_id)

    if request.method == 'POST':
        # Get the form data from the request
        college.institute_name = request.POST.get('institute_name')
        college.institute_address = request.POST.get('institute_address')
        college.institute_email = request.POST.get('institute_email')
        college.institute_number = request.POST.get('institute_number')
        college.admin_name = request.POST.get('admin_name')
        college.admin_number = request.POST.get('admin_number')
        college.admin_email = request.POST.get('admin_email')
        college.admin_username = request.POST.get('admin_username')
        # college.domain = request.POST.get('domain')

        # Update on_trial status (checkbox)
        on_trial_value = request.POST.get('on_trial', 'False')
        college.on_trial = on_trial_value == 'True'

        # Update paid_until date
        college.paid_until = request.POST.get('paid_until')

        newAdmin_password = request.POST.get('admin_password')
        newConfirm_password = request.POST.get('confirm_password')

        if newAdmin_password or newConfirm_password:
            if newAdmin_password == newConfirm_password:
                # Hash and assign the new password directly
                college.admin_password = make_password(newAdmin_password)
            else:
                messages.error(request, "Passwords do not match.")
                return render(request, 'super/manage.html', {'college': college})

        # Save the changes to the college object
        college.save()

        # Now we need to update the corresponding tenant in the tenant schema
        try:
            # Fetch the tenant schema using the schema_name from tenants.models
            tenant = Tenant.objects.get(schema_name=college.schema_name)
            
            # Update the tenant schema with the new values from the form
            tenant.on_trial = college.on_trial
            tenant.paid_until = college.paid_until
            tenant.save()

        except Tenant.DoesNotExist:
            messages.error(request, "Tenant schema not found.")
        
        # Display a success message and redirect
        messages.success(request, "College details and tenant schema updated successfully!")
        return redirect('view')  # Redirect to the page where colleges are listed

    return render(request, 'super/manage.html', {'college': college})

def manage_college(request, college_id):
    college = get_object_or_404(College, id=college_id)
    return render(request, 'super/manage.html', {'college': college})

def delete_college(request, college_id):
    college = get_object_or_404(College, id=college_id)
    schema_name = college.schema_name
    institute_name = college.institute_name

    try:
        # Delete the tenant schema
        tenant = Tenant.objects.get(schema_name=schema_name)
        tenant.delete(force_drop=True)  # This drops the schema

        # Delete the college record from the public schema
        college.delete()

        messages.success(
            request,
            f"College '{institute_name}' deleted successfully (Schema: '{schema_name}')."
        )
    except Tenant.DoesNotExist:
        messages.error(request, f"Tenant with schema '{schema_name}' not found.")
    except Exception as e:
        messages.error(request, f"Failed to delete college: {e}")
    return redirect('view')  # or your view page's URL name