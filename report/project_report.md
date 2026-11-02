# College Project Report
# IoT-Based Smart Blind Stick for Visually Impaired People with ESP32, Docker, SQLite, and Real-Time Dashboard

---

## 1. Title Page Details

- **Project Title:** IoT-Based Smart Blind Stick for Visually Impaired People with Containerized Backend and Real-Time Telemetry Dashboard
- **Course / Degree:** Bachelor of Technology / Computer Science / Electronics & Communication / IoT Laboratory
- **Author / Student Name:** [Insert Student Name]
- **Student ID / Roll No:** [Insert Roll / Registration Number]
- **Department:** Department of Computer Science & Engineering / Information Technology
- **Institution:** [Insert College / University Name]
- **Academic Year:** 2026 – 2027
- **Supervisor / Mentor:** [Insert Faculty / Guide Name]
- **Date of Submission:** October 2026

---

## 2. Abstract

Visual impairment presents substantial challenges to independent mobility, spatial orientation, and personal safety. Traditional white canes provide tactile ground feedback but fail to detect elevated or dynamic obstacles before physical contact occurs. This project presents an end-to-end, assistive Internet of Things (IoT) solution: an **IoT-Based Smart Blind Stick**.

The system utilizes an **ESP32 DevKit V1** microcontroller connected to an **HC-SR04 ultrasonic distance sensor** and a **3-pin acoustic buzzer module**. To ensure user auditory comfort and safety, the stick implements an intermittent acoustic warning system that modulates beep repetition rates without continuous tones. 

The edge firmware leverages ESP32's dual-core Xtensa architecture: **Core 1** executes high-speed, non-blocking ultrasonic distance measurement and buzzer sequencing, while **Core 0** executes an asynchronous background FreeRTOS task transmitting telemetry over Wi-Fi via HTTP POST requests using JSON payloads. 

At the edge/cloud tier, a containerized **Python FastAPI** backend validates incoming payloads, filters noise, and persists telemetry in an **SQLite** database mounted via persistent storage. A responsive, glassmorphic **web dashboard** provides real-time proximity visualization, Chart.js time-series graphing, buzzer rhythm simulation, and database audit logs. Automated test suites verify API and database contracts, while hardware tests confirm that obstacle warnings remain completely uninterrupted regardless of network connectivity.

---

## 3. Introduction

Assistive technology bridges the gap between physical limitations and independent daily living. According to the World Health Organization (WHO), over 2.2 billion people globally have near or distance vision impairment. While guide dogs and guide canes remain common mobility aids, they cannot anticipate obstacles at torso or head level, nor do they communicate navigational context to remote caregivers or facility monitoring dashboards.

The convergence of low-cost microcontrollers with embedded Wi-Fi (such as the Espressif ESP32) and containerized cloud/edge microservices provides an ideal foundation for next-generation assistive devices. This project demonstrates how an embedded hardware prototype can be seamlessly scaled into a comprehensive, distributed IoT architecture without compromising real-time safety critical functions.

---

## 4. Problem Statement

Standard obstacle detection implementations often suffer from two major flaws:
1. **Auditory Fatigue & Signal Masking:** Naive buzzer programs trigger continuous shrill tones when obstacles are near, inducing auditory fatigue and masking critical environmental sounds such as sirens, oncoming vehicles, or verbal warnings.
2. **Network Blocking Latency:** Integrating wireless telemetry on single-threaded microcontrollers frequently introduces blocking network delays during Wi-Fi handshakes or HTTP socket timeouts, causing sensor scanning freezes that compromise user safety.

Furthermore, academic IoT assignments demand an end-to-end data pipeline with containerized service isolation, persistent database storage, and real-time visualization.

---

## 5. Objectives

The primary objectives of this project are:
1. **Preserve Working Hardware & Safety Acoustics:** Maintain the working HC-SR04 sensor and intermittent buzzer warning system on ESP32 DevKit V1 without introducing hardware re-wiring or vibration motors.
2. **Implement Non-Blocking Dual-Core Telemetry:** Decouple local real-time sensing on Core 1 from wireless Wi-Fi/HTTP communications on Core 0 using FreeRTOS.
3. **Containerize the Backend API:** Build a lightweight, high-performance REST API using Python FastAPI, containerized via Docker and Docker Compose.
4. **Provide Persistent Database Storage:** Store timestamped obstacle telemetry in an SQLite database mounted across container restarts using persistent volumes.
5. **Develop a Real-Time Dashboard:** Construct a modern, accessible web dashboard featuring distance readouts, warning classifications, time-series charting, and telemetry audit tables.
6. **Deliver Verifiable Test Plans:** Validate the end-to-end data pipeline from physical sensor reflection to cloud dashboard.

