from msilib.schema import RemoveIniFile
import os 
import random
from time import mktime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DrowsyBackend.settings")

import django 
django.setup() 

from faker import factory,Faker 
from driver.models import * 
from Session.models import * 
from model_bakery.recipe import Recipe,foreign_key , baker, related
import datetime
from random import randrange
fake = Faker() 
Faker.seed(2942)
from datetime import timedelta
DROWSY_PERCENTAGE = 0.40

logs = ""

message_choice = ["1", "2", "3", "4"]
type_choice = ["0", "1", "2"]


start_date = "1/01/22"
# taken_date = datetime.datetime.strptime(start_date, "%d/%m/%y")
# newdate = taken_date + datetime.timedelta(days=1)
# print(newdate)

# taken_date = datetime.datetime.strptime(start_date, "%d/%m/%y")
# newdate = taken_date + datetime.timedelta(days=1)
# end_date = newdate + datetime.timedelta(days = 1)
# end_date = end_date - datetime.timedelta(days = 1, minutes=1)
# print([taken_date, end_date])
# times = [fake.date_time_between(taken_date, end_date) for _ in range(50)]
# times.sort()
# for i in times:
#     print(i.strftime('%X'))


def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    try:
        random_second = randrange(int_delta)
    except:
        random_second = 0
    return start + timedelta(seconds=random_second)

for k in range(30):
    username = fake.name()
    first_name = username.split(' ')[0]
    last_name = username.split(' ')[1]
    username = username.replace(' ', '_')
    username = username.lower()
    user=User( username=username,
                    first_name = first_name,
                    last_name = last_name)
    user.set_password(username)
    user.save()
    driver=Driver(
                    user = user,
                    rating = random.randint(0, 5),
                    speed_limit = random.randint(50, 100),
                    photo_url = 'https://source.unsplash.com/user/c_v_r/1600x900',
                    )
    driver.save()
    start_date = "01/04/21"
    taken_date = datetime.datetime.strptime(start_date, "%d/%m/%y")
    # newdate = taken_date + datetime.timedelta(days=1)

    days = (taken_date - datetime.datetime.now()).days
    days = -days
    for day in range(days):
        no_sessions = random.randint(0,5)
        taken_date = datetime.datetime.strptime(start_date, "%d/%m/%y")
        newdate = taken_date + datetime.timedelta(days=day)
        # print(newdate.strftime("%x"))
        end_date = newdate + datetime.timedelta(days = 1)
        end_date = end_date - datetime.timedelta(minutes=1)
        # print(end_date)
        times = [random_date(newdate, end_date) for _ in range(2*no_sessions)]
        times.sort()
        datetime_index = 0
        for session_no in range(no_sessions):
            hours = mktime(times[datetime_index + 1].timetuple()) - mktime(times[datetime_index].timetuple())
            hours /= 3600
            hours = abs(hours)
            hours = str(hours)[:4]
            session = Session(
                        user = driver,
                        start_time = times[datetime_index],
                        end_time = times[datetime_index + 1],
                        hours=hours)
            session.save()
            no_logs = random.randint(0, 10)
            no_logs *= DROWSY_PERCENTAGE
            no_logs = int(no_logs)

            start_date1 = times[datetime_index]
            end_date = times[datetime_index + 1]
            end_date = end_date - datetime.timedelta(minutes=1)

            times_log = [random_date(start_date1, end_date) for _ in range(no_logs)]
            times_log.sort()

            times_log_index = 0
            for log in range(no_logs):
                message_index = -1
                type_index = -1
                error_prob = random.randint(0,140)

                if error_prob < 20:
                    message_index = 0
                elif error_prob < 60:
                    message_index = 1
                elif error_prob < 100:
                    message_index = 2
                elif error_prob < 140:
                    message_index = 3

                if message_index == 0:
                    type_index = 0
                elif message_index <= 2:
                    type_index = 1
                else: type_index = 2

                logs = Log(
                            session=session,
                            timestamp = times_log[times_log_index],
                            message = message_choice[message_index],
                            type = type_choice[type_index])
                logs.save()
                times_log_index += 1

            datetime_index += 2