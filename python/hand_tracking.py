import cv2
import mediapipe as mp
import math
import pyautogui
import asyncio
import websockets

# Screen size
screen_width, screen_height = pyautogui.size()

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)

mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0


def process_hand():
    global prev_x, prev_y, curr_x, curr_y

    success, img = cap.read()
    if not success:
        return None

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    pinch_state = 0

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            h, w, _ = img.shape
            thumb_tip = None
            index_tip = None

            # 🔥 IMPORTANT LOOP
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)

                if id == 8:  # Index finger
                    index_tip = (cx, cy)
                if id == 4:  # Thumb
                    thumb_tip = (cx, cy)

            if thumb_tip and index_tip:
                x1, y1 = thumb_tip
                x2, y2 = index_tip

                # Distance for pinch
                distance = math.hypot(x2 - x1, y2 - y1)

                # 🔥 CORRECT SCREEN MAPPING
                screen_x = int(x2 * screen_width / w)
                screen_y = int(y2 * screen_height / h)

                # 🔥 LIGHT SMOOTHING (balanced)
                curr_x = prev_x * 0.7 + screen_x * 0.3
                curr_y = prev_y * 0.7 + screen_y * 0.3

                prev_x, prev_y = curr_x, curr_y

                # Pinch detection
                if distance < 40:
                    pinch_state = 1

                # Debug
                print(int(curr_x), int(curr_y), pinch_state)

    cv2.imshow("Hand Tracking", img)

    if cv2.waitKey(1) & 0xFF == 27:
        return "exit"

    return f"{int(curr_x)},{int(curr_y)},{pinch_state}"


# 🔥 WebSocket handler
async def handler(websocket):
    print("Browser connected")

    try:
        while True:
            data = process_hand()

            if data == "exit":
                break

            if data:
                await websocket.send(data)

            await asyncio.sleep(0.003)

    except:
        print("Browser disconnected safely")


# 🔥 Run server
async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Server started at ws://localhost:8765")
        await asyncio.Future()


asyncio.run(main())

cap.release()
cv2.destroyAllWindows()