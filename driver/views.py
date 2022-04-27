from tabnanny import check
from telnetlib import STATUS
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from driver.models import Driver
from .serializers import DriverDetailsSerializer,  UserLoginSerializer, UserRegisterSerializer
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.hashers import check_password
from django.views import View
from django.views.generic import ListView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from driver import serializers
# Create your views here.

User = get_user_model()

class UserListView(generics.ListAPIView):
    serializer_class = DriverDetailsSerializer
    queryset = Driver.objects.all()

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()


class UserLoginView(APIView): 
    def post(self, request):
        user_data_instance = UserRegisterSerializer(data = request.data)
        if user_data_instance.is_valid(raise_exception=True):
            username_check = UserLoginSerializer(data=request.data)
            user_data_instance = user_data_instance.data
            if not username_check.is_valid():
                print(request.data)
                user = User.objects.get(username = request.data['username'])
                if not user.check_password(request.data['password']):
                    return HttpResponse('Password Incorrect', status=404)
                else:
                    user = authenticate(username = request.data['username'], password = request.data['password'])
                    if user is not None:
                        login(request, user)
                    else:
                        return HttpResponse('Falied to authenticate', status=404)
                    user = User.objects.get(username=request.data['username'])
                    driver = Driver.objects.get(user=user)
                    outer_dict = {}
                    outer_dict['User'] = user.__dict__
                    outer_dict['User']['_state'] = ''
                    outer_dict['Driver'] = driver.__dict__
                    outer_dict['Driver']['_state'] = ""
                    print(outer_dict)
                    return Response(outer_dict, status=200)
            else:
                return HttpResponse('Username does not exist', status=404)

        return Response(user_data_instance.data)
    
    def get(self, request):
        return HttpResponse("Only Post", status=404)


class UserLogoutAPI(APIView):
    def get(self, request, pk=None):
        user = User.objects.filter(id=pk)
        if user.exists():
        # logout(request)
            return Response({"Message": "Success"})
        else:
            return HttpResponse("Invalid PK", status="404")



class UserEditAPI(APIView):
    def post(self, request, pk=None):
        user = User.objects.filter(id=pk)
        if user.exists():
            user = User.objects.filter(pk=pk)
            user.update(**request.data)
           
            return Response(request.data)
        else:
            return HttpResponse("Invalid PK", status="404")


class DriverEditAPI(APIView):
    def post(self, request, pk=None):
        user = User.objects.filter(id=pk)
        if user.exists():
            user = User.objects.get(id=pk)
            driver = Driver.objects.filter(user=user)
            driver.update(**request.data)
            return Response(request.data)
        else:
            return HttpResponse("Invalid PK", status="404")
        