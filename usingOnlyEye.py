import speech_recognition as sr
import pandas as pd
from playsound import playsound
import sys
import concurrent.futures
from imutils import face_utils
import numpy as np
from gtts.tts import gTTS
import dlib
import cv2
import os
from threading import Thread
import time
from datetime import datetime, date
import face_recognition
from PIL import Image
today = date.today()

# Project related imports for image processing

# Importing required files
import Distraction
import main_detection 

# Initializing the speech recognition
r = sr.Recognizer()

# Asking for the user's name before starting
# NAME = input("Please enter your name : ")
# NAME = NAME.lower()

# A comman speak function
def speak(filename, msg):
    tts = gTTS("{}".format("{}".format(msg)))
    tts.save('{}.mp3'.format(filename))
    playsound('{}.mp3'.format(filename))
    os.remove('{}.mp3'.format(filename))

# The global name variable
# NAME = ""

# Function for input of user name
# with sr.Microphone() as source:
#     while True:
#         try:
#             speak("name_again", "Hello, what is your name?")
#             text = r.record(source, duration=5)
#             recognised_text = r.recognize_google(text)
#             # time.sleep(3)
#             NAME = recognised_text
#             print(recognised_text)
#             speak("NAME", "Is your name, {}, please say ok to confirm".format(NAME))
#             text = r.record(source, duration=5)
#             confirm_name = r.recognize_google(text)
#             print(confirm_name)
#             if "ok" in confirm_name.lower() or "":
#                 speak("welcome", "Welcome onboard, {}".format(NAME))
#                 break
#             else:
#                 speak("tryAgain", "Please try again")
#                 continue

#             # os.exit()
#         except Exception as e:
#             print(e)
#             print(len(NAME))
#             if len(NAME.strip()) == 0:
#                 speak("nameNotFound", "I didn't get that, please try again!")
#                 continue


# Declaring constants

# Drowsy Distance between eye lids threshold
EYE_OPEN_THERSHOLD = 7

# Drowsy Time Threshold
EYE_THRESH = 1

# Eye closed counter
EYE_CONSEC = 0

# Eye consec counter function flag
EYE_FLAG = False


# Frame capture delay
FPS = 1

# Loading the detector
detector = dlib.get_frontal_face_detector()

# Loading the predictor
predictor = dlib.shape_predictor("eye_predictor.dat")

# Distraction Counter
DISC_COUNTER = 0

# Distractoin Counter Threshold
DISC_COUNT_THRES = 7

# Distraction Flag
DISC_FLAG = False
DISC_FLAG1 = False

# Taking video input form specified camera
cap = cv2.VideoCapture(0)

# Mouth Aspect Ration Constant
MAR = 0
MAR_COUNTER = 0

# MAR Threshold
MAR_THRES = 20

# Alarm when driver is drowsy for a threshold value of frames


def distractionAlert(num, msg):
    tts = gTTS("{}".format(msg))
    tts.save('distractAlert.mp3')
    playsound('distractAlert.mp3')
    os.remove('distractAlert.mp3')


# Multiple places flag
MULTIPLE_FACES_FLAG = False

# Alarm when multiple faces are detected

def multipleFacesAlarm(msg):
    global MULTIPLE_FACES_FLAG
    if MULTIPLE_FACES_FLAG:
        tts = gTTS("{}".format(msg))
        tts.save('multipleFaces.mp3')
        playsound('multipleFaces.mp3')
        os.remove('multipleFaces.mp3')
        time.sleep(2)
        MULTIPLE_FACES_FLAG = False


# No Face detected flag
NO_FACE_FLAG = False
NO_FACE_FLAG1 = False
NO_FACE_THRES = 10

# Vars for df rows
Dfmsg = ""

NO_FACE_COUNT = 0

# Function for alarm when no face is detected


def NoFaceFunc():
    global NO_FACE_FLAG, NO_FACE_FLAG1, Dfmsg, NO_FACE_THRES, NO_FACE_COUNT
    time.sleep(NO_FACE_THRES)
    if not NO_FACE_FLAG and not NO_FACE_FLAG1:
        mst = []
        mst = Dfmsg.split(" | ")
        if mst[len(mst) - 1] != "No face detected" or NO_FACE_COUNT == 60:
            Dfmsg += "No face detected | "
            NO_FACE_COUNT = 0
        NO_FACE_FLAG = True
        tts = gTTS(
            "No face is detected please make sure you are properly visible in the camera")
        tts.save('noFace.mp3')
        playsound('noFace.mp3')
        os.remove('noFace.mp3')
        playsound('beep.mp3')

        # Beta mode
        # print(start.AdvanceDetection(cap))
        NO_FACE_FLAG = False


