import os 
import random
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DrowsyBackend.settings")

import django 
django.setup() 

from faker import factory,Faker 
from driver.models import * 
from model_bakery.recipe import Recipe,foreign_key 

fake = Faker() 
Faker.seed(2942)

for k in range(100):
    username = fake.name()
    username = username.replace(' ', '_')
    user=Recipe(User,
                username=username,
                password=username,)
  
    driver=Recipe(Driver,
                    user = foreign_key(user),
                    rating = random.randint(0, 5),
                    speed_limit = random.randint(50, 100),
                    )
    
    driver.make()