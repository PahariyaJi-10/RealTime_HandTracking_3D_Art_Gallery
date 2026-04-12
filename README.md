# 🖐️ Real-Time Hand Tracking Drawing & 3D Art Gallery

An AI-powered web application that allows users to draw on a canvas using real-time hand gestures captured via webcam. The project integrates computer vision with a web-based drawing interface, providing a seamless and interactive experience.

# 🚀 Features:-
 🎨 Hand Gesture Drawing
- Draw using index finger tracking
- Real-time movement mapping
- Smooth curve rendering

 ✌ Gesture Controls
- ☝ Index finger → Draw
- ✌ Index + Middle → Erase
- ✊ No fingers → Stop

 🖌 Drawing Tools
- Color picker
- Brush size adjustment
- Smooth stroke rendering

 💾 Save & Gallery
- Save drawings locally
- View in gallery grid layout
- Click to preview (modal view)

🌙 UI Features
- Dark mode toggle
- Clean and modern UI
- Responsive layout

---

 🧠 Technologies Used

🔹 Frontend
- HTML5
- CSS3
- JavaScript (Canvas API)

🔹 Backend
- Python

🔹 Libraries
- OpenCV
- MediaPipe
- PyAutoGUI
- WebSockets (asyncio + websockets)


## ⚙️ How It Works

1. Python backend captures webcam feed using OpenCV  
2. MediaPipe detects hand landmarks  
3. Index finger position is tracked and mapped to screen coordinates  
4. Gesture detection determines draw/erase/stop modes  
5. Data is sent via WebSocket to the frontend  
6. Canvas renders strokes in real-time  
