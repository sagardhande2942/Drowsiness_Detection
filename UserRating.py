import pandas as pd
import numpy as np
from firebase_admin import db
import speech_recognition as sr
from gtts.tts import gTTS
from playsound import playsound
import firebase_authentication

import os

recognizer = sr.Recognizer()
given_username = ""

def speak(filename, msg):
    tts = gTTS("{}".format("{}".format(msg)))
    tts.save('{}.mp3'.format(filename))
    playsound('{}.mp3'.format(filename))
    os.remove('{}.mp3'.format(filename))

def take_username():
    global given_username

    username_ref = db.reference('Username/')
    users = username_ref.get()

    recognizer = sr.Recognizer()
    

    with sr.Microphone() as source:
        while True:
            try:
                speak("ask_username", "Hello, what is your username?")
                uname = recognizer.record(source, duration=5)
                given_username = recognizer.recognize_google(uname)
                given_username = given_username.lower()
                given_username = given_username.replace(" ", "")
                print("Given Username : ", str(given_username))
                speak("confirm_username", "Is your username, {}, Please say ok to confirm".format(
                    given_username))
                confirm_username = recognizer.record(source, duration=5)
                confirm_username = recognizer.recognize_google(confirm_username)
                print("Confirm Text : ", str(confirm_username))
                name_exists = False
                if "ok" in confirm_username.lower() or "":
                    for key, user in users.items():
                        if user == given_username:
                            name_exists = True
                            break
                    if name_exists:
                        break
                    else:
                        continue
                else:
                    speak("try_again", "Please try again!")
            except Exception as e:
                if len(given_username.strip()) == 0:
                    speak("nameNotFound", "I didn't get that, please try again!")


take_username()

df = ""

try:
    df = pd.read_csv("{}.csv".format(given_username)) 
except:
    speak("ask_username", "Not enough data available, please try again")
    exit()

weights = []

dict = {"User is drowsy": 10, "User is distracted Looking Right": 5, "User is distracted Looking Left": 5, "No face detected": 0,
"User is Speaking or talking on phone please focus on road" : 2}

for i in df['Message']:
    i = i.strip()
    print(i)
    if i == "User is drowsy":
        weights.append(dict[i])
    elif i == "User is distracted Looking Right":
        weights.append(dict[i])
    elif i == "User is distracted Looking Left":
        weights.append(dict[i])
    elif i == "No face detected":
        weights.append(dict[i])
    elif i == "User is Speaking or talking on phone please focus on road":
        weights.append(dict[i])
    else:
        weights.append("")

print(weights)
df['Weights'] = weights

check = False
index = 0
global_timestamp = ""

for i in df['Message']: 
    # print(index)
    i = i.strip()
    if i == "User is drowsy":
        if check:
            # print(global_timestamp)
            # print(df.iloc[index]['Timestamp'][:-2])
            if global_timestamp == df.iloc[index]['Timestamp'][:-2].strip():
                df = df.drop(df.index[index]) 
                index -= 1
        check = True
        global_timestamp = df.iloc[index]['Timestamp']
        global_timestamp = global_timestamp[:-2].strip()
    else:
        check = False
    index += 1

print(df)
# df.set_index("Sr No.")
df.to_csv("{}.csv".format(given_username), index=False)

df = pd.read_csv("{}.csv".format(given_username))

index = 0

for i in df["Name"]:
    if i.strip() == "NEW SESSION":
        df = df.drop(df.index[index])
        index -= 1
    index += 1
    
l = [i for i in range(df.shape[0])]

df['index'] = l

df['Sr No.'] = l


index = 0

for i in df["Message"]:
    if i.strip() == "No face detected":
        df = df.drop(df.index[index])
        index -= 1
    index += 1

df['Sr No.'] = index


Time = []
for i in df['Timestamp']:
    if len(i) == 16:
        Time.append(float(i[11:16].replace(":", ".")))
    else:
        Time.append(-1)
   
df['Time'] = Time

interval_weights = []

interval_start = 0
interval_end = 0

speak("ask_username", "Please specify the start time")
with sr.Microphone() as source:
    while True:
        speak("ask_username", "start hour")
        hour = recognizer.record(source, duration = 4)
        hour = recognizer.recognize_google(hour)
        hour = hour.replace(" ", "")
        try:
            hour = int(hour)
        except:
            speak("nameNotFound", "I didn't get that, please try again!")
            continue
        speak("ask_username", "start minutes")
        minutes = recognizer.record(source, duration = 4)
        minutes = recognizer.recognize_google(minutes)
        minutes = minutes.replace(" ", "")
        try:
            minutes = int(minutes)
        except:
            speak("nameNotFound", "I didn't get that, please try again!")
            continue
        interval_start = float(str(hour) + "." + str(minutes))
        break

speak("ask_username", "Please specify the end time")
with sr.Microphone() as source:
    while True:
        speak("ask_username", "end hour")
        hour = recognizer.record(source, duration = 4)
        hour = recognizer.recognize_google(hour)
        hour = hour.replace(" ", "")
        try:
                hour = int(hour)
        except:
            speak("nameNotFound", "I didn't get that, please try again!")
            continue
        speak("ask_username", "end minutes")
        minutes = recognizer.record(source, duration = 4)
        minutes = recognizer.recognize_google(minutes)
        minutes = minutes.replace(" ", "")
        try:
            minutes = int(minutes)
        except:
            speak("nameNotFound", "I didn't get that, please try again!")
            continue
        interval_end = float(str(hour) + "." + str(minutes))
        break

print(interval_start, interval_end)

check = False

for index, row in df.iterrows():
    if row['Time'] >= interval_start and row['Time'] <= interval_end:
        interval_weights.append(row['Weights'])
        check = True

        
if not check or interval_start >= interval_end:
    speak("ask_username", "There is not enough data available for this time range.")
    exit()
else:
    df["Weights"] = interval_weights

test_data = list(df["Weights"])

counter = 0
sum1 = 0
total_sum = 0

four_averages = []

if len(test_data) == 0:
    speak("ask_username", "Not Enough Data Available")

for i in range(len(test_data)):
    total_sum += test_data[i]
    sum1 = 0
    
    for j in range(4):
        if i + 4 > len(test_data):
            break
        sum1 += test_data[i + j]
    
    if sum1 >= 30:
        four_averages.append(sum1 / 4)
        
orig_rating = total_sum / len(test_data)
second_average = 0

if len(four_averages) > 0:
    sum1 = 0
    for i in four_averages:
        sum1 += i

    second_average = sum1 / len(four_averages)

final_rating = (orig_rating + second_average) / 2
final_rating = 10-final_rating    

print(final_rating / 2)
speak("ask_username", str("The efficiency rating of {} is".format(given_username)) + str(final_rating / 2))