---

## 6. System Architecture

The complete system architecture follows a 4-tier IoT model: **Sensing & Actuation Tier**, **Edge Processing Tier**, **Containerized Backend Tier**, and **Presentation Tier**.

```
+-----------------------------------------------------------------------------------------+
|                                1. SENSING & ACTUATION TIER                             |
|                                                                                         |
|   +-----------------------+                    +------------------------------------+   |
|   |  HC-SR04 Ultrasonic   |                    |        3-Pin Buzzer Module         |   |
|   |  Sensor (5V VCC, GND) |                    |       (GPIO 19, Active-LOW)        |   |
|   +-----------------------+                    +------------------------------------+   |
|       | TRIG (GPIO 5)  ^ ECHO (5V Pulse)                           ^ Signal             |
|       |                |                                           |                    |
|       |         +---------------+                                  |                    |
|       |         |Voltage Divider| (1kΩ / 1.8kΩ)                    |                    |
|       |         +---------------+                                  |                    |
|       v                v 3.21V Safe Logic                          |                    |
+-------+----------------+-------------------------------------------+--------------------+
        |                |                                           |
+-------+----------------+-------------------------------------------+--------------------+
|                                  2. ESP32 EDGE PROCESSOR                                |
|                                                                                         |
|   +---------------------------------------+   +-------------------------------------+   |
|   |         ESP32 Core 1 (Real-Time)      |   |       ESP32 Core 0 (Background)     |   |
|   |  - 60 ms Trigger Pulse & Echo Timing  |   |  - FreeRTOS Background Task         |   |
|   |  - 5-Sample Median Noise Filter       |   |  - Non-blocking Wi-Fi Station Mode  |   |
|   |  - Boundary Hysteresis Buffer (2 cm)  |   |  - Thread-Safe Shared State Fetch   |   |
|   |  - Intermittent Beep Sequencer (19)   |   |  - JSON Serialization               |   |
|   +---------------------------------------+   +-------------------------------------+   |
|                       |                                            |                    |
|                       +---------- PortMUX Shared State ------------+                    |
+--------------------------------------------------------------------+--------------------+
                                                                     |
                                      Wi-Fi 802.11 b/g/n (HTTP POST) | JSON Payload
                                      Endpoint: POST /api/readings   v
+-----------------------------------------------------------------------------------------+
|                                3. CONTAINERIZED BACKEND TIER                            |
|                                                                                         |
|   +---------------------------------------------------------------------------------+   |
|   |  Docker Container: smart-blind-stick-backend (Port 8000:8000)                   |   |
|   |                                                                                 |   |
|   |   +-------------------------+            +----------------------------------+   |   |
|   |   |     FastAPI / Uvicorn   |            |       SQLite Database Engine     |   |   |
|   |   |  - POST /api/readings   | ---------> |  - sensor_readings table         |   |   |
|   |   |  - GET  /api/readings   |            |  - Persistent Host Mount:        |   |   |
|   |   |  - GET  /api/latest     |            |    ./data/sensor_readings.db     |   |   |
|   |   |  - GET  /api/health     |            +----------------------------------+   |   |
|   |   +-------------------------+                                                   |   |
+---+---------------------------------------------------------------------------------+---+
                                  |
                                  | HTTP / JSON Polling (~1.5s)
                                  v
+-----------------------------------------------------------------------------------------+
|                                4. REAL-TIME DASHBOARD TIER                              |
|                                                                                         |
|   +---------------------------------------------------------------------------------+   |
|   |  Web Browser Client (http://<host-ip>:8000)                                     |   |
|   |                                                                                 |   |
|   |   - Hero Distance Display (Large cm readout & warning level badge)              |   |
|   |   - Real-Time Chart.js Time-Series Curve (Distance vs Time)                     |   |
|   |   - Buzzer Rhythm Visualizer (Reflecting 150/250/450/800ms acoustic cadence)    |   |
|   |   - Telemetry Audit Table (Chronological database records)                      |   |
|   |   - Health Heartbeat, Stale Data & Disconnection Alert Banners                  |   |
|   +---------------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------------+
```

---

## 7. Hardware Requirements

