import math
import threading
import cv2
import dlib
from imutils import face_utils
import numpy as np
from numpy.core.numeric import count_nonzero
from scipy.spatial import distance as dist
import os
import pyttsx3
from gtts import gTTS
from playsound import playsound
import PNPProb

EYE_AR_THRESH = 0.3
EYE_BLINK_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 20
CONSEC_YAWN = 10
COUNTER = 0
TOTAL = 0
YAWN_THRESH = 25
ALARM_ON = False
COUNTER_YAWN = 0

alarm_status = False
alarm_status2 = False
saying = False

#Initialisation of pyttsxe
# engine = pyttsx3.init()

#Getting the points from the Facil landmarks
(jStart,jEnd) = face_utils.FACIAL_LANDMARKS_IDXS["jaw"]
(nStart,nEnd)= face_utils.FACIAL_LANDMARKS_IDXS["nose"]
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


 


def yawnAlarm(num):

    # Tried the pyttsx3 lib but it is sync

    # engine.say("You are feeling sleepy please take a break")
    # engine.runAndWait()

    # End

    # Using the Google text to speech for voice alert
    tts = gTTS("You are feeling sleepy please take a break")

    tts.save('hello.mp3')
    playsound("hello.mp3")
    os.remove('hello.mp3')


# Alarm when driver is drowsy for a threshold value of frames
def drowsyAlert(num):
    tts = gTTS("You are really sleepy please have some refreshments")
    tts.save('hello1.mp3')
    playsound('hello1.mp3')
    os.remove('hello1.mp3')



# EAR formula function, to calculate the distance between eyelids
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear  


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
# predictor = dlib.shape_predictor("shape_predictor_5_face_landmarks.dat")
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# read the image
cap = cv2.VideoCapture(0)

blinkCheck = False

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

        # For detection head pose
        newrect = dlib.rectangle(x,y,w,h)
        refImgPts = PNPProb.ref2dImagePoints(shape)
        height, width, channels = frame.shape
        focalLength = 1 * width
        cameraMatrix = PNPProb.CameraMatrix(focalLength, (height / 2, width / 2))

        mdists = np.zeros((4, 1), dtype=np.float64)

        # calculate rotation and translation vector using solvePnP
        success, rotationVector, translationVector = cv2.solvePnP(
        face3Dmodel, refImgPts, cameraMatrix, mdists)
        rmat, jac = cv2.Rodrigues(rotationVector)
        angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
        shape = face_utils.shape_to_np(shape)
        noseEndPoints3D = np.array([[0, 0, 1000.0]], dtype=np.float64)
        noseEndPoint2D, jacobian = cv2.projectPoints(
        noseEndPoints3D, rotationVector, translationVector, cameraMatrix, mdists)

        #  draw nose line
        p1 = (int(refImgPts[0, 0]), int(refImgPts[0, 1]))
        p2 = (int(noseEndPoint2D[0, 0, 0]), int(noseEndPoint2D[0, 0, 1]))
        cv2.line(frame, p1, p2, (110, 220, 0),thickness=2, lineType=cv2.LINE_AA)
        
        rmat, jac = cv2.Rodrigues(rotationVector)
        angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
        # print('*' * 80)
        # print(f"Qx:{Qx}\tQy:{Qy}\tQz:{Qz}\t")
        x1 = np.arctan2(Qx[2][1], Qx[2][2])
        y1 = np.arctan2(-Qy[2][0], np.sqrt((Qy[2][1] * Qy[2][1] ) + (Qy[2][2] * Qy[2][2])))
        z1 = np.arctan2(Qz[0][0], Qz[1][0])
        # print("ThetaX: ", x)
        # print("ThetaY: ", y1)
        # print("ThetaZ: ", z)
        # print('*' * 80)
        if angles[1] < -15:
            GAZE = "Looking: Left"
        elif angles[1] > 15:
            GAZE = "Looking: Right"
        else:
            GAZE = "Forward"

        cv2.putText(frame, GAZE, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 80), 2)

        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        # print(face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]

        jaw = shape[jStart:jEnd]
        nose = shape[nStart:nEnd]
        l1= math.sqrt((jaw[0][0]-nose[1][0])**2+(jaw[0][1]-nose[1][1])**2)
        l2 = math.sqrt((jaw[16][0]-nose[1][0])**2+(jaw[16][1]-nose[1][1])**2)
        ratio = l1/l2
        m = (jaw[0][1]-jaw[16][1])/(jaw[0][0]-jaw[16][0])
        if (ratio <= 1.1 and ratio > .9) :
            cond1 = True
        else:
            cond1= False
        if (jaw[0][1]<= (nose[1][1]+5) and jaw[0][1]> (nose[1][1]-5)):
            cond2 = True
        else:
            cond2= False
        if (m <= .05 and m >-.05 ):
            cond3 = True
        else:
            cond3= False

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        distance = lip_distance(shape)
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        
        if (distance > YAWN_THRESH):
                COUNTER_YAWN += 1
                if COUNTER_YAWN >= CONSEC_YAWN:
                    cv2.putText(frame, "Yawn Alert", (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    if alarm_status2 == False and saying == False:
                        alarm_status2 = True
                        t1 = threading.Thread(target = yawnAlarm,args=(10,)).start()
                        # t.deamon = True
                        # t.start()
        else:
            COUNTER_YAWN = 0
            alarm_status2 = False


        if ear < EYE_BLINK_THRESH and blinkCheck == False:
            blinkCheck = True
            TOTAL += 1
        elif ear > 0.3:
            blinkCheck = False
        
        if ear < EYE_AR_THRESH:
            COUNTER += 1
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1
                if not ALARM_ON:
                    t = threading.Thread(target = drowsyAlert,args=(10,)).start()
                    ALARM_ON = True
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            # engine.stop()
            COUNTER = 0
            ALARM_ON = False
        
        cv2.putText(
            frame,
            "Blinks: {}".format(TOTAL),
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )
        cv2.putText(
            frame,
            "EAR: {:.2f}".format(ear),
            (300, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

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
            cv2.circle(frame, (x, y), radius=2, color=(0, 0, 255), thickness=-1)



    # show the image
    cv2.imshow(winname="Face", mat=frame)

    # Exit when escape is pressed
    if cv2.waitKey(delay=1) == 27:
        break

# When everything done, release the video capture and video write objects
cap.release()

# Close all windows
cv2.destroyAllWindows()
