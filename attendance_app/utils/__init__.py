# attendance_app/utils/__init__.py
from .decorators import admin_required

# This makes the decorators available when importing from the utils package
__all__ = [
    'admin_required',
]