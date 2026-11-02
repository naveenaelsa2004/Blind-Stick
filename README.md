# IoT-Based Smart Blind Stick for Visually Impaired People
### Complete IoT System with ESP32, Docker, SQLite Database, and Real-Time Dashboard

A reliable, beginner-friendly, and non-blocking IoT assistive navigation system built using an **ESP32 DevKit V1**, an **HC-SR04 ultrasonic sensor**, an **intermittent acoustic buzzer module**, a **FastAPI backend** containerized with **Docker**, an **SQLite database**, and a **real-time web dashboard**.

---

## 1. System Overview and Data Flow

The complete system transmits live obstacle measurements through the following pipeline:

```
[HC-SR04 Sensor]
       │ (10 µs Trigger / Echo Pulse)
       ▼
[ESP32 DevKit V1]
   ├─► Core 1: 60 ms Scan, Median Filter & Intermittent Buzzer (GPIO 19)
   └─► Core 0: FreeRTOS Task sends JSON Telemetry via Wi-Fi every 1.5s
       │ (HTTP POST /api/readings)
       ▼
[Docker Backend: FastAPI (Port 8000)]
       │ (Validates schema & range [2.0 - 400.0] cm)
       ▼
[Persistent SQLite DB: ./data/sensor_readings.db]
       ▲
       │ (HTTP Polling every 1.5s)
[Real-Time Web Dashboard: http://localhost:8000]
```

### Safety Design Principle
- **Buzzer is NEVER continuously ON:** Even within 15 cm, warnings consist of short 60 ms beeps separated by silence gaps to prevent ear fatigue and avoid masking sirens, speech, or oncoming traffic.
- **Dual-Core Isolation:** Core 1 runs the ultrasonic sensor and buzzer with zero latency. Core 0 handles Wi-Fi and HTTP in the background. Even if Wi-Fi disconnects or the backend server is offline, **local obstacle detection and buzzer operation continue completely uninterrupted!**

---

## 2. Project Directory Structure

```
Blind Stick/
├── platformio.ini               # PlatformIO build configuration for ESP32
├── docker-compose.yml           # Root Docker Compose service definition
├── .env.example                 # Environment variables template
├── src/
│   ├── config.h                 # Wi-Fi SSID, Password, and Backend URL settings
│   ├── config.h.example         # Template configuration header
│   └── main.cpp                 # Complete ESP32 firmware (Dual-Core FreeRTOS)
├── backend/
│   ├── main.py                  # FastAPI REST API & static dashboard server
│   ├── database.py              # SQLite storage layer with parameterized SQL
│   ├── requirements.txt         # Python dependencies (FastAPI, Uvicorn, Pydantic)
│   ├── Dockerfile               # Production Docker container definition
│   ├── docker-compose.yml       # Backend Docker Compose service definition
│   ├── .dockerignore            # Docker ignore file
│   ├── test_backend.py          # Automated API & database verification test suite
│   └── static/
│       ├── index.html           # Real-time web dashboard HTML
│       ├── style.css            # Modern glassmorphism dark mode styling
│       └── dashboard.js         # Chart.js time-series logic & live API poller
├── data/                        # Persistent SQLite host volume directory
│   └── sensor_readings.db       # SQLite database (auto-created on startup)
├── report/
│   ├── project_report.md        # Complete 20-section college assignment report
│   └── screenshots/             # Labeled screenshot placeholders for submission
└── README.md                    # Beginner-friendly setup guide
```

---

## 3. Hardware Connections & Pinout

| Peripheral | Pin | ESP32 DevKit V1 Pin | Notes |
|---|---|---|---|
| **HC-SR04** | **VCC** | ESP32 **VIN** (5V) | Powered from the USB 5V rail |
| **HC-SR04** | **GND** | ESP32 **GND** | Breadboard common ground |
| **HC-SR04** | **TRIG** | ESP32 **GPIO 5** | 10 µs trigger pulse |
| **HC-SR04** | **ECHO** | Voltage Divider Input | **Must be stepped down to 3.21 V!** |
| **Buzzer Module** | **VCC** | ESP32 **VIN (5V)** or **3.3V** | Active-LOW module power |
| **Buzzer Module** | **GND** | ESP32 **GND** | Breadboard common ground |
| **Buzzer Module** | **I/O** | ESP32 **GPIO 19** | Intermittent acoustic warning tone |

