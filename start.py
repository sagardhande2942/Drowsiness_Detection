import cv2
import dlib
from firebase_admin import db
import firebase_admin
import speech_recognition as sr
from playsound import playsound
import os
from gtts.tts import gTTS
import face_recognition
import numpy as np
import firebase_authentication
from PIL import Image
import login_user
import register_user

recognizer = sr.Recognizer()


def speak(filename, msg):
    tts = gTTS("{}".format("{}".format(msg)))
    tts.save('{}.mp3'.format(filename))
    playsound('{}.mp3'.format(filename))
    os.remove('{}.mp3'.format(filename))

recognize_decision = ""

with sr.Microphone() as source:
     while True:
        try:
            speak("ask_login_register", "Hello, do you want to login or register?, say yes for login and no for register.")
            decision = recognizer.record(source, duration=3)
            recognize_decision = recognizer.recognize_google(decision)
            recognize_decision = recognize_decision.lower()
            recognize_decision = recognize_decision.replace(" ", "")
            if "yes" in recognize_decision:
                login_user.login_user()
                break
            elif "no" in recognize_decision:
                register_user.register_user()
                break
            else:
                speak("try_again", "please try again")
        except Exception as e:
            if len(recognize_decision.strip()) == 0:
                speak("no_decision", "I didn't get that, please try again!")

            print(e)
