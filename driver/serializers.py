from dataclasses import field
from .models import Driver
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200)
    password = serializers.CharField(write_only=True, max_length=200)

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        User(username = validated_data['username'], password = validated_data['password']).save()
        x = User.objects.get(username=validated_data['username'])
        Driver(user=x).save()
        return validated_data


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']
        

class DriverDetailsSerializer(serializers.ModelSerializer):
    user = UserLoginSerializer()

    class Meta:
        model = Driver
        fields = '__all__'