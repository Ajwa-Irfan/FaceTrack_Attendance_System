import datetime
from attendance_app.models import *
import face_recognition, cv2, pickle, datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime, time, timedelta
from django.utils.timezone import localtime
from ..utils.decorators import admin_required
from django.contrib.auth.decorators import login_required

@login_required
@admin_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('user_dashboard')
    member = Member.objects.all()
    return render(request, 'attendance_app/admin/admin_dashboard.html', {'members':member})


@admin_required
def add_member_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        image = request.FILES.get('face_file')

        if name and email and image:
            # Process image for face encoding
            img = face_recognition.load_image_file(image)
            encodings = face_recognition.face_encodings(img)

            if encodings:
                encoding = encodings[0]
                # Save member
                member = Member(
                    name=name,
                    email=email,
                    face_file=image,
                    encoding=pickle.dumps(encoding)
                )
                member.save()
                return HttpResponse("1") 
            else:
                return HttpResponse("no_face")  
        else:
            return HttpResponse("missing_field") 

    return render(request, 'attendance_app/admin/add_member.html')

def today_attendance_page(request):
    return render(request, 'attendance_app/admin/today_attendance.html')

def logs_page(request):
    return render(request, 'attendance_app/admin/logs.html')

def employee_list(request):
    today = datetime.today().date()
    employees = Member.objects.all()
    data = []

    checkin_time = time(11, 0)   # 12:00 PM
    checkout_time = time(16, 0)  # 04:00 PM
    grace = timedelta(minutes=30)

    for emp in employees:
        record = Attendance.objects.filter(member=emp, date=today).first()

        status = "absent"
        today_check_in = None
        today_check_out = None

        if record:
            if record.check_in:
                today_check_in = localtime(record.check_in).strftime("%H:%M")
                in_time = record.check_in.time()
                if in_time < (datetime.combine(today, checkin_time) - grace).time():
                    status = "early_in"
                elif abs(datetime.combine(today, in_time) - datetime.combine(today, checkin_time)) <= grace:
                    status = "on_time"
                else:
                    status = "late_in"

            if record.check_out:
                today_check_out = localtime(record.check_out).strftime("%H:%M")
                out_time = record.check_out.time()
                if out_time < (datetime.combine(today, checkout_time) - grace).time():
                    status = "early_out"
                else:
                    status = "valid_out"

        data.append({
            "id": emp.id,
            "name": emp.name,
            "today_check_in": today_check_in,
            "today_check_out": today_check_out,
            "status": status
        })

    return render(request, "attendance_app/admin/employee_list.html", {"employees": data})

def live_display_page(request):
    return render(request, 'attendance_app/admin/live_display.html')

from django.utils.timezone import now
from attendance_app.models import Member, Attendance
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def dashboard_stats(request):
    today = now().date()

    total_employees = Member.objects.count()
    present = Attendance.objects.filter(date = today, status = "Present").count()
    absent = total_employees-present
    late = Attendance.objects.filter(date = today, status = "Present").count()
    leave = Attendance.objects.filter(date = today, status = "Present").count()

    data = {
        'total_employees' : total_employees,
        'present' : present,
        'absent': absent,
        'leave': leave,
        'late': late
    }
    
    return Response(data)
