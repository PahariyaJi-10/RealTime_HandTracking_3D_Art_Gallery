import cv2
import mediapipe as mp
import math

# Initialize MediaPipe
mp_hands = mp.solutions.hands 
hands = mp_hands.Hands(min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)

mp_draw = mp.solutions.drawing_utils

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    # Flip image (optional for mirror view)
    img = cv2.flip(img, 1)

    # Convert to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # Initialize points
    thumb_tip = None
    index_tip = None

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:

            # Draw landmarks
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            h, w, c = img.shape

            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)

                # Index finger tip (id = 8)
                if id == 8:
                    index_tip = (cx, cy)
                    cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

                # Thumb tip (id = 4)
                if id == 4:
                    thumb_tip = (cx, cy)
                    cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

            # --- PINCH DETECTION ---
            if thumb_tip and index_tip:
                x1, y1 = thumb_tip
                x2, y2 = index_tip

                distance = math.hypot(x2 - x1, y2 - y1)

                # Draw line between fingers
                cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)

                # Show distance
                cv2.putText(img, f"Dist: {int(distance)}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                # Pinch condition
                if distance < 40:
                    cv2.putText(img, "PINCH", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                    print("PINCH")

                else:
                    cv2.putText(img, "MOVE", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    cv2.imshow("Hand Tracking", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()