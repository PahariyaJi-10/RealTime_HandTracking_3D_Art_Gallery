import cv2
import mediapipe as mp
import pyautogui
import asyncio
import websockets

# Screen size
screen_width, screen_height = pyautogui.size()

# MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Camera
cap = cv2.VideoCapture(0)

# 🔥 IMPORTANT (initialize smoothing vars)
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0


async def handler(websocket):
    global prev_x, prev_y, curr_x, curr_y

    print("✅ Browser connected")

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        mode = "stop"
        send_data = None

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

                h, w, _ = img.shape

                index_tip = handLms.landmark[8]
                index_pip = handLms.landmark[6]

                middle_tip = handLms.landmark[12]
                middle_pip = handLms.landmark[10]

                # Pixel position
                x = int(index_tip.x * w)
                y = int(index_tip.y * h)

                # Highlight
                cv2.circle(img, (x, y), 10, (0, 255, 0), -1)

                # 🔥 SCREEN MAPPING
                screen_x = int(x * screen_width / w)
                screen_y = int(y * screen_height / h)

                # 🔥 PERFECT SMOOTHING
                alpha = 0.6
                curr_x = prev_x + (screen_x - prev_x) * alpha
                curr_y = prev_y + (screen_y - prev_y) * alpha

                prev_x, prev_y = curr_x, curr_y

                # 👉 Gesture detection
                index_up = index_tip.y < index_pip.y
                middle_up = middle_tip.y < middle_pip.y

                if index_up and not middle_up:
                    mode = "draw"
                elif index_up and middle_up:
                    mode = "erase"
                else:
                    mode = "stop"

                # 🔥 SEND SMOOTHED DATA (FIXED)
                send_data = f"{int(curr_x)},{int(curr_y)},{mode}"

        # Send data
        if send_data:
            await websocket.send(send_data)

        # Show camera
        cv2.imshow("Hand Tracking", img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

        # 🔥 MINIMAL DELAY
        await asyncio.sleep(0.001)

    cap.release()
    cv2.destroyAllWindows()


async def main():
    print("🚀 Server started at ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())