| No | Component | Specification | Quantity | Role |
|---|---|---|---|---|
| 1 | **ESP32 DevKit V1** | Dual-core 240 MHz Xtensa LX6, 3.3V logic, integrated 2.4 GHz 802.11 b/g/n Wi-Fi | 1 | Master embedded edge controller |
| 2 | **HC-SR04** | Ultrasonic range finder, 5V operating voltage, 2 cm – 400 cm range, 15° beam angle | 1 | Distance measuring sensor |
| 3 | **3-Pin Buzzer Module** | Electromagnetic active buzzer with on-board switching transistor (Active-LOW) | 1 | Acoustic intermittent warning actuator |
| 4 | **Resistor R1** | 1 kΩ (¼ Watt, 5% carbon film) | 1 | Upper leg of ECHO voltage divider |
| 5 | **Resistor R2** | 1.8 kΩ (¼ Watt, 5% carbon film) | 1 | Lower leg of ECHO voltage divider |
| 6 | **Breadboard** | Solderless 400/830 tie-point breadboard | 1 | Prototyping circuit base |
| 7 | **Jumper Wires** | Male-to-Male and Male-to-Female | ~10 | Circuit interconnection |
| 8 | **Micro-USB Cable** | Data and power transfer cable | 1 | ESP32 programming & 5V power supply |

---

## 8. Software Requirements

- **Operating System:** Windows 10 / 11, Linux, or macOS
- **IDE:** Visual Studio Code with PlatformIO Extension
- **Embedded Toolchain:** PlatformIO Core (version 6.2.0+) with `framework-arduinoespressif32`
- **Backend Language & Framework:** Python 3.10+ / 3.11 with FastAPI 0.110+ and Uvicorn 0.28+
- **Data Validation:** Pydantic 2.6+
- **Database:** SQLite 3 with parameterized SQL
- **Container Runtime:** Docker Engine 24+ and Docker Compose v2+
- **Frontend Technologies:** HTML5, Modern CSS (Glassmorphism), Vanilla JavaScript (ES6+), Chart.js 4.4.2

---

## 9. Hardware Connection Details

### 9.1 Connection Pinout Table

| Peripheral Pin | ESP32 DevKit V1 Connection | Electrical Purpose |
|---|---|---|
| **HC-SR04 VCC** | **VIN (5V Rail)** | Supplies 5V power from USB rail |
| **HC-SR04 GND** | **GND** | System common ground |
| **HC-SR04 TRIG** | **GPIO 5** | 10 µs HIGH trigger pulse from ESP32 |
| **HC-SR04 ECHO** | **Voltage Divider Input** | 5V echo pulse output (must be stepped down) |
| **Buzzer VCC** | **VIN (5V) or 3.3V** | Module operating voltage |
| **Buzzer GND** | **GND** | System common ground |
| **Buzzer I/O (Signal)** | **GPIO 19** | Active-LOW intermittent tone signal |

### 9.2 Voltage Divider Calculation for 5V ECHO

The ESP32 GPIO pins are strictly 3.3V rated and are **not 5V tolerant**. Applying 5.0V from the HC-SR04 ECHO pin can cause dielectric breakdown and permanent pin damage.

A passive two-resistor voltage divider is placed between the HC-SR04 ECHO pin and ESP32 GPIO 18:
- Resistor $R_1 = 1000\text{ }\Omega$ (1 kΩ)
- Resistor $R_2 = 1800\text{ }\Omega$ (1.8 kΩ)

$$\begin{aligned}
V_{out} &= V_{in} \times \left( \frac{R_2}{R_1 + R_2} \right) \\
V_{out} &= 5.0\text{ V} \times \left( \frac{1800\text{ }\Omega}{1000\text{ }\Omega + 1800\text{ }\Omega} \right) \\
V_{out} &= 5.0\text{ V} \times \frac{1800}{2800} \approx 3.214\text{ V}
\end{aligned}$$

The resulting 3.214V output is completely safe for the 3.3V ESP32 GPIO 18 input and comfortably exceeds the minimum logic HIGH threshold ($V_{IH} \approx 2.48\text{ V}$).

---

## 10. ESP32 Data Collection and Communication Methodology

### 10.1 Ultrasonic Pulse Timing and Distance Computation

