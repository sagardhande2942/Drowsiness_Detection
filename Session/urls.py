from unicodedata import name
from django.urls import path
from Session import views

urlpatterns = [
    path('get_total_hours_sessions/', views.ProfileSessionsHoursAPI.as_view(), name="TotalHours"),
    path('get_session_details/', views.ProfileSessionListAPI.as_view(), name="ProfileSessionDetails"),
    path('get_session_hours/', views.ProfileSessionHoursGraphAPI.as_view(), name="ProfileSessionHoursGraph"),
    path('get_count_all/', views.DashboardAllCountAPI.as_view(), name="DashboardAllCountAPI"),
    path('get_dashboard_error_graph/', views.DashboardErrorGraphAPI.as_view(), name="DashboardErrorGraph"),
]