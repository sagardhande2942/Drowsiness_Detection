# Basic python imports
import math
import os
import threading
import time

# Imports related to image processing and alarms
import cv2
import dlib
import numpy as np 
from gtts import gTTS
from imutils import face_utils
from numpy.core.numeric import count_nonzero
from playsound import playsound
from scipy.spatial import distance as dist

# PNPProb ( Perspective-n-Point Problem ) import from the file ( For 3d face detection )
import PNPProb

# Declaring Required Constants And Thresholds

# Time threshold for yawn detection
CONSEC_YAWN = 10

# Drowsy Detection seconds  counter ( eyes closed for sec )
COUNTER = 0

# Blinks counter
TOTAL = 0


# Yawn Distance Threshold for lips
YAWN_THRESH = 25

# Flag for alarm
ALARM_ON = False

# Yawn counter
COUNTER_YAWN = 0

# Flag required for various alarms
alarm_status = False
alarm_status2 = False
saying = False


# Initialisation of pyttsxe
# engine = pyttsx3.init()

# Getting the points from the Facil landmarks
(jStart, jEnd) = face_utils.FACIAL_LANDMARKS_IDXS["jaw"] # Points for jaw
(nStart, nEnd) = face_utils.FACIAL_LANDMARKS_IDXS["nose"] # Points for nose
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"] # Points for left eye
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"] # Points for right eye


# Function to sound the yawn alarm
def yawnAlarm():

    # Tried the pyttsx3 lib but it is sync

    # engine.say("You are feeling sleepy please take a break")
    # engine.runAndWait()

    # End

    # Using the Google text to speech for voice alert
    tts = gTTS("You are feeling sleepy please take a break")

    tts.save('hello.mp3')
    playsound("hello.mp3")
    os.remove('hello.mp3')





# EAR formula function, to calculate the distance between eyelids
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])

    #Calculating the EAR from the standard formula
    EAR = (A + B) / (2.0 * C)
    return EAR


# MAR formula function, to calculate the distance between lips
def lip_distance(shape):
    top_lip = shape[50:53]
    top_lip = np.concatenate((top_lip, shape[61:64]))

    low_lip = shape[56:59]
    low_lip = np.concatenate((low_lip, shape[65:68]))

    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)

    distance = abs(top_mean[1] - low_mean[1])
    return distance


# Loading the 3d model for head pose estimation from PNPProb
face3Dmodel = PNPProb.ref3DModel()


# Load the detector
detector = dlib.get_frontal_face_detector()

# Load the predictor
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# read the image
# cap = cv2.VideoCapture(0)

# Flag for Blink Check
blinkCheck = False