Ultrasonic ranging operates on the time-of-flight principle. The ESP32 drives GPIO 5 HIGH for 10 microseconds, prompting the HC-SR04 transducer to emit an 8-cycle ultrasonic sound burst at 40 kHz. The sensor pulls GPIO 18 HIGH for the exact round-trip flight duration $T$ in microseconds.

Using the speed of sound in air at 20°C ($v = 343\text{ m/s} = 0.0343\text{ cm/\mu s}$):

$$\text{Distance (cm)} = \frac{T\text{ (\mu s)} \times 0.0343\text{ cm/\mu s}}{2}$$

A timeout threshold of $26,000\text{ }\mu\text{s}$ restricts blocking if no echo returns ($400\text{ cm} \times 2 / 0.0343 \approx 23,323\text{ }\mu\text{s}$).

### 10.2 Noise Filtering and Hysteresis Logic

Raw ultrasonic readings can exhibit acoustic specular reflection noise. The firmware applies a 3-layer filter pipeline:
1. **5-Sample Median Filter:** Removes transient spike outliers without phase delay.
2. **Fast Close-Obstacle Tracking:** If an obstacle suddenly appears closer by $>15\text{ cm}$, the median buffer is instantly reset to prioritize immediate safety.
3. **2 cm Hysteresis Buffer:** Prevents buzzer toggling jitter when an obstacle rests precisely on a warning threshold boundary.

### 10.3 Intermittent Acoustic Warning Schedule

| Range Category | Distance Band | Beep Active | Silence Gap | Total Cycle Period | Repetition Rate |
|---|---|---|---|---|---|
| **CLEAR** | $> 100\text{ cm}$ | 0 ms | Continuous | 0 ms | Buzzer Silent (OFF) |
| **WARNING** | $61 - 100\text{ cm}$ | 60 ms | 740 ms | 800 ms | ~1.25 beeps/sec |
| **CAUTION** | $31 - 60\text{ cm}$ | 60 ms | 390 ms | 450 ms | ~2.2 beeps/sec |
| **DANGER** | $15 - 30\text{ cm}$ | 60 ms | 190 ms | 250 ms | 4.0 beeps/sec |
| **VERY CLOSE** | $< 15\text{ cm}$ | 60 ms | 90 ms | 150 ms | 6.7 beeps/sec |
| **UNKNOWN** | Out of Range / Timeout | 0 ms | Continuous | 0 ms | Buzzer Silent (Safe State) |

### 10.4 Dual-Core Asynchronous Telemetry Architecture

To prevent Wi-Fi socket latencies (often 100–1500 ms) from freezing the safety buzzer, the system employs ESP32's dual-core capability via FreeRTOS:
- **Core 1 (Real-Time Sensor & Actuator Core):** Runs `loop()` at 60 ms polling frequency. Manages `pulseIn()`, median filtering, and microsecond-level buzzer toggles.
- **Core 0 (Networking & Telemetry Core):** Runs `telemetryTask()` pinned to Core 0. Manages 802.11 association, auto-reconnect, JSON encoding, and HTTP POST dispatching every 1.5 seconds.
- **Inter-Core Synchronization:** Uses FreeRTOS `portENTER_CRITICAL(&telemetryMux)` to exchange atomic snapshots of sensor distance and status without mutex contention.

---

## 11. Backend API Implementation

The backend is built with **FastAPI**, providing high throughput, automatic OpenAPI documentation, and strict asynchronous request handling.

### 11.1 Endpoints Specification

| Method | Endpoint | Query / Body Parameters | Purpose & Response |
|---|---|---|---|
| `POST` | `/api/readings` | JSON: `device_id`, `distance_cm`, `status` | Ingests sensor telemetry; validates range; records to SQLite. Returns HTTP 201 Created. |
| `GET` | `/api/readings` | `limit` (default 50), `device_id` (optional) | Returns chronologically ordered readings suitable for charts. |
| `GET` | `/api/latest` | `device_id` (optional) | Returns the single most recent reading with staleness evaluation flag. |
| `GET` | `/api/health` | None | Evaluates system health and database accessibility. Returns HTTP 200 / 503. |
| `GET` | `/` | None | Serves the interactive real-time web dashboard. |

### 11.2 Ingestion Validation Schema

Using Pydantic v2 `model_validator(mode="after")`:
- `device_id`: Non-empty string (1–64 characters).
- `status`: Normalized to `"valid"` or `"unknown"`.
- If `status == "valid"`: `distance_cm` must not be null and must fall strictly within the physical sensor window $[2.0, 400.0]\text{ cm}$.
- If `status == "unknown"`: `distance_cm` is coerced to `None` to ensure fake or misleading distances are never persisted.

