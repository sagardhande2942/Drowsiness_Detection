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
import usingOnlyEye


def speak(filename, msg):
    tts = gTTS("{}".format("{}".format(msg)))
    tts.save('{}.mp3'.format(filename))
    playsound('{}.mp3'.format(filename))
    os.remove('{}.mp3'.format(filename))



def login_user():

    username_ref = db.reference('Username/')
    users = username_ref.get()

    recognizer = sr.Recognizer()
    
    given_username = ""

    user_images_path = "user_images/"
    # for temporarily saving images at the time of logging
    login_images_path = "user_login_images/"

    multiple_faces = False

    loggedIn = False  # user is looged in or not

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
        if  len(rect) > 1:
            print("in multiple faces")
            multiple_faces = True
            temp_image = "temp_image"

            #image with multiple faces
            img_captured = cv2.imwrite('{}{}.jpg'.format(login_images_path, temp_image), image)  

            if not img_captured:
                print("storing image failed")

            user_image_location = face_recognition.load_image_file('{}{}.jpg'.format(user_images_path, given_username))
            user_image_encoding = face_recognition.face_encodings(user_image_location)[0]

            #captured image location
            cap_image_location = face_recognition.load_image_file('{}{}.jpg'.format(login_images_path, temp_image))
                
            # array of locations of all faces in captured image
            cap_image_encoding = face_recognition.face_locations(cap_image_location)
            
            for face_location in cap_image_encoding:
            
                top, right, bottom, left = face_location
                face_image = cap_image_location[top:bottom,left:right]
                pil_image = Image.fromarray(face_image)

                # image of a single face in captured photo
                pil_image.save(login_images_path+"cropped.jpg")

                # cropped face location
                cropped_face_location = face_recognition.load_image_file('{}cropped.jpg'.format(login_images_path))
                # cropped face encodings
                cropped_face_encoding = face_recognition.face_encodings(cropped_face_location)[0]  

                match = face_recognition.face_distance([user_image_encoding], cropped_face_encoding)
                match = match[0]
                print(match)
                os.remove('{}cropped.jpg'.format(login_images_path))

                if match < 0.4:
                    loggedIn = True
                    speak("user_loggedIn", "You are logged in succesfully")
                    break
            if(loggedIn):
                os.remove('{}{}.jpg'.format(login_images_path,temp_image))
                break
            else:
                continue

        else:
            break


    #if multiple faces are not present

    if not multiple_faces :
        print(rect[0])
        x1 = rect[0].left()
        x2 = rect[0].right()
        y1 = rect[0].top()
        y2 = rect[0].bottom()
        print(x1, x2, y1, y2)


        write_success = cv2.imwrite('{}{}.jpg'.format(
            login_images_path, given_username), image)

        if not write_success:
            raise "Image writing was not succesfull"

        user_image_location = face_recognition.load_image_file(
            '{}{}.jpg'.format(user_images_path, given_username))
        user_image_encoding = face_recognition.face_encodings(user_image_location)[0]

        # for key, user in users.items():
        if(name_exists):
            print(user)
            db_face_locations = face_recognition.load_image_file(
                '{}{}.jpg'.format(user_images_path, user))
            db_face_encodings = face_recognition.face_encodings(db_face_locations)[0]

            match = face_recognition.face_distance(
            [user_image_encoding], db_face_encodings)
            match = match[0]
            print(match)
            if match < 0.4:
                speak("user_loggedIn", "You are logged in succesfully")
                loggedIn = True

        os.remove('{}{}.jpg'.format(login_images_path, given_username))

    if loggedIn:
        print("hii")
        usingOnlyEye.start_detection(given_username)