### Mandatory Voltage Divider for ECHO Pin

The HC-SR04 ECHO pulse is 5.0 V, but ESP32 GPIO pins tolerate a maximum of 3.3 V. Use a 1 kΩ ($R_1$) and 1.8 kΩ ($R_2$) resistor pair:

```
HC-SR04 ECHO Pin ──► [ 1 kΩ Resistor ] ──┬──► ESP32 GPIO 18 (3.21 V Safe Logic)
                                         │
                                   [ 1.8 kΩ Resistor ]
                                         │
                                         ▼
                                     ESP32 GND (Common Ground)
```

$$\text{Output Voltage} = 5.0\text{ V} \times \frac{1800\text{ }\Omega}{1000\text{ }\Omega + 1800\text{ }\Omega} \approx 3.21\text{ V}$$

---

## 4. Warning Ranges & Intermittent Acoustic Schedule

| Distance Measured | Status Label | Beep Duration | Silent Gap | Total Cycle Period | Beep Rate |
|---|---|---|---|---|---|
| **> 100 cm** | `CLEAR` | 0 ms | Continuous | 0 ms | Buzzer Silent (OFF) |
| **61 – 100 cm** | `WARNING` | 60 ms | ~740 ms | 800 ms | ~1.25 beeps/sec |
| **31 – 60 cm** | `CAUTION` | 60 ms | ~390 ms | 450 ms | ~2.2 beeps/sec |
| **15 – 30 cm** | `DANGER` | 60 ms | ~190 ms | 250 ms | 4.0 beeps/sec |
| **< 15 cm** | `VERY CLOSE` | 60 ms | ~90 ms | 150 ms | 6.7 beeps/sec |
| **Sensor Timeout** | `UNKNOWN` | 0 ms | Continuous | 0 ms | Buzzer Silent (Safe State) |

---

## 5. Beginner Step-by-Step Installation Guide (Windows & VS Code)

