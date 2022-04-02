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

session1 = Recipe(Session, hours=2)
session2 = Recipe(Session, hours=3)

user = Recipe(User,
            username = "John")

driver = Recipe(Driver,
            user = foreign_key(user),
            session_set = related('session1', 'session2'))