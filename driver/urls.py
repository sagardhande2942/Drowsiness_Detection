from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserCreateView.as_view(), name='Register'),
    path('login/', views.UserLoginView.as_view(), name='Login'),
    path('list/',views.UserListView.as_view(), name='List'),
    path('logout/', views.UserLogoutAPI.as_view(), name='Logout'),
]