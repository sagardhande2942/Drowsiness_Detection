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

cred_obj = firebase_admin.credentials.Certificate('drowsinessdetection-c0493-firebase-adminsdk-qeyqj-74ccb3f0e6.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':'https://drowsinessdetection-c0493-default-rtdb.firebaseio.com/'
	})

username_ref = db.reference('Username/')
users = username_ref.get()

recognizer = sr.Recognizer()

def speak(filename, msg):
    tts = gTTS("{}".format("{}".format(msg)))
    tts.save('{}.mp3'.format(filename))
    playsound('{}.mp3'.format(filename))
    os.remove('{}.mp3'.format(filename))

with sr.Microphone() as source:
    while True:
        try:
            speak("ask_username", "Hello, what is your username?")
            uname = recognizer.record(source, duration=5)
            given_username = recognizer.recognize_google(uname)
            given_username = given_username.lower()
            given_username = given_username.replace(" ", "")
            print("Given Username : ", str(given_username))
            speak("confirm_username", "Is your username, {}, Please say ok to confirm".format(given_username))
            confirm_username = recognizer.record(source, duration=5)
            confirm_username = recognizer.recognize_google(confirm_username)
            print("Confirm Text : ", str(confirm_username))
            unique_checker = False
            if "ok" in confirm_username.lower() or "":
                for user in users:
                    if user == given_username:
                        speak("not_unique", "Sorry, this username is already taken, Please try again!")
                        unique_checker = True
                        break
                if unique_checker:
                    continue
                else:
                    break
            else:
                speak("try_again", "Please try again!")
        except Exception as e:
            if len(given_username.strip()) == 0:
                speak("nameNotFound", "I didn't get that, please try again!")


while True:
    camera = cv2.VideoCapture(0)

    speak("alert_for_photo", "Please align yourself facing to the camera")

    detector = dlib.get_frontal_face_detector()

    is_succesfull, image = camera.read()
    speak("photo_taken", "Photo Taken")

    if not is_succesfull:
        raise "Cannot read the camera feed"

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    rect = detector(gray, 1)

    camera.release()
    cv2.destroyAllWindows()

    if len(rect) == 0:
        speak("no_face", "Sorry, no face was detected, Please try again!")
        continue
    elif len(rect) > 1:
        speak("multiple_faces", "Sorry, multiple faces were detected, please make sure only your face is visible in the frame, Please try again!")
        continue
    else:
        break

print(rect[0])
x1 = rect[0].left()
x2 = rect[0].right()
y1 = rect[0].top()
y2 = rect[0].bottom()
print(x1, x2, y1, y2)

user_images_path = "user_images/"

write_success = cv2.imwrite('{}{}.jpg'.format(user_images_path, given_username), image)

if not write_success:
    raise "Image writting was not succesfull"

user_image_location = face_recognition.load_image_file('{}{}.jpg'.format(user_images_path, given_username))
user_image_encoding = face_recognition.face_encodings(user_image_location)[0]

for key, user in users.items():
    print(user)
    db_face_locations = face_recognition.load_image_file('{}{}.jpg'.format(user_images_path, user)) 
    db_face_encodings = face_recognition.face_encodings(db_face_locations)[0]

    match = face_recognition.face_distance([user_image_encoding], db_face_encodings)
    match = match[0]
    print(match)
    if match < 0.4:
        speak("no_unique", "Your face already exists in the system")
        os.remove('{}{}.jpg'.format(user_images_path, given_username))
        raise "Your face already exists in the system"

username_ref.push().set(given_username)

speak("registration_complete", "Thank You, Your registration is complete.")

