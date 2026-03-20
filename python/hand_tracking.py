import cv2
import mediapipe as mp
import math
import pyautogui

# Screen size
screen_width, screen_height = pyautogui.size()

# Initialize MediaPipe
mp_hands = mp.solutions.hands 
hands = mp_hands.Hands(min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)

mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

# Smoothing
prev_x, prev_y = 0, 0
smoothening = 5

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    thumb_tip = None
    index_tip = None

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            h, w, c = img.shape

            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)

                if id == 8:  # Index
                    index_tip = (cx, cy)
                    cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

                if id == 4:  # Thumb
                    thumb_tip = (cx, cy)
                    cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

            if thumb_tip and index_tip:
                x1, y1 = thumb_tip
                x2, y2 = index_tip

                distance = math.hypot(x2 - x1, y2 - y1)

                # Map to screen
                screen_x = int(x2 * screen_width / w)
                screen_y = int(y2 * screen_height / h)

                # Smooth
                curr_x = prev_x + (screen_x - prev_x) / smoothening
                curr_y = prev_y + (screen_y - prev_y) / smoothening

                prev_x, prev_y = curr_x, curr_y

                # Move mouse
                pyautogui.moveTo(curr_x, curr_y)

                # Click (pinch)
                if distance < 40:
                    pyautogui.click()
                    cv2.putText(img, "CLICK", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                else:
                    cv2.putText(img, "MOVE", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    cv2.imshow("Hand Mouse Control", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()