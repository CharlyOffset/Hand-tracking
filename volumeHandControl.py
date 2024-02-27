import time
import cv2
import numpy as np
import handTrackingModule as htm
import math

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


######################################
wCam, hCam = 640, 480
######################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=1)


# initialisation of the volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPercent = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])   # pour afficher les differente position de lmList[4] et lmList[8]

        # to put the different indexes of lmList[4] and lmList[8] in x1 y1 and x2 y2
        # note: lmList are the two fingers choosen to make the task
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

         # to put circles on the two choosen finger landmarks
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)       # to draw the line linkig the two fingers
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)    # to put the middle(center) cirle

        length = math.hypot(x2 - x1, y1 - y2)
        #print(length)  # to print the distance of x2 - x1 and y1 - y2 from the center which is 30 to 150

        #hand length 30 to 150
        # volume range  -65 to 0

        vol = np.interp(length, [30,150],[minVol, maxVol])
        volBar = np.interp(length, [30, 150], [400, 150])
        volPercent = np.interp(length, [30, 150], [0, 100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)


        if length < 30:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

  # display volume on the screen
    cv2.rectangle(img, (30, 150), (70, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (30, int(volBar)), (70, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'vol: {int(volPercent)} %', (30, 450), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 3)
    # frequency timer
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'fPS: {int(fps)}', (30, 50), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 3)  # display on screen
    cv2.imshow("image", img)
    cv2.waitKey(1)