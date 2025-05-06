from django.shortcuts import render, redirect
from django.http import HttpResponse

def index(request):
    return render(request, 'public/index.html')

def tenant_form(request):
    return render(request, 'public/tenant_form.html')

def go_to_tenant(request):
    if request.method == "POST":
        subdomain = request.POST.get('subdomain', '').strip()
        
        # Validate subdomain and redirect
        if subdomain:
            # If the subdomain is valid (add more subdomains if needed)
            valid_subdomains = ['test1', 'macet', 'super']  # Adjust based on your needs
            if subdomain in valid_subdomains:
                # Redirect to the correct subdomain (e.g., test1.localhost:8000)
                return redirect(f'http://{subdomain}.localhost:8000/')
            else:
                return HttpResponse("Invalid subdomain.", status=400)
        else:
            return HttpResponse("Please enter a valid subdomain.", status=400)
    # If it's a GET request, render the form
    return render(request, 'index.html') 


# def domain_based_redirect(request):
#     host = request.get_host().split(':')[0]  
#     if host == 'super.localhost':
#         return redirect('/super/')
#     return redirect('/public/')