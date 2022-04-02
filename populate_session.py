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

fake = Faker() 
Faker.seed(2942)

DROWSY_PERCENTAGE = 0.25

logs = ""

message_choice = ["1", "2", "3", "4"]
type_choice = ["1", "2", "3"]

log1 = Recipe(Log)
log2 = Recipe(Log)
log3 = Recipe(Log)

session1 = Recipe(Session, hours=2, log_set=related('log1', 'log2'))
session2 = Recipe(Session, hours=3, log_set=related('log3'))

driver = Recipe(Driver,
        session_set = related('session1', 'session2'))

user = Recipe(User,
            username = "John",
            driver = foreign_key(driver, one_to_one=True))

user.make()


# session1 = baker.prepare(Session, user=driver)
# session2 = baker.prepare(Session, user=driver)
# baker.make_recipe('driver.driver')

# user = Recipe(User, username="John")
# driver = Recipe(Driver, user= foreign_key(user, one_to_one=True))
# session1 = Recipe(Session, user = foreign_key(driver), hours=3)
# session2 = Recipe(Session, user = foreign_key(driver), hours=2)
# session2.make()


for k in range(100):
    username = fake.name()
    username = username.replace(' ', '_')
    user=Recipe(User,
                    username=username,
                    password=username,)
    user.prepare()
    driver=Recipe(Driver,
                    user = foreign_key(user, one_to_one=True),
                    rating = random.randint(0, 5),
                    speed_limit = random.randint(50, 100),
                    )
    start_date = "01/01/22"
    taken_date = datetime.datetime.strptime(start_date, "%d/%m/%y")
    # newdate = taken_date + datetime.timedelta(days=1)

    days = (taken_date - datetime.datetime.now()).days
    days = -days
    for day in range(days):
        no_sessions = random.randint(0,10)
        if no_sessions:
            driver.prepare(_quantity=no_sessions)
        start_date = "01/01/22"
        taken_date = datetime.datetime.strptime(start_date, "%d/%m/%y")
        newdate = taken_date + datetime.timedelta(days=day)
        end_date = newdate + datetime.timedelta(days = 1)
        end_date = end_date - datetime.timedelta(minutes=1)

        times = [fake.date_time_between(taken_date, end_date) for _ in range(2*no_sessions)]
        datetime_index = 0
        for session_no in range(no_sessions):
            hours = mktime(times[datetime_index + 1].timetuple()) - mktime(times[datetime_index].timetuple())
            hours //= 3600
            session = Recipe(Session,
                        user= foreign_key(driver),
                        start_time = times[datetime_index],
                        end_time = times[datetime_index + 1],
                        hours=hours)
            no_logs = random.randint(0, 10)
            no_logs *= DROWSY_PERCENTAGE
            no_logs = int(no_logs)
            if no_logs:
                session.prepare(_quantity=no_logs)

            start_date = times[datetime_index]
            end_date = times[datetime_index + 1]
            end_date = end_date - datetime.timedelta(minutes=1)

            times_log = [fake.date_time_between(start_date, end_date) for _ in range(no_logs)]
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

                if message_index == 1:
                    type_index = 0
                elif message_index <= 3:
                    type_index = 1
                else: type_index = 2

                logs = Recipe(Log,
                            session=foreign_key(session),
                            timestamp = times_log[times_log_index],
                            message = message_choice[message_index],
                            type = type_choice[type_index])
                times_log_index += 1
                # logs.make()

        datetime_index += 2
    logs.make()
    # logs.make()