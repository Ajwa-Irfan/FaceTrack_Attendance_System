import os
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout

def login_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(email=email, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
    return render(request, 'attendance_app/auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')