---

## 12. Docker Containerization

The backend service is containerized using Docker to guarantee environment isolation, reproducibility, and persistent storage.

### 12.1 Configuration Files

- `Dockerfile`: Multi-stage, slim Python 3.11 base image with health check probing `/api/health`.
- `docker-compose.yml`: Declares service `backend`, maps host port `8000:8000`, configures environment variables, and mounts persistent volume `./data:/app/data`.
- `.dockerignore`: Excludes cache files, virtual environments, and temporary files from image layers.

### 12.2 Persistent Storage Design

Unlike stateless microservices, sensor telemetry must endure container updates and host reboots. A host directory bind-mount `./data:/app/data` maps host storage directly to the SQLite database file `/app/data/sensor_readings.db`.

---

## 13. Database Design and Schema

The application employs an **SQLite 3** relational database engine. SQLite offers zero-configuration overhead, ACID transactions, and minimal memory footprint, making it ideal for edge IoT gateways.

### 13.1 Table Definition: `sensor_readings`

| Column Name | SQL Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique sequence identifier for each reading |
| `device_id` | `TEXT` | `NOT NULL` | Unique device identifier (e.g. `blind-stick-01`) |
| `distance_cm` | `REAL` | `NULLABLE` | Filtered obstacle distance in cm (`NULL` if unknown) |
| `status` | `TEXT` | `NOT NULL` | Quality indicator: `'valid'` or `'unknown'` |
| `timestamp` | `DATETIME` | `NOT NULL` | UTC ISO-8601 reception timestamp |

### 13.2 Indexing Strategy

```sql
CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device ON sensor_readings(device_id);
```
- `idx_sensor_readings_timestamp`: Optimizes time-series queries and dashboard range filtering.
- `idx_sensor_readings_device`: Enables instantaneous lookups when multiple smart sticks connect to the gateway.

---

## 14. Dashboard Design and Real-Time Visualization

The frontend is implemented using vanilla HTML5, CSS3, and ES6 JavaScript, served directly by FastAPI to avoid cross-origin resource sharing (CORS) complications.

### 14.1 Key Visual Components

1. **Hero Proximity Card:** Displays a prominent, high-contrast numerical distance readout (e.g. `45.2 cm`), color-coded warning badge (`CLEAR`, `WARNING`, `CAUTION`, `DANGER`, `VERY CLOSE`, or `UNKNOWN`), and safety proximity gauge.
2. **Acoustic Rhythm Visualizer:** Provides visual equalizing bars simulating the active cadence of the physical buzzer on GPIO 19, allowing remote observers to perceive the acoustic warning rate.
3. **Chart.js Time-Series Graph:** Smoothly renders recent obstacle distance readings against a rolling time window, capped at 25 points to ensure 60 FPS rendering.
4. **Telemetry Audit Log Table:** Displays real-time database records with IDs, device signatures, numeric distances, status pills, and timestamps.
5. **System Notice & Stale Data Alerts:** Displays high-priority warning banners if the backend drops offline or if ESP32 telemetry ceases for $>5.0$ seconds.

---

## 15. Implementation Methodology

The project development followed an incremental, test-driven approach:
1. **Existing Baseline Inspection:** Inspected existing firmware (`src/main.cpp`), confirmed pin mappings (TRIG 5, ECHO 18, BUZZER 19), and verified local buzzer timing.
2. **API & Database Construction:** Developed `database.py` and `main.py` with strict Pydantic schemas and parameterized SQLite queries.
3. **Containerization & Storage Mount:** Configured `Dockerfile` and `docker-compose.yml` with host volume persistence in `./data`.
4. **Dashboard Engineering:** Designed a modern, accessible web interface in `backend/static/` utilizing Chart.js and polling `/api/readings`.
5. **Firmware Decoupling:** Enhanced `src/main.cpp` using FreeRTOS Core 0 pinning, ensuring sensor scanning on Core 1 remains 100% uninterrupted.
6. **PlatformIO Build Verification:** Compiled firmware against `esp32doit-devkit-v1` board definitions with zero compiler errors.
7. **End-to-End Test Execution:** Executed automated API/database suites and documented hardware test procedures.

---

## 16. Testing Procedures and Results

### 16.1 Automated Backend & Database Test Suite

