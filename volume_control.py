import cv2
import mediapipe as mp
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# 1. Access System Volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

# 2. Initialize Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])

            if lm_list:
                # Thumb tip (4) and Index tip (8)
                x1, y1 = lm_list[4][1], lm_list[4][2]
                x2, y2 = lm_list[8][1], lm_list[8][2]
                
                # Calculate distance between fingers
                length = math.hypot(x2 - x1, y2 - y1)

                # --- NEW INTERPOLATION LOGIC ---
                # Map distance to Volume Level
                vol = np.interp(length, [50, 200], [minVol, maxVol])
                # Map distance to Bar position (pixels on screen)
                volBar = np.interp(length, [50, 200], [400, 150])
                # Map distance to Percentage (0-100)
                volPer = np.interp(length, [50, 200], [0, 100])
                
                volume.SetMasterVolumeLevel(vol, None)

                # Draw circles on fingers and a line between them
                cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

    # --- DRAWING THE UI ---
    # Draw the background volume rectangle
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    # Fill the rectangle based on volume level
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    # Display Percentage Text
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 
                1, (255, 0, 0), 3)

    cv2.imshow("Janani's AI Volume Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()