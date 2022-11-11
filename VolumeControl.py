import cv2
import time
import math
import numpy as np
import mediapipe as mp
import HandTrackingModule as htm

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0

detector = htm.handDetector(detectionCon=0.7)

# pycaw usage
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volPer = 0
volBar = 400
while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:

        # Filter based on size

        # print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 7, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)

        # Hand range 50 - 300
        # Volume Range -65 - 0

        vol = np.interp(length, [12,165], [minVol, maxVol])
        volBar = np.interp(length, [12,165], [400, 150])
        volPer = np.interp(length, [12,165], [0, 100])

        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

    cv2.rectangle(img, (50,150), (85,400), (250, 0, 0), 3)
    cv2.rectangle(img, (50,int(volBar)), (85,400), (250, 0, 0), cv2.FILLED)
    cv2.putText(img, f'  {int(volPer)} %', (20, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (250, 0, 0), 2)


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (20, 60), cv2.FONT_HERSHEY_COMPLEX, 1, (250, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