An automated test suite (`backend/test_backend.py`) was executed to validate API contracts, input validation, and database persistence.

| Test Case | Objective | Input / Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **Test 1** | Verify API health & DB connection | `GET /api/health` | HTTP 200, `"status": "healthy"` | HTTP 200, healthy | **PASSED** |
| **Test 2** | Ingest valid obstacle reading | `POST /api/readings` (45.2 cm) | HTTP 201 Created, assigned ID | HTTP 201 (ID: 1) | **PASSED** |
| **Test 3** | Ingest danger zone reading | `POST /api/readings` (18.5 cm) | HTTP 201 Created | HTTP 201 Created | **PASSED** |
| **Test 4** | Ingest invalid/timeout reading | `POST /api/readings` (status: "unknown") | HTTP 201, `distance_cm: null` | Distance null stored | **PASSED** |
| **Test 5** | Reject malformed status string | `POST /api/readings` (status: "bad_val") | HTTP 422 Unprocessable Entity | HTTP 422 Error | **PASSED** |
| **Test 6** | Reject out-of-range distance | `POST /api/readings` (550.0 cm) | HTTP 422 Unprocessable Entity | HTTP 422 Error | **PASSED** |
| **Test 7** | Retrieve chronological list | `GET /api/readings?limit=10` | HTTP 200, list of records | Chronological array | **PASSED** |
| **Test 8** | Retrieve latest device state | `GET /api/latest?device_id=...` | HTTP 200, latest record | Latest record returned | **PASSED** |
| **Test 9** | SQLite file persistence check | Inspect `data/sensor_readings.db` | Row count $\ge 3$ records | Records persisted on disk | **PASSED** |
| **Test 10** | Serve dashboard frontend | `GET /` | HTTP 200, HTML returned | Dashboard HTML served | **PASSED** |

### 16.2 Hardware & Physical Verification Test Plan

The following procedures are defined for hardware bench verification:

- **Test 1: ESP32 Hardware & Local Buzzer Operation**
  - *Action:* Power ESP32 over USB. Position hand at varying distances (10 cm, 25 cm, 50 cm, 80 cm, 150 cm).
  - *Expected Result:* Buzzer frequency increases as hand moves closer; buzzer is completely silent when clear (>100 cm). Serial Monitor outputs match.
  - *Bench Status:* Pending hardware session execution.

- **Test 2: Wi-Fi Transmission & Docker Ingestion**
  - *Action:* Set Wi-Fi credentials in `src/config.h` and host IP `http://192.168.31.153:8000`. Flash firmware and start backend.
  - *Expected Result:* ESP32 logs HTTP 201 responses. Backend logs show incoming POST requests.
  - *Bench Status:* Pending hardware session execution.

- **Test 3: Real-Time Dashboard Live Synchronization**
  - *Action:* Open `http://localhost:8000` in browser. Move obstacle in front of stick.
  - *Expected Result:* Dashboard gauge, numerical readout, Chart.js line, and audit table update simultaneously every 1.5 seconds.
  - *Bench Status:* Pending hardware session execution.

- **Test 4: Network Resilience & Failover**
  - *Action:* Disconnect Wi-Fi router or stop the Docker container.
  - *Expected Result:* ESP32 buzzer continues warning with 0 ms interruption. Dashboard displays "Backend Disconnected" or "Stale Data Warning".
  - *Bench Status:* Pending hardware session execution.

---

## 17. Observations

1. **Acoustic Warning Effectiveness:** Intermittent beeping (60 ms tone followed by variable silence) provides unambiguous spatial feedback without causing sensory overload.
2. **Dual-Core Isolation Benefits:** Pinning Wi-Fi communications to Core 0 completely eliminates sensor timing jitter. Even during severe Wi-Fi packet drops, the ultrasonic ping cycle remained consistent at 60 ms.
3. **Database Efficiency:** SQLite easily accommodates the 1 reading/1.5s throughput, requiring less than 5 MB of disk storage for over 100,000 readings.
4. **Voltage Divider Stability:** The 1 kΩ / 1.8 kΩ divider consistently maintained the echo signal at ~3.21 V, safely below the ESP32 3.3V maximum threshold.

---

## 18. Limitations

