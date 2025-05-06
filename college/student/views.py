from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import path, include
from tenants.models import TenantDomain

# Create your views here.
def index(request):
    return render(request, 'student/index.html')

def create_student_form(request):
    return HttpResponse("Create Student Form Page")

def create_student(request):
    return HttpResponse("Student Creation Logic Handler")

def view_student(request):
    return HttpResponse("View All Students Page")

def goto_manage_student(request, student_id):
    return HttpResponse(f"Redirecting to manage student with ID: {student_id}")

def manage_student(request, student_id):
    return HttpResponse(f"Manage Student Page for ID: {student_id}")

def delete_student(request, student_id):
    return HttpResponse(f"Delete Student with ID: {student_id}")