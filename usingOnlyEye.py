import math
import os
from threading import Thread
import time

# Project related imports for image processing
import cv2
import dlib
from gtts.tts import gTTS
import numpy as np
from imutils import face_utils
import concurrent.futures
from playsound import playsound

# Importing required files
import start
import Distraction
# Declaring constants

# Drowsy Distance between eye lids threshold
EYE_OPEN_THERSHOLD = 7

# Drowsy Time Threshold 
EYE_THRESH = 3

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


# Alarm when driver is drowsy for a threshold value of frames
def distractionAlert(num, msg):
    tts = gTTS("You seem distracted please focus on the road")
    tts.save('hello1.mp3')
    playsound('hello1.mp3')
    os.remove('hello1.mp3')



# No Face detected flag
NO_FACE_FLAG = False
NO_FACE_FLAG1 = False
# Function for alarm when no face is detected
def NoFaceFunc():
    global NO_FACE_FLAG, NO_FACE_FLAG1
    time.sleep(4)
    if not NO_FACE_FLAG and not NO_FACE_FLAG1:
        NO_FACE_FLAG = True
        tts = gTTS("No face is detected please make sure you are properly visible in the camera")
        tts.save('noFace.mp3')
        playsound('noFace.mp3')
        os.remove('noFace.mp3')
        NO_FACE_FLAG = False


def increasingWithTime():
    global DISC_COUNTER
    time.sleep(1)
    DISC_COUNTER += 1
    if DISC_COUNTER > DISC_COUNT_THRES + 5:
        DISC_COUNTER = 0
    increasingWithTime()

incTimeThread = Thread(target = increasingWithTime)
incTimeThread.daemon = True
incTimeThread.start()

def eyeThresholdCount():
    time.sleep(1)
    global EYE_CONSEC, EYE_FLAG
    EYE_CONSEC += 1
    EYE_FLAG = False

print("Started..")

while True:

    # Capturing frames
    _, frame = cap.read()

    # Converting the camera input to gray scale image for detection
    gray = cv2.cvtColor(src = frame, code = cv2.COLOR_BGR2GRAY)

    # Getting all detected faces rectangle
    rects = detector(gray, 1)
    print(len(rects))
    if len(rects) == 0:
        NO_FACE_FLAG1 = False
        if not NO_FACE_FLAG:
            Thread(target = NoFaceFunc).start()
    else:
        NO_FACE_FLAG1 = True
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
                DISC_FLAG, message = future.result()
            print(message)
            if "Left" in message or "Right" in message:
                Thread(target = distractionAlert, args=(10, message)).start()
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
                eyeThresholdThread = Thread(target = eyeThresholdCount).start()
        else:
            EYE_CONSEC = 0

        # If eyes are closed for the entires threshold, performing specified event
        if(EYE_CONSEC >= EYE_THRESH):
            print("Drowsy")
            print(start.AdvanceDetection(cap))
            EYE_CONSEC = 0

        # Plotting the eye points on the screen
        for (x, y) in shape:
            cv2.circle(frame, (x, y), radius = 2, color=(0, 0, 255), thickness = -1)

    # Opening camera feed in a new window
    cv2.imshow(winname="Face", mat=frame)

    # Assigning ESC as closing key
    if cv2.waitKey(delay = 1) == 27:
        break

# Closing the camera input and closing the windows
cap.release()
cv2.destroyAllWindows()

