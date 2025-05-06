from django.shortcuts import render, redirect
from django.http import HttpResponse,  HttpResponseRedirect
from django.urls import path, include
from tenants.models import TenantDomain

def start(request):
    return HttpResponse("This is in building phase")

EXCLUDED_DOMAINS = ['super.localhost', 'localhost', '127.0.0.1']

def domain_based_redirect(request):
    try:
        host = request.get_host().split(':')[0]  # Remove port if present
        print(f"Host: {host}")

        # ✅ 1. Handle excluded/public domains FIRST
        if host in EXCLUDED_DOMAINS:
            if host == 'super.localhost':
                print("Redirecting to super from public domain")
                return redirect('/super/')
            else:
                print("Redirecting to public landing")
                return redirect('/public/')  # optional public landing

        # ✅ 2. If not public, proceed with subdomain-based logic
        subdomain = host.split('.')[0]
        print(f"Subdomain: {subdomain}")

        print("Registered domains:", list(TenantDomain.objects.values_list('domain', flat=True)))

        tenant_domain = TenantDomain.objects.filter(domain=host).first()
        if tenant_domain:
            if subdomain == 'super':
                print("Redirecting to super (shouldn't reach here)")
                return redirect('/super/')
            else:
                print("Redirecting to director")
                return redirect('/director/')
        else:
            return HttpResponse("This domain is not registered with CollegeSync.", status=404)

    except Exception as e:
        print(f"Error in domain_based_redirect: {e}")
        return HttpResponse("An internal error occurred.", status=500)