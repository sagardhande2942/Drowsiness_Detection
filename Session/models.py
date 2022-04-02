from turtle import ondrag
from django.db import models
from driver.models import Driver
# Create your models here.

message_choice = [
    ("1", "Drowsy"),
    ("2", "Left"),
    ("3", "Right"),
    ("4", "Speaking")
]

class Session(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('driver.Driver', on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    hours = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f'{self.id} {self.user}'

class Log(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(null=True, blank=True)
    message = models.CharField(max_length=200,blank=True,null=True , choices=message_choice)
    type = models.CharField(max_length=200,blank=True,null=True , choices=[("0", "Drowsiness"), ("1", "Distraction_1"), ("2", "Distraction_2")])

    def __str__(self):
        return f'{self.id} {self.message}'