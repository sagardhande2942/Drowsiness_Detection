from calendar import month
import re
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from driver.models import Driver
from Session.models import Session, Log

# Create your views here.


class ProfileSessionsHoursAPI(APIView):
    def get(self, request):
        user = request.user
        driver = Driver.objects.get(user=user)
        session_qs = Session.objects.filter(user=driver)
        total_hours = 0
        for obj in session_qs:
            total_hours += abs(float(obj.hours))
            total_hours = round(total_hours, 2)
        
        return Response({"hours":total_hours, "total_sessions":len(session_qs)})


class ProfileRatingAPI(APIView):
    def get(self, request):
        pass

class ProfileSessionListAPI(APIView):
    def get(self,request):
        user = request.user
        driver = Driver.objects.get(user=user)
        session_qs = Session.objects.filter(user=driver)[:5]
        outer_list = []
        for session_instance in session_qs:
            log_qs = Log.objects.filter(session=session_instance)
            inner_dict = {
                "start_time":session_instance.start_time,
                "end_time":session_instance.end_time,
                "duration": session_instance.hours
            }
            drowsy, speaking, distracted = 0, 0, 0
            for log_instance in log_qs:
                type = log_instance.type
                if type == "0":
                    drowsy+=1
                elif type == "1":
                    distracted+=1
                else: speaking+=1
            
            inner_dict['Drowsy'], inner_dict['Distracted'], inner_dict['Speaking'] = drowsy, distracted, speaking
            outer_list.append(inner_dict)
        
        return Response(outer_list)

class ProfileSessionHoursGraphAPI(APIView):
    def get(self, request):
        user = request.user
        driver = Driver.objects.get(user=user)
        session_qs = Session.objects.filter(user=driver)
        outer_dict = {}
        for session_instance in session_qs:
            month_date = session_instance.start_time
            month_date = month_date.strftime("%m")
            if month_date in outer_dict.keys():
                outer_dict[month_date]["sessions"]+=1
                outer_dict[month_date]["hours"]+=float(session_instance.hours)
                outer_dict[month_date]["hours"] = round(outer_dict[month_date]["hours"], 2)
            else:
                outer_dict[month_date] = {
                    "sessions":1,
                    "hours":float(session_instance.hours)
                }
                outer_dict[month_date]["hours"] = round(outer_dict[month_date]["hours"], 2)
        return Response(outer_dict)


class DashboardAllCountAPI(APIView):
    def get(self, request):
        user = request.user
        driver = Driver.objects.get(user=user)
        session_qs = Session.objects.filter(user=driver)
        outer_dict = {
            "Drowsy":0,
            "Speaking":0,
            "Distracted":0,
            "Total": 0
        }
        for session_instance in session_qs:
            log_qs = Log.objects.filter(session=session_instance)
            for log_instance in log_qs:
                if log_instance.type == "0":
                    outer_dict['Drowsy']+=1
                elif log_instance.type == "1":
                    outer_dict['Distracted']+=1
                else: outer_dict['Speaking']+=1

        outer_dict['Total'] = outer_dict['Drowsy'] + outer_dict['Distracted'] + outer_dict['Speaking']
        return Response(outer_dict)


class DashboardErrorGraphAPI(APIView):
    def get(self, request):
        user = request.user
        driver = Driver.objects.get(user=user)
        session_qs = Session.objects.filter(user=driver)
        outer_dict = {}
        for session_instance in session_qs:
            log_qs = Log.objects.filter(session = session_instance)
            for log_instance in log_qs:
                months_date = log_instance.timestamp
                months_date = months_date.strftime("%m")
                if months_date in outer_dict.keys():
                    if log_instance.type == "0":
                        outer_dict[months_date]['Drowsy'] += 1
                    elif log_instance.type == "1":
                        outer_dict[months_date]['Distracted'] += 1
                    else: outer_dict[months_date]['Speaking'] += 1
                else:

                    outer_dict[months_date] = {
                        "Drowsy":0,
                        "Distracted":0,
                        "Speaking":0
                    }

                    if log_instance.type == "0":
                        outer_dict[months_date]['Drowsy'] += 1
                    elif log_instance.type == "1":
                        outer_dict[months_date]['Distracted'] += 1
                    else: outer_dict[months_date]['Speaking'] += 1
        
        return Response(outer_dict)