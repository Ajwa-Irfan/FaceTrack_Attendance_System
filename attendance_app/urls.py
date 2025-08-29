from django.urls import path
from .views.auth import *
from .views.admin_views import *
from .views.api_views import *
from .views.attendance_views import *
from .views.file_views import *
from .views.user_views import *

urlpatterns = [
    #API URLS
    path('api/login/', LoginView.as_view()),
    path('api/members/', MemberCreateView.as_view()),
    path('api/recognize-face/', FaceRecognitionView.as_view()),
    path('api/attendance/today/', TodayAttendanceView.as_view()),
    path('api/attendance/live/', LiveAttendanceView.as_view()),
    path('api/logs/', RecognitionLogListView.as_view()),

    #AUTH URLS
    path('login/', login_page, name='login'),
    path('logout/', logout_view, name='logout'),

    #ADMIN URLS
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    path('dashboard/admin/live-display/', live_display_page, name='live_display'),
    path('dashboard/admin/add-member/', add_member_page, name='add_member'),
    path('dashboard/admin/today-attendance/', today_attendance_page, name='today_attendance'),
    path('dashboard/admin/logs/', logs_page, name='logs'),
    path("employees/", employee_list, name="employee_list"),

    #USER URLS
    path('dashboard/user/', user_dashboard, name='user_dashboard'),
    path('scan-attendance/', scan_attendance_page, name='scan_attendance'),
    path("employees/<int:member_id>/yearly/", yearly_attendance, name="yearly_attendance"),

    #FILE URLS
    path('secure-face/<str:filename>/', serve_protected_face, name='secure_face'),
]