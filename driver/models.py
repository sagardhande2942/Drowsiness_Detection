import email
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
# Create your models here.

alarm_choice = [
    ("0", "xx"),
    ("1", "22"),
    ("2", "33")
]

class Driver(models.Model):
    # id = models.AutoField(primary_key=True, default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    photo_url = models.CharField(max_length=200, null=True, blank=True)
    rating = models.CharField(max_length=200, null=True, blank=True)
    speed_limit = models.IntegerField(blank=True, null=True)
    alarm_sound = models.CharField(max_length=200,blank=True,null=True ,choices=alarm_choice, default="0")
    alarm_sound1 = models.CharField(max_length=200,blank=True,null=True ,choices=alarm_choice, default="0")

    def __str__(self):
        return self.user.username
    # rating, speedlimit, alarm_sound, 

    # Session: start_time, end_time, log(table), hours

