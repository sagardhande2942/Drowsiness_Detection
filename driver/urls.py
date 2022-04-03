from unicodedata import name
from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register/', views.UserCreateView.as_view(), name='Register'),
    path('login/', csrf_exempt(views.UserLoginView.as_view()), name='Login'),
    path('list/',views.UserListView.as_view(), name='List'),
    path('logout/', views.UserLogoutAPI.as_view(), name='Logout'),
    path('user_edit/', csrf_exempt(views.UserEditAPI.as_view()), name="UserEditAPI"),
    path('driver_edit/', csrf_exempt(views.DriverEditAPI.as_view()), name="UserEditAPI"),
]