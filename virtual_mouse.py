import cv2
import pyautogui
# We import the internal path directly to bypass the 'solutions' error
try:
    import mediapipe.python.solutions.hands as mp_hands
    import mediapipe.python.solutions.drawing_utils as mp_drawing
except ImportError:
    # If that fails, we try the alternative internal path
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import drawing_utils as mp_drawing

# Initialize using the direct imports
detector = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = detector.process(imgRGB)
    
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            # Landmark 8 is the Index Finger Tip
            index_finger = handLms.landmark[8]
            
            # Map coordinates to screen
            cursor_x = int(index_finger.x * screen_w)
            cursor_y = int(index_finger.y * screen_h)
            
            # Move mouse (setting tween=0 makes it instant)
            pyautogui.moveTo(cursor_x, cursor_y, _pause=False)
            
            # Draw a circle on your finger in the preview
            h, w, _ = img.shape
            cv2.circle(img, (int(index_finger.x * w), int(index_finger.y * h)), 10, (0, 255, 0), cv2.FILLED)

    cv2.imshow("Hand Mouse Test", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()