### Step 1: Install Required Software
1. **VS Code:** Download and install from [code.visualstudio.com](https://code.visualstudio.com/).
2. **PlatformIO IDE Extension:** Inside VS Code, press `Ctrl + Shift + X`, search for **PlatformIO IDE**, and click **Install**.
3. **Python 3.10+:** Ensure Python is installed and added to your Windows PATH.
4. **Docker Desktop:** Download and install from [docker.com](https://www.docker.com/products/docker-desktop/). Ensure Docker Desktop is running.

### Step 2: Open the Project in VS Code
1. Open VS Code.
2. Select **File > Open Folder...** and select `d:\Blind Stick`.
3. Wait a few seconds for PlatformIO and the workspace to initialize.

### Step 3: Find Your Computer's Reachable Local IP Address

> [!CRITICAL]
> **Windows Networking Rule:**
> In your ESP32 code, **do NOT use `localhost` or `127.0.0.1`!**
> On the ESP32, `localhost` refers to the ESP32 itself, not your computer.
> You must use your computer's local Wi-Fi IPv4 address on the same network.

1. Open PowerShell on your computer and run:
   ```powershell
   ipconfig
   ```
2. Look for your active **Wireless LAN adapter Wi-Fi** section.
3. Locate the **IPv4 Address** (for example: `192.168.31.153`).

### Step 4: Configure Wi-Fi & Backend Address in Firmware
Open [src/config.h](file:///d:/Blind%20Stick/src/config.h) in VS Code and set:

```cpp
// 1. Enter your Wi-Fi credentials (must be a 2.4 GHz network or mobile hotspot)
#define WIFI_SSID       "Your_WiFi_Name"
#define WIFI_PASSWORD   "Your_WiFi_Password"

// 2. Set your computer's local IP address (found in Step 3)
#define BACKEND_BASE_URL "http://192.168.31.153:8000"
#define BACKEND_ENDPOINT "/api/readings"

// 3. Device identifier
#define DEVICE_ID        "blind-stick-01"
```

Save the file (`Ctrl + S`).

---

## 6. How to Run the Backend & Database

You can run the backend in one of two ways:

### Method A: Using Docker Compose (Recommended)
1. Ensure **Docker Desktop** is running on your computer.
2. Open a terminal in the project root (`d:\Blind Stick`) and execute:
   ```powershell
   docker compose up --build
   ```
3. To run in the background (detached mode):
   ```powershell
   docker compose up -d --build
   ```
4. View container logs:
   ```powershell
   docker compose logs -f
   ```
5. Stop the container:
   ```powershell
   docker compose down
   ```

### Method B: Native Python Execution (Quick Alternative)
If Docker Desktop is not started, you can run the FastAPI server directly:
```powershell
# Open terminal in project root
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 7. How to Test the Backend API and Database

We have included an automated test suite that validates health, schemas, range checks, and database persistence.

Run the test suite in PowerShell:
```powershell
python backend/test_backend.py
```

Expected output:
```text
==================================================
 Running Automated Backend & Database Tests       
==================================================
[PASS] Test 1: GET /api/health returned 200 OK and database connected
[PASS] Test 2: POST /api/readings accepted valid reading (ID: 1)
[PASS] Test 3: POST /api/readings accepted danger range reading (18.5 cm)
[PASS] Test 4: POST /api/readings handled 'unknown' reading safely with distance null
[PASS] Test 5: POST /api/readings correctly rejected invalid status (HTTP 422)
[PASS] Test 6: POST /api/readings correctly rejected distance out of physical range (HTTP 422)
[PASS] Test 7: GET /api/readings returned 7 chronological records
[PASS] Test 8: GET /api/latest returned correct latest record
[PASS] Test 9: SQLite persistence verified in 'D:\Blind Stick\data\sensor_readings.db' (Row count: 7)
[PASS] Test 10: GET / successfully serves real-time dashboard HTML
==================================================
 All Backend & Database Tests PASSED Successfully! 
==================================================
```

### Manual API Verification in Browser:
- **Health Check:** Open `http://localhost:8000/api/health`
- **Latest Reading:** Open `http://localhost:8000/api/latest`
- **Recent Telemetry:** Open `http://localhost:8000/api/readings?limit=10`
- **Interactive OpenAPI Docs:** Open `http://localhost:8000/docs`

---

## 8. How to Upload Firmware to the ESP32

1. Connect your ESP32 DevKit V1 to your computer using a micro-USB data cable.
2. In VS Code:
   - Click the **PlatformIO Build** icon (`✔`) on the bottom blue status bar to compile.
   - Click the **PlatformIO Upload** icon (`➡`) on the bottom status bar to flash.
3. Or compile and upload using PowerShell:
   ```powershell
   # Compile firmware
   & "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe" run

   # Upload firmware to connected ESP32
   & "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe" run --target upload

   # Open Serial Monitor at 115200 baud
   & "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe" device monitor --baud 115200
   ```

---

## 9. Opening and Using the Real-Time Web Dashboard

1. Start the backend container or server (Port 8000).
2. Open your web browser (Chrome, Edge, Firefox) and navigate to:
   ```
   http://localhost:8000
   ```
   *(Or from another laptop/phone on the same Wi-Fi: `http://192.168.31.153:8000`)*
3. **Dashboard Features:**
   - **Hero Proximity Card:** Large numeric distance display in centimeters, warning status badge, and color proximity gauge.
   - **Hardware Buzzer Rhythm Visualizer:** Dynamic equalizing bars matching the live 150/250/450/800 ms beep rhythm on GPIO 19.
   - **Time-Series Chart:** Chart.js graph plotting distance vs. time, automatically refreshed every 1.5 seconds.
   - **Telemetry Audit Table:** Historical log displaying reading ID, device ID, distance, status, and UTC timestamp.
   - **System Alert Banners:** Displays warnings if the backend becomes disconnected or if sensor readings become stale (>5s).

---

## 10. How to Inspect Database Records

Sensor records are permanently saved in `./data/sensor_readings.db`. To inspect the stored data directly, run in PowerShell:

```powershell
python -c "import sqlite3; conn = sqlite3.connect('data/sensor_readings.db'); print(conn.execute('SELECT * FROM sensor_readings ORDER BY id DESC LIMIT 5;').fetchall())"
```

---

## 11. Complete End-to-End Demonstration Guide

Follow this 5-minute procedure during your college evaluation:

1. **Step 1: Start Backend:** Launch `docker compose up -d` or `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`.
2. **Step 2: Open Dashboard:** Open `http://localhost:8000` in your browser. Verify the backend status shows `Connected (HTTP 200)`.
3. **Step 3: Power ESP32:** Plug the ESP32 into a USB port or power bank.
4. **Step 4: Demonstrate Obstacle Detection:**
   - *Clear Path (>100 cm):* Point the sensor at an open space. Dashboard shows `CLEAR`, buzzer is silent.
   - *Warning Zone (61–100 cm):* Place your hand at 80 cm. Dashboard shows `WARNING`, buzzer emits slow beeps (every 800 ms).
   - *Caution Zone (31–60 cm):* Move hand to 45 cm. Dashboard shows `CAUTION`, buzzer beeps every 450 ms.
   - *Danger Zone (15–30 cm):* Move hand to 20 cm. Dashboard shows `DANGER`, buzzer beeps every 250 ms.
   - *Very Close Zone (<15 cm):* Move hand to 10 cm. Dashboard pulses `VERY CLOSE`, buzzer emits rapid pulses every 150 ms.
5. **Step 5: Demonstrate Chart & Audit Table:** Point out the live curve on the Chart.js graph and the new rows appearing in the audit table.
6. **Step 6: Demonstrate Network Fail-Safe:** Turn off your Wi-Fi or stop the container. Point out that the buzzer continues warning you of obstacles in real-time, and the dashboard displays a connection alert banner.

---

## 12. Troubleshooting Guide

| Issue | Likely Cause | Exact Solution |
|---|---|---|
| **ESP32 cannot connect to backend (HTTP error)** | Using `localhost` or `127.0.0.1` in `config.h`. | Change `BACKEND_BASE_URL` in [src/config.h](file:///d:/Blind%20Stick/src/config.h) to your computer's actual Wi-Fi IPv4 address (e.g. `192.168.31.153`). |
| **Windows Firewall blocks ESP32 requests** | Windows Defender blocking port 8000. | Allow inbound traffic on port 8000 in Windows Defender Firewall or set network profile to Private. |
| **Buzzer sounds continuously without stopping** | Active-LOW module inverted polarity. | In [src/main.cpp](file:///d:/Blind%20Stick/src/main.cpp), line 32, verify `const bool BUZZER_ACTIVE_LOW = true;`. If your module is active-HIGH, change to `false;`. |
| **Distance shows `UNKNOWN` continuously** | Loose wire on TRIG (GPIO 5) or ECHO (GPIO 18). | Check breadboard connections. Verify HC-SR04 VCC is connected to `VIN` (5V rail) and GND is connected to ESP32 GND. |
| **PlatformIO upload fails (Port not found)** | Micro-USB cable is charge-only or driver missing. | Use a micro-USB cable that supports data transfer. Install the CP2102 or CH340 USB-to-UART bridge VCP driver. |
| **Dashboard shows "Stale Data Warning"** | ESP32 is powered off or disconnected from Wi-Fi. | Verify ESP32 power and Wi-Fi credentials in `src/config.h`. Check Serial Monitor output. |

---

## 13. License & Academic Attribution

This project is submitted in partial fulfillment of coursework in Internet of Things (IoT) and Embedded Systems. Free to use for academic study and research.
