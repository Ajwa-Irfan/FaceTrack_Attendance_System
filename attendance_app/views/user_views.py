from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

@login_required
def user_dashboard(request):
    return render(request, 'attendance_app/user_dashboard.html')

@csrf_exempt
def scan_attendance_page(request):
    return render(request, 'attendance_app/scan_attendance.html')