from unicodedata import name
from django.urls import path
from Session import views

urlpatterns = [
    path('<int:pk>/get_total_hours_sessions/', views.ProfileSessionsHoursAPI.as_view(), name="TotalHours"),
    path('<int:pk>/get_session_details/', views.ProfileSessionListAPI.as_view(), name="ProfileSessionDetails"),
    path('<int:pk>/get_session_hours/', views.ProfileSessionHoursGraphAPI.as_view(), name="ProfileSessionHoursGraph"),
    path('<int:pk>/get_count_all/', views.DashboardAllCountAPI.as_view(), name="DashboardAllCountAPI"),
    path('<int:pk>/get_dashboard_error_graph/', views.DashboardErrorGraphAPI.as_view(), name="DashboardErrorGraph"),
    path('<int:pk>/get_rating_rank/', views.ProfileRatingRankAPI.as_view(), name="ProfileRatingRank"),
    path('<int:pk>/get_leaderboard/', views.ProfileLeaderboardAPI.as_view(), name="ProfileLeaderboard"),
]