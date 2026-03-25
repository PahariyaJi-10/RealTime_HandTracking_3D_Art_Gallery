import cv2
import mediapipe as mp
import pyautogui
import asyncio
import websockets

# Screen size
screen_width, screen_height = pyautogui.size()

# MediaPipe
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

    mode = "stop"  # draw / erase / stop

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            h, w, _ = img.shape

            # 👉 Index tip & pip
            index_tip = handLms.landmark[8]
            index_pip = handLms.landmark[6]

            middle_tip = handLms.landmark[12]
            middle_pip = handLms.landmark[10]

            # Convert to pixels
            x = int(index_tip.x * w)
            y = int(index_tip.y * h)

            # Screen mapping
            screen_x = int(x * screen_width / w)
            screen_y = int(y * screen_height / h)

            # Smooth movement
            curr_x = prev_x * 0.7 + screen_x * 0.3
            curr_y = prev_y * 0.7 + screen_y * 0.3

            prev_x, prev_y = curr_x, curr_y

            # 👉 Finger detection
            index_up = index_tip.y < index_pip.y
            middle_up = middle_tip.y < middle_pip.y

            if index_up and not middle_up:
                mode = "draw"
            elif index_up and middle_up:
                mode = "erase"
            else:
                mode = "stop"

            print(int(curr_x), int(curr_y), mode)

    cv2.imshow("Hand Tracking", img)

    if cv2.waitKey(1) & 0xFF == 27:
        return "exit"

    return f"{int(curr_x)},{int(curr_y)},{mode}"

# WebSocket
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


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Server started at ws://localhost:8765")
        await asyncio.Future()


asyncio.run(main())

cap.release()
cv2.destroyAllWindows()