def increasingWithTime():
    global DISC_COUNTER, NO_FACE_COUNT
    time.sleep(1)
    DISC_COUNTER += 1
    NO_FACE_COUNT += 1
    if DISC_COUNTER > DISC_COUNT_THRES + 5:
        DISC_COUNTER = 0
    increasingWithTime()


incTimeThread = Thread(target=increasingWithTime)
incTimeThread.daemon = True
incTimeThread.start()


def eyeThresholdCount():
    time.sleep(1)
    global EYE_CONSEC, EYE_FLAG
    EYE_CONSEC += 1
    EYE_FLAG = False


print("Started..")

data = {
    'Name': 'NEW SESSION',
    'Time': today.strftime("%d-%m-%Y") + " " + datetime.now().strftime("%H:%M:%S"),
    'Message': 'Message',
}

df = pd.DataFrame(data, index=[0])

# To close flag
TO_END = False

NAME = sys.argv[1]

def start_detection():
    global TO_END, df, NO_FACE_FLAG, NO_FACE_FLAG1, Dfmsg, NO_FACE_COUNT, NO_FACE_THRES, MAR_THRES, MAR, MAR_COUNTER
    global cap, DISC_FLAG, DISC_FLAG1, DISC_FLAG1, DISC_COUNT_THRES, DISC_COUNTER, predictor, detector, FPS, EYE_FLAG, EYE_CONSEC
    global EYE_OPEN_THERSHOLD, EYE_THRESH, r, today
    user_images_path = "user_images/"
    while True:
        TO_END = True

        # Capturing frames
        _, frame = cap.read()

        # Converting the camera input to gray scale image for detection
        gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)

        # Getting all detected faces rectangle
        rects = detector(gray, 1)

        # req_rect = []

        look_for_matching_face = False

        if len(rects) == 0:
            NO_FACE_FLAG1 = False
            if not NO_FACE_FLAG:
                Thread(target=NoFaceFunc).start()
        elif len(rects) > 1:

            print("in multiple faces")
            temp_image = "temp_image"

            #image with multiple faces
            img_captured = cv2.imwrite('{}{}.jpg'.format(user_images_path, temp_image), frame)  

            if not img_captured:
                print("storing image failed")

            user_image_location = face_recognition.load_image_file('{}{}.jpg'.format(user_images_path, NAME))
            user_image_encoding = face_recognition.face_encodings(user_image_location)[0]

            #captured image location
            cap_image_location = face_recognition.load_image_file('{}{}.jpg'.format(user_images_path, temp_image))
                
            # array of locations of all faces in captured image
            cap_image_encoding = face_recognition.face_encodings(cap_image_location)

            face_locations = face_recognition.face_locations(cap_image_location)
            
            for ind, face_encoding in enumerate(cap_image_encoding):
            
                top, right, bottom, left = face_locations[ind]
                face_image = cap_image_location[top:bottom,left:right]
                pil_image = Image.fromarray(face_image)

                # image of a single face in captured photo
                pil_image.save(user_images_path+"cropped.jpg")

                # cropped face location
                # cropped_face_location = face_recognition.load_image_file('{}cropped.jpg'.format(user_images_path))
                # # cropped face encodings
                # print("h")
                # cropped_face_encoding = face_recognition.face_encodings(cropped_face_location)
                # print(cropped_face_encoding)
                # cropped_face_encoding = cropped_face_encoding[0]

                match = face_recognition.face_distance([user_image_encoding], face_encoding)
                print(match)
                match = match[0]

                if match < 0.4:
                    look_for_matching_face = True
                    # print("hii2")
                    # multiple_faces_solved = True
                    # req_rect = [top, right, bottom, left]
                    # print("hii3")
                    # print(frame)
                    # frame = frame[top:top+(top - bottom), left:left+(right - left)]
                    # cv2.imwrite('myimage.jpg', frame)
                    # # Converting the camera input to gray scale image for detection
                    my_image = cv2.imread('{}cropped.jpg'.format(user_images_path))
                    gray = cv2.cvtColor(src=my_image, code=cv2.COLOR_BGR2GRAY)

                    # Getting all detected faces rectangle
                    rects = detector(gray, 1)
            if not look_for_matching_face:
                print("No Match Found")
        else:
            NO_FACE_FLAG1 = True



        # Multiple faces detection
        # if len(rects) > 1:
        #     time.sleep(2)
        #     multipleFaces = "Multiple faces detected please make sure only your face is present in the frame"
        #     if not MULTIPLE_FACES_FLAG:
        #         MULTIPLE_FACES_FLAG = True
        #         Thread(target = multipleFacesAlarm, args = (multipleFaces, )).start()
        #     continue

        # Running required processes on all detected faces

       

        for (i, rect) in enumerate(rects):

            # Getting the face details from the predictor
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            # Time wait for each frame
            # time.sleep(1 / FPS)

            # Distraction Check

            if DISC_COUNTER == DISC_COUNT_THRES and not DISC_FLAG1:
                DISC_FLAG1 = True
                print("Checking for distractions..")
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(Distraction.Distraction, cap)
                    DISC_FLAG, message, MAR = future.result()
                print(message)
                if MAR > MAR_THRES:
                    MAR_COUNTER += 1
                if MAR_COUNTER >= 2:
                    mm = "User is Speaking or talking on phone please focus on road"
                    Thread(target=distractionAlert, args=(
                        10, "{}".format(mm))).start()
                    Dfmsg += "{}".format(mm) + " | "
                    MAR_COUNTER = 0
                if "Left" in message or "Right" in message:
                    Thread(target=distractionAlert, args=(10, message)).start()
                    Dfmsg += "{}".format(message) + " | "
            if DISC_FLAG:
                DISC_FLAG1 = False
                DISC_COUNTER = 0
                DISC_FLAG = False

            # Getting the coordinates of eyelids in requierd variables
            test = shape
            _, leyetop = test[1]
            _, leyebot = test[5]
            _, reyetop = test[7]
            _, reyebot = test[11]

            # Checking if the distance between eye lids is less than the
            # Given threshold
            if abs(leyetop - leyebot) < EYE_OPEN_THERSHOLD and abs(reyetop - reyebot) < EYE_OPEN_THERSHOLD:
                if not EYE_FLAG:
                    eyeThresholdThread = Thread(target=eyeThresholdCount).start()
            else:
                EYE_CONSEC = 0

            # If eyes are closed for the entires threshold, performing specified event
            if(EYE_CONSEC >= EYE_THRESH):
                print("Drowsy")
                print(main_detection.AdvanceDetection(cap))
                Dfmsg += "User is drowsy | "
                EYE_CONSEC = 0

            # Plotting the eye points on the screen
            for (x, y) in shape:
                cv2.circle(frame, (x, y), radius=2,
                        color=(0, 0, 255), thickness=-1)

        # Opening camera feed in a new window
        cv2.imshow(winname="Face", mat=frame)

        # Assigning ESC as closing key
        try:
            if cv2.waitKey(delay=1) == 27:
                break
        except Exception as e:
            print("Error while closing with ESC :" + str(e))
        if len(Dfmsg) != 0:
            Dfmsg = Dfmsg[:-2]
            df.loc[len(df.index)] = [NAME, today.strftime("%Y-%m-%d") +
                                    " " + datetime.now().strftime("%H:%M:%S"), Dfmsg]
        Dfmsg = ""

    # Closing the camera input and closing the windows
    print(df)
    cap.release()
    cv2.destroyAllWindows()

    data = {
        'Name': 'END SESSION',
        'Time': today.strftime("%d-%m-%Y") + " " + datetime.now().strftime("%H:%M:%S"),
        'Message': 'Message',
    }

    df.loc[len(df.index)] = [data["Name"], data["Time"], data["Message"]]


    df.to_csv('{}.csv'.format(NAME), mode='a', header=False)
    # You're still reading? This is to take a look at what you want to double check your work. index_col = 0 will prevent a "Unnamed:0" column for appearing.
    df_result = pd.read_csv('{}.csv'.format(
        NAME), index_col=0).reset_index(drop=True, inplace=True)
    os.startfile('{}.csv'.format(NAME))
