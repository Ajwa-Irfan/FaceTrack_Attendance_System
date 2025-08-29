from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    """Decorator that checks if user is superuser (admin)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
