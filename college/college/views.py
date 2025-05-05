from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import path, include


def start(request):
    return HttpResponse("This is in building phase")


def domain_based_redirect(request):
    try:
        host = request.get_host()
        print(f"Host: {host}")

        if host.startswith("localhost"):
            return redirect('/public/')  # Redirect to a path served by public.urls

        if '.' in host:
            subdomain = host.split('.')[0]

            if subdomain in ['test1', 'macet', 'super']:
                return redirect('/director/')  # Redirect to a path served by director.urls

        return HttpResponse("Invalid domain", status=404)

    except Exception as e:
        print(f"Error in domain_based_redirect: {e}")
        return HttpResponse("An error occurred while processing the domain.", status=500)