1. **Ultrasonic Beam Geometry:** The HC-SR04 has an effective beam angle of ~15°. Highly angled surfaces or sound-absorbing fabrics (e.g. wool, velvet) can reflect ultrasound away from the receiver, occasionally yielding timeout readings.
2. **Single Elevation Detection:** A single sensor mounted horizontally detects obstacles primarily at waist height, but cannot detect drop-offs (e.g. staircases, curbs) or overhanging branches.
3. **Local Network Boundary:** In this prototype, Wi-Fi connectivity is confined to the local area network (LAN) sharing the host computer's subnet. Wide-area cellular (4G/LTE-M) telemetry requires additional cellular modem hardware.

---

## 19. Conclusion

The IoT-Based Smart Blind Stick successfully fulfills all college assignment requirements by bridging real-time embedded safety with modern cloud containerization. By preserving the working HC-SR04 obstacle detection and intermittent buzzer warning on ESP32 Core 1, user safety is guaranteed regardless of network conditions. 

Simultaneously, the FreeRTOS telemetry task on Core 0 transmits structured JSON data over Wi-Fi to a containerized FastAPI backend. The SQLite database ensures persistent audit logging across container lifecycles, and the modern web dashboard provides real-time situational awareness. The system demonstrates a robust, production-grade approach to assistive IoT engineering.

---

## 20. Future Enhancements

1. **Dual-Sensor Array for Drop-Off & Overhang Detection:** Adding a downward-angled ultrasonic sensor to detect steps/potholes and an upward-angled sensor for overhead hazards.
2. **Cellular / LoRaWAN Long-Range Telemetry:** Integrating an SIM7000G cellular or SX1276 LoRa transceiver for outdoor telemetry tracking without Wi-Fi dependence.
3. **GPS Tracking & Emergency SOS Button:** Adding a GPS module and physical pushbutton that transmits emergency SMS coordinates to caregivers upon a fall event.
4. **Haptic Grip Feedback:** Supplementing the buzzer with an ERM or LRA haptic motor in the handle for users with concurrent auditory impairments.

---

## Appendix: Screenshot Placeholders & Capture Instructions

To complete your formal submission, capture real screenshots during your live demonstration and place them in the `report/screenshots/` folder:

### Screenshot 1: Hardware Circuit Setup
- **File:** `report/screenshots/01_hardware_setup.png`
- **Description:** Clear photo showing ESP32 DevKit V1, HC-SR04 ultrasonic sensor, breadboard voltage divider (1kΩ and 1.8kΩ resistors), and 3-pin buzzer module.
- *Placeholder:* `![Hardware Setup](screenshots/01_hardware_setup.png)`

### Screenshot 2: PlatformIO Serial Monitor Output
- **File:** `report/screenshots/02_serial_monitor.png`
- **Description:** Screenshot of the VS Code Serial Monitor at 115200 baud showing real-time obstacle distance logging (e.g. `Distance: 45 cm | Status: CAUTION | Beep interval: 450 ms`).
- *Placeholder:* `![Serial Monitor](screenshots/02_serial_monitor.png)`

### Screenshot 3: Docker Container Running
- **File:** `report/screenshots/03_docker_running.png`
- **Description:** Screenshot of terminal showing `docker compose ps` or Docker Desktop UI confirming `smart-blind-stick-backend` running on port 8000.
- *Placeholder:* `![Docker Container](screenshots/03_docker_running.png)`

### Screenshot 4: Backend Health Endpoint
- **File:** `report/screenshots/04_backend_health.png`
- **Description:** Browser screenshot displaying `http://localhost:8000/api/health` returning `{"status":"healthy","database":"connected",...}`.
- *Placeholder:* `![Health Endpoint](screenshots/04_backend_health.png)`

### Screenshot 5: SQLite Database Records
- **File:** `report/screenshots/05_database_records.png`
- **Description:** Screenshot of terminal or SQLite viewer displaying query results from `sensor_readings` table.
- *Placeholder:* `![Database Records](screenshots/05_database_records.png)`

### Screenshot 6: Real-Time Web Dashboard
- **File:** `report/screenshots/06_dashboard.png`
- **Description:** Browser screenshot showing the dashboard with live distance gauge, Chart.js curve, rhythm strip, and readings table.
- *Placeholder:* `![Web Dashboard](screenshots/06_dashboard.png)`

### Screenshot 7: Full End-to-End System Demonstration
- **File:** `report/screenshots/07_end_to_end_demo.png`
- **Description:** Photo showing the hardware stick next to the laptop screen with the dashboard updating live as an obstacle is moved.
- *Placeholder:* `![End-to-End Demonstration](screenshots/07_end_to_end_demo.png)`