def Distraction(cap):
    global blinkCheck, predictor, detector, face3Dmodel, CONSEC_YAWN, COUNTER, TOTAL, YAWN_THRESH, ALARM_ON, COUNTER_YAWN, alarm_status, alarm_status2, saying

    while True:
        # taking frames from the video
        _, frame = cap.read()

        # Convert image into grayscale
        gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)

        # Use detector to find rectangle box for all detected faces
        rects = detector(gray, 1)

        # For iterating through all the faces detected by detector
        for (i, rect) in enumerate(rects):

            # determine the facial landmarks for the face region
            shape = predictor(gray, rect)

            # the four corners of rectangle around face
            (x, y, w, h) = face_utils.rect_to_bb(rect)

            # Displaying the rectangle on the screen
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # For detecting head pose
            newrect = dlib.rectangle(x, y, w, h)
            refImgPts = PNPProb.ref2dImagePoints(shape)
            height, width, channels = frame.shape
            focalLength = 1 * width
            cameraMatrix = PNPProb.CameraMatrix(
                focalLength, (height / 2, width / 2))

            mdists = np.zeros((4, 1), dtype=np.float64)

            # calculate rotation and translation vector using solvePnP
            # solvePNP is a OpenCV api to solve the PnP Problem
            success, rotationVector, translationVector = cv2.solvePnP(
                face3Dmodel, refImgPts, cameraMatrix, mdists)

            # Rodrigues is an API of OpenCV, it converts rotation matrix to a
            # rotation vector ( because we already have rotation matrix from solvePNP )
            rmat, jac = cv2.Rodrigues(rotationVector)

            # RQDecomp3x3 is an api of OpenCV to extract Euler Angles from Rotation Vector
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
            shape = face_utils.shape_to_np(shape)
            noseEndPoints3D = np.array([[0, 0, 1000.0]], dtype=np.float64)

            #  draw nose line
            noseEndPoint2D, jacobian = cv2.projectPoints(
                noseEndPoints3D, rotationVector, translationVector, cameraMatrix, mdists)
            p1 = (int(refImgPts[0, 0]), int(refImgPts[0, 1]))
            p2 = (int(noseEndPoint2D[0, 0, 0]), int(noseEndPoint2D[0, 0, 1]))
            cv2.line(frame, p1, p2, (110, 220, 0),
                    thickness=2, lineType=cv2.LINE_AA)

            # Delete later
            # rmat, jac = cv2.Rodrigues(rotationVector)
            # angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

            # print('*' * 80)
            # print(f"Qx:{Qx}\tQy:{Qy}\tQz:{Qz}\t")

            # Using arctan to get angle from tan inverse
            x1 = np.arctan2(Qx[2][1], Qx[2][2])
            y1 = np.arctan2(-Qy[2][0], np.sqrt((Qy[2][1] *
                            Qy[2][1]) + (Qy[2][2] * Qy[2][2])))
            z1 = np.arctan2(Qz[0][0], Qz[1][0])

            

            # Plotting eyes from the points taken from facial landmark
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            distance = lip_distance(shape)

            # Getting EAR for both eyes
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            ear = (leftEAR + rightEAR) / 2.0

            # Plotting the ellipses for both the eyes
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)

            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            # Deciding whether yawn threshold is reached
            if (distance > YAWN_THRESH):
                COUNTER_YAWN += 1
                if COUNTER_YAWN >= CONSEC_YAWN:
                    cv2.putText(frame, "Yawn Alert", (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    if alarm_status2 == False and saying == False:
                        alarm_status2 = True

                        # Alarm alert on a different thread
                        t1 = threading.Thread(target=yawnAlarm, args=(10,)).start()
                        # t.deamon = True
                        # t.start()
            else:
                COUNTER_YAWN = 0
                alarm_status2 = False

            # Deciding whether the user blinked or not & increasing the counter accordingly
            # if ear < EYE_BLINK_THRESH and blinkCheck == False:
            #     blinkCheck = True
            #     TOTAL += 1
            # elif ear > 0.3:
            #     blinkCheck = False


            # Printing the total blinks on screen
            cv2.putText(
                frame,
                "Blinks: {}".format(TOTAL),
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

            # Printing the current EAR of the driver on screen
            cv2.putText(
                frame,
                "EAR: {:.2f}".format(ear),
                (300, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
            )

            # Printing the current MAR of the driver on screen
            cv2.putText(
                frame,
                "MAR: {:.2f}".format(distance),
                (300, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
            )



            # convert dlib's rectangle to a OpenCV-style bounding box
            # [i.e., (x, y, w, h)], then draw the face bounding box

            cv2.putText(frame, "Face #{}".format(i + 1), (x - 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # loop over the (x, y)-coordinates for the facial landmarks
            # and draw them on the image
            for (x, y) in shape:
                # cv2.circle(frame, (x, y), 1, (0, 0, 255), -1, radius=2)
                cv2.circle(frame, (x, y), radius=2,
                        color=(0, 0, 255), thickness=-1)


            if angles[1] < -20:
                GAZE = "Looking Left"
                return True, "User is distracted {}".format(GAZE), distance
            elif angles[1] > 20:
                GAZE = "Looking Right"
                return True, "User is distracted {}".format(GAZE), distance
            else:
                GAZE = "Forward"
                return True, "User is focussed now", distance

            # cv2.putText(frame, GAZE, (20, 20),
            #         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 80), 2)

        # show the image
        cv2.imshow(winname="Face", mat=frame)

        # Exit when escape is pressed
        if cv2.waitKey(delay=1) == 27:
            break

    # When everything done, release the video capture and video write objects
    cap.release()

    # Close all windows
    cv2.destroyAllWindows()
