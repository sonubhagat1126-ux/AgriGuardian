# SmartEdge AgriGuardian - Mobile App Integration 🌾

This mobile app is built with Flutter and has been fully integrated with the live hardware sensor server running on your laptop.

## 🚀 How to Run the App

Since Flutter is not in the system environment PATH for this terminal sandbox, you should launch the app from your local development environment:

### Method 1: Using VS Code (Recommended)
1. Open **VS Code**.
2. Select **File > Open Folder...** and choose `d:\python programe\AGRO SNAPDRAGON\smartedge_app\mobile_app`.
3. Select your device (Android Emulator, Web, or your **OnePlus 15** phone via USB debugging) in the status bar at the bottom right.
4. Press **`F5`** (or go to `Run > Start Debugging`) to build and launch the app!

### Method 2: Using the Command Prompt / PowerShell
Open your terminal (where you have your Flutter SDK configured) and run:
```bash
cd "d:\python programe\AGRO SNAPDRAGON\smartedge_app\mobile_app"
flutter run
```

---

## 🔌 Connecting to Your Live Arduino Sensors

To display the live data from your Arduino UNO Q (`COM8`):
1. Launch the mobile app.
2. On the Home screen, tap the **Settings icon** (gear symbol ⚙️) in the top-right corner.
3. Enter your laptop's local network IP address (e.g. `192.168.x.x:8000`).
   * *If running on an Android Emulator, use `10.0.2.2:8000` (which is the loopback address to your laptop's localhost).*
4. Tap **Save**.

The app will immediately start polling your laptop's FastAPI server every **2 seconds**, dynamically updating the **Moisture**, **Temperature**, **Humidity**, and calculating a live **Crop Health Score**!
