/**
 * @file main.cpp
 * @brief IoT-Based Smart Blind Stick for Visually Impaired People
 * 
 * Hardware:
 *   - ESP32 DevKit V1
 *   - HC-SR04 Ultrasonic Distance Sensor
 *   - 3-Pin Buzzer Module (Active-HIGH / Active-LOW configurable)
 * 
 * Pin Connections:
 *   - HC-SR04 TRIG -> ESP32 GPIO 5
 *   - HC-SR04 ECHO -> ESP32 GPIO 18 (via 1kΩ / 1.8kΩ voltage divider)
 *   - Buzzer I/O   -> ESP32 GPIO 19
 *   - Common GND for all components
 * 
 * Architecture:
 *   - Core 1: Non-blocking ultrasonic measurement, median filtering, and intermittent buzzer sequencer.
 *   - Core 0: Background FreeRTOS task managing Wi-Fi connectivity and HTTP JSON telemetry transmission.
 *   - Dual-core separation guarantees that network latency NEVER interferes with local obstacle warnings!
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include "esp_wifi.h"
#include "config.h"

// ============================================================================
// HARDWARE PIN DEFINITIONS (Preserved)
// ============================================================================
const int PIN_TRIG   = 5;   // HC-SR04 Trigger Pin
const int PIN_ECHO   = 18;  // HC-SR04 Echo Pin (connected via voltage divider)
const int PIN_BUZZER = 19;  // 3-Pin Buzzer Module I/O Pin

// ============================================================================
// BUZZER POLARITY CONFIGURATION (Preserved)
// ============================================================================
// Set to true for active-LOW buzzer modules (sounds when pin is LOW, silent on HIGH).
// Set to false for active-HIGH buzzer modules (sounds when pin is HIGH, silent on LOW).
// Active-LOW is standard for most 3-pin buzzer modules.
const bool BUZZER_ACTIVE_LOW = true;

// ============================================================================
// DETECTION & TIMING CONSTANTS (Preserved)
// ============================================================================
// Speed of sound in dry air at 20°C: ~0.0343 cm/microsecond (343 m/s)
const float SOUND_SPEED_CM_PER_US = 0.0343f;

// HC-SR04 measurement timeout (microseconds):
// 400 cm maximum distance * 2 (round trip) / 0.0343 ≈ 23323 µs.
// A timeout of 26000 µs prevents the code from blocking if no echo is returned.
const unsigned long ECHO_TIMEOUT_US = 35000UL;

// Minimum and maximum valid distance limits for HC-SR04 in cm
const float MIN_VALID_DISTANCE_CM = 2.0f;
const float MAX_VALID_DISTANCE_CM = 500.0f;

// Beep duration: Short, intermittent audible pulse (50–70 ms)
// The buzzer NEVER stays continuously ON, even at the closest distance!
const unsigned long BEEP_DURATION_MS = 60UL;

// Interval between sensor distance readings (ms)
// Gives time for ultrasonic sound reflections to dissipate between pings.
const unsigned long SENSOR_INTERVAL_MS = 60UL;

// Serial output update interval (ms)
const unsigned long SERIAL_LOG_INTERVAL_MS = 250UL;

// Hysteresis buffer (cm) to prevent flickering near warning zone boundaries
const float HYSTERESIS_CM = 2.0f;

// ============================================================================
// WARNING LEVELS (Preserved)
// ============================================================================
enum WarningLevel {
    LEVEL_UNKNOWN,    // Sensor timeout or invalid measurement
    LEVEL_CLEAR,      // > 100 cm (Buzzer OFF)
    LEVEL_WARNING,    // 61 - 100 cm (Beep every ~800 ms)
    LEVEL_CAUTION,    // 31 - 60 cm (Beep every ~450 ms)
    LEVEL_DANGER,     // 15 - 30 cm (Beep every ~250 ms)
    LEVEL_VERY_CLOSE  // < 15 cm (Beep every ~150 ms)
};

// ============================================================================
// FILTERING CONFIGURATION (Preserved)
// ============================================================================
const int FILTER_SIZE = 5;
float filterBuffer[FILTER_SIZE];
int filterIndex = 0;
int filterSampleCount = 0;

// Maximum consecutive invalid readings before declaring sensor state UNKNOWN
const int MAX_CONSECUTIVE_INVALID = 3;
int consecutiveInvalidCount = 0;

// ============================================================================
// GLOBAL STATE VARIABLES
// ============================================================================
WarningLevel currentLevel = LEVEL_CLEAR;
int currentBeepIntervalMs = 0;
float currentDistanceCm = -1.0f;
bool isSensorReadingValid = false;

// Non-blocking timer timestamps
unsigned long lastSensorSampleTime = 0;
unsigned long lastSerialLogTime = 0;
unsigned long lastBeepCycleStartTime = 0;
bool isBuzzerCurrentlyOn = false;

// ============================================================================
// INTER-CORE THREAD-SAFE TELEMETRY STATE
// ============================================================================
// Core 1 writes sensor values; Core 0 reads them for HTTP transmission
portMUX_TYPE telemetryMux = portMUX_INITIALIZER_UNLOCKED;
float sharedDistanceCm = -1.0f;
bool sharedIsValid = false;

// ============================================================================
// FUNCTION DECLARATIONS
// ============================================================================
void setBuzzer(bool state);
bool readRawDistanceCm(float &distanceOut);
bool filterDistance(float rawDist, bool isValid, float &filteredDistOut);
WarningLevel calculateWarningLevel(float distanceCm, WarningLevel previousLevel, int &intervalOut);
void updateBuzzerPattern(unsigned long currentMillis, WarningLevel level, int intervalMs);
void printSerialStatus(unsigned long currentMillis);
void telemetryTask(void *pvParameters);

// ============================================================================
// ARDUINO SETUP
// ============================================================================
void setup() {
    // Initialize Serial Monitor at 115200 baud
    Serial.begin(115200);
    delay(200);

    Serial.println();
    Serial.println("====================================================");
    Serial.println(" IoT Smart Blind Stick - ESP32 DevKit V1 Initialized ");
    Serial.println("====================================================");
    Serial.printf("Buzzer Polarity: %s\n", BUZZER_ACTIVE_LOW ? "ACTIVE-LOW" : "ACTIVE-HIGH");
    Serial.printf("Configured Device ID: %s\n", DEVICE_ID);
    Serial.printf("Configured Backend URL: %s%s\n", BACKEND_BASE_URL, BACKEND_ENDPOINT);
    Serial.println("System starting non-blocking obstacle scanning...");
    Serial.println();

    // Configure GPIO Pins safely
    digitalWrite(PIN_TRIG, LOW);
    digitalWrite(PIN_BUZZER, BUZZER_ACTIVE_LOW ? HIGH : LOW); // Set OFF level before enabling output
    pinMode(PIN_TRIG, OUTPUT);
    pinMode(PIN_ECHO, INPUT);
    pinMode(PIN_BUZZER, OUTPUT);
    setBuzzer(false); // Ensure buzzer starts completely OFF

    // Initialize filter buffer
    for (int i = 0; i < FILTER_SIZE; i++) {
        filterBuffer[i] = 0.0f;
    }

    // Launch background telemetry task on Core 0
    // Stack size set to 10240 to support MbedTLS HTTPS operations without stack overflow
    xTaskCreatePinnedToCore(
        telemetryTask,        // Function to implement the task
        "TelemetryTask",      // Name of the task
        10240,                // Stack size in words (expanded for MbedTLS HTTPS)
        NULL,                 // Task input parameter
        1,                    // Priority of the task
        NULL,                 // Task handle
        0                     // Core where the task should run (0 = background, 1 = Arduino loop)
    );
}

// ============================================================================
// ARDUINO MAIN LOOP (Runs on Core 1)
// ============================================================================
void loop() {
    unsigned long currentMillis = millis();

    // 1. NON-BLOCKING SENSOR MEASUREMENT & FILTERING
    if (currentMillis - lastSensorSampleTime >= SENSOR_INTERVAL_MS) {
        lastSensorSampleTime = currentMillis;

        float rawDistance = 0.0f;
        bool isRawValid = readRawDistanceCm(rawDistance);

        float filteredDistance = 0.0f;
        isSensorReadingValid = filterDistance(rawDistance, isRawValid, filteredDistance);

        if (isSensorReadingValid) {
            currentDistanceCm = filteredDistance;
            int newIntervalMs = 0;
            currentLevel = calculateWarningLevel(currentDistanceCm, currentLevel, newIntervalMs);
            currentBeepIntervalMs = newIntervalMs;
        } else {
            // Sensor produced invalid readings or timed out
            currentLevel = LEVEL_UNKNOWN;
            currentBeepIntervalMs = 0;
            currentDistanceCm = -1.0f;
        }

        // Thread-safe update of shared telemetry values for Core 0
        portENTER_CRITICAL(&telemetryMux);
        sharedDistanceCm = currentDistanceCm;
        sharedIsValid = isSensorReadingValid;
        portEXIT_CRITICAL(&telemetryMux);
    }

    // 2. NON-BLOCKING INTERMITTENT BUZZER CONTROLLER
    // Evaluated continuously every loop iteration without blocking delays
    updateBuzzerPattern(currentMillis, currentLevel, currentBeepIntervalMs);

    // 3. PERIODIC SERIAL MONITOR LOGGING
    if (currentMillis - lastSerialLogTime >= SERIAL_LOG_INTERVAL_MS) {
        lastSerialLogTime = currentMillis;
        printSerialStatus(currentMillis);
    }
}

// ============================================================================
// HARDWARE CONTROL FUNCTIONS (Preserved)
// ============================================================================

/**
 * @brief Sets the buzzer output respecting the configured polarity.
 * @param turnOn true to sound the buzzer, false to silence it.
 */
void setBuzzer(bool turnOn) {
    if (turnOn) {
        digitalWrite(PIN_BUZZER, BUZZER_ACTIVE_LOW ? LOW : HIGH);
    } else {
        digitalWrite(PIN_BUZZER, BUZZER_ACTIVE_LOW ? HIGH : LOW);
    }
    isBuzzerCurrentlyOn = turnOn;
}

/**
 * @brief Triggers HC-SR04 and reads echo pulse duration to compute distance.
 * @param[out] distanceOut Calculated distance in centimeters.
 * @return true if valid reading obtained; false on timeout or out-of-range.
 */
static unsigned long lastDurationUs = 0;
static float lastRawDist = 0.0f;

bool readRawDistanceCm(float &distanceOut) {
    // If ECHO pin is stuck HIGH from an earlier out-of-range pulse, unstick it:
    if (digitalRead(PIN_ECHO) == HIGH) {
        pinMode(PIN_ECHO, OUTPUT);
        digitalWrite(PIN_ECHO, LOW);
        delayMicroseconds(10);
        pinMode(PIN_ECHO, INPUT);
        delayMicroseconds(10);
    }

    // Send a clean 12 µs HIGH trigger pulse
    digitalWrite(PIN_TRIG, LOW);
    delayMicroseconds(4);
    digitalWrite(PIN_TRIG, HIGH);
    delayMicroseconds(12);
    digitalWrite(PIN_TRIG, LOW);

    // Measure duration of the HIGH pulse on ECHO pin (35ms covers full HC-SR04 cycle)
    unsigned long durationUs = pulseIn(PIN_ECHO, HIGH, 35000UL);
    lastDurationUs = durationUs;

    // Check for timeout
    if (durationUs == 0) {
        lastRawDist = -1.0f;
        return false;
    }

    // Distance in cm = (duration in µs * speed of sound) / 2
    float calculatedDist = (durationUs * SOUND_SPEED_CM_PER_US) / 2.0f;
    lastRawDist = calculatedDist;

    // Validate against sensor physical limits
    if (calculatedDist < MIN_VALID_DISTANCE_CM || calculatedDist > MAX_VALID_DISTANCE_CM) {
        return false;
    }

    distanceOut = calculatedDist;
    return true;
}

/**
 * @brief Filters raw sensor readings using median filtering, boundary hysteresis,
 *        and fast-response adoption for sudden close obstacles.
 * @param rawDist The latest raw distance reading from sensor.
 * @param isValid Whether rawDist is valid.
 * @param[out] filteredDistOut Filtered distance value.
 * @return true if a valid filtered distance is available; false otherwise.
 */
bool filterDistance(float rawDist, bool isValid, float &filteredDistOut) {
    if (!isValid) {
        consecutiveInvalidCount++;
        if (consecutiveInvalidCount >= MAX_CONSECUTIVE_INVALID) {
            // Confirm sensor state as invalid / unknown
            filterSampleCount = 0;
            return false;
        }
        // If we haven't reached consecutive invalid threshold, keep previous valid reading
        if (filterSampleCount > 0) {
            filteredDistOut = currentDistanceCm;
            return true;
        }
        return false;
    }

    // Reset invalid count upon receiving a valid reading
    consecutiveInvalidCount = 0;

    // Fast response check: If an obstacle suddenly appears significantly closer
    // (e.g. > 15 cm closer than current average), reset the buffer to avoid lag.
    if (filterSampleCount > 0 && rawDist < (currentDistanceCm - 15.0f)) {
        for (int i = 0; i < FILTER_SIZE; i++) {
            filterBuffer[i] = rawDist;
        }
        filterSampleCount = FILTER_SIZE;
        filterIndex = 0;
        filteredDistOut = rawDist;
        return true;
    }

    // Store in circular buffer
    filterBuffer[filterIndex] = rawDist;
    filterIndex = (filterIndex + 1) % FILTER_SIZE;
    if (filterSampleCount < FILTER_SIZE) {
        filterSampleCount++;
    }

    // Compute median of valid samples to eliminate transient spikes
    float tempBuffer[FILTER_SIZE];
    for (int i = 0; i < filterSampleCount; i++) {
        tempBuffer[i] = filterBuffer[i];
    }

    // Simple bubble sort for small array
    for (int i = 0; i < filterSampleCount - 1; i++) {
        for (int j = 0; j < filterSampleCount - i - 1; j++) {
            if (tempBuffer[j] > tempBuffer[j + 1]) {
                float tmp = tempBuffer[j];
                tempBuffer[j] = tempBuffer[j + 1];
                tempBuffer[j + 1] = tmp;
            }
        }
    }

    filteredDistOut = tempBuffer[filterSampleCount / 2];
    return true;
}

/**
 * @brief Classifies distance into warning levels with hysteresis.
 * @param distanceCm The filtered obstacle distance.
 * @param previousLevel The preceding warning level (for hysteresis).
 * @param[out] intervalOut Corresponding beep interval in ms.
 * @return WarningLevel enum value.
 */
WarningLevel calculateWarningLevel(float distanceCm, WarningLevel previousLevel, int &intervalOut) {
    // Define zone upper limits with hysteresis for ascending transitions (moving away)
    // Moving closer triggers immediately; moving away requires crossing threshold + HYSTERESIS_CM.
    float thresholdVeryClose = 15.0f;
    float thresholdDanger    = 30.0f;
    float thresholdCaution   = 60.0f;
    float thresholdWarning   = 100.0f;

    if (previousLevel == LEVEL_VERY_CLOSE) thresholdVeryClose += HYSTERESIS_CM;
    if (previousLevel == LEVEL_DANGER)     thresholdDanger    += HYSTERESIS_CM;
    if (previousLevel == LEVEL_CAUTION)    thresholdCaution   += HYSTERESIS_CM;
    if (previousLevel == LEVEL_WARNING)    thresholdWarning   += HYSTERESIS_CM;

    if (distanceCm < thresholdVeryClose) {
        intervalOut = 150; // Very close: beep every 150 ms
        return LEVEL_VERY_CLOSE;
    } else if (distanceCm <= thresholdDanger) {
        intervalOut = 250; // Danger: beep every 250 ms
        return LEVEL_DANGER;
    } else if (distanceCm <= thresholdCaution) {
        intervalOut = 450; // Caution: beep every 450 ms
        return LEVEL_CAUTION;
    } else if (distanceCm <= thresholdWarning) {
        intervalOut = 800; // Warning: beep every 800 ms
        return LEVEL_WARNING;
    } else {
        intervalOut = 0;   // Clear: > 100 cm, no beep
        return LEVEL_CLEAR;
    }
}

/**
 * @brief Non-blocking intermittent buzzer sequencer.
 *        Guarantees the buzzer is NEVER continuously ON.
 *        Produces short beeps (BEEP_DURATION_MS) separated by silence gaps.
 * @param currentMillis Current millis() timestamp.
 * @param level Active warning level.
 * @param intervalMs Cycle interval in ms.
 */
void updateBuzzerPattern(unsigned long currentMillis, WarningLevel level, int intervalMs) {
    // If the path is clear, sensor is invalid, or interval is 0, keep buzzer OFF
    if (level == LEVEL_CLEAR || level == LEVEL_UNKNOWN || intervalMs <= 0) {
        setBuzzer(false);
        return;
    }

    // Time elapsed in the current beep cycle
    unsigned long timeInCycle = currentMillis - lastBeepCycleStartTime;

    // Start a new beep cycle when the interval expires
    if (timeInCycle >= (unsigned long)intervalMs) {
        lastBeepCycleStartTime = currentMillis;
        setBuzzer(true); // Begin short beep
    } 
    // Stop the beep once BEEP_DURATION_MS has elapsed, keeping buzzer silent for remainder
    else if (isBuzzerCurrentlyOn && (timeInCycle >= BEEP_DURATION_MS)) {
        setBuzzer(false); // End short beep, begin silent gap
    }
}

/**
 * @brief Prints formatted system status to the Serial Monitor at 115200 baud.
 * @param currentMillis Current millis() timestamp.
 */
void printSerialStatus(unsigned long currentMillis) {
    if (currentLevel == LEVEL_UNKNOWN || !isSensorReadingValid) {
        Serial.printf("Distance: UNKNOWN | Raw: %.1f cm | Pulse: %lu us | Echo: %d\n",
                      lastRawDist, lastDurationUs, digitalRead(PIN_ECHO));
        return;
    }

    int roundedDistance = (int)round(currentDistanceCm);

    switch (currentLevel) {
        case LEVEL_CLEAR:
            Serial.printf("Distance: %d cm | Status: CLEAR | Buzzer: OFF\n", roundedDistance);
            break;

        case LEVEL_WARNING:
            Serial.printf("Distance: %d cm | Status: WARNING | Beep interval: %d ms\n", 
                          roundedDistance, currentBeepIntervalMs);
            break;

        case LEVEL_CAUTION:
            Serial.printf("Distance: %d cm | Status: CAUTION | Beep interval: %d ms\n", 
                          roundedDistance, currentBeepIntervalMs);
            break;

        case LEVEL_DANGER:
            Serial.printf("Distance: %d cm | Status: DANGER | Beep interval: %d ms\n", 
                          roundedDistance, currentBeepIntervalMs);
            break;

        case LEVEL_VERY_CLOSE:
            Serial.printf("Distance: %d cm | Status: VERY CLOSE | Beep interval: %d ms\n", 
                          roundedDistance, currentBeepIntervalMs);
            break;

        default:
            Serial.println("Distance: UNKNOWN | Sensor reading invalid");
            break;
    }
}

// ============================================================================
// BACKGROUND TELEMETRY TASK (Runs on Core 0)
// ============================================================================
/**
 * @brief Dedicated FreeRTOS background task pinned to ESP32 Core 0.
 *        Connects to Wi-Fi and transmits JSON telemetry via HTTP POST every ~1.5s.
 *        Does NOT block or delay the buzzer/ultrasonic loop on Core 1.
 */
/**
 * @brief Dedicated FreeRTOS background task pinned to ESP32 Core 0.
 *        Connects to Wi-Fi and transmits JSON telemetry via HTTP POST every ~1.5s.
 *        Does NOT block or delay the buzzer/ultrasonic loop on Core 1!
 */
void telemetryTask(void *pvParameters) {
    Serial.println("[Core 0] Background Telemetry Task started.");

    // Disconnect any stale association and configure station mode
    WiFi.persistent(false);
    WiFi.disconnect(true);
    vTaskDelay(pdMS_TO_TICKS(300));

    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);

    // Explicitly configure WPA3-SAE and PMF (Protected Management Frames)
    // This allows seamless connection to WPA3-Personal mobile hotspots!
    wifi_config_t wifi_conf;
    memset(&wifi_conf, 0, sizeof(wifi_conf));
    strncpy((char *)wifi_conf.sta.ssid, WIFI_SSID, sizeof(wifi_conf.sta.ssid) - 1);
    strncpy((char *)wifi_conf.sta.password, WIFI_PASSWORD, sizeof(wifi_conf.sta.password) - 1);
    wifi_conf.sta.pmf_cfg.capable = true;
    wifi_conf.sta.pmf_cfg.required = false;
    wifi_conf.sta.sae_pwe_h2e = WPA3_SAE_PWE_BOTH;
    esp_wifi_set_config(WIFI_IF_STA, &wifi_conf);

    Serial.printf("[Core 0] Initiating Wi-Fi connection to SSID: %s (WPA2/WPA3-SAE enabled)...\n", WIFI_SSID);
    esp_wifi_connect();

    String fullUrl = String(BACKEND_BASE_URL) + String(BACKEND_ENDPOINT);
    bool wasConnected = false;
    unsigned long lastStatusPrint = 0;
    unsigned long lastReconnectAttempt = millis();

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(TELEMETRY_INTERVAL_MS));

        wl_status_t status = WiFi.status();

        if (status != WL_CONNECTED) {
            if (wasConnected) {
                wasConnected = false;
                Serial.println("[Core 0] Wi-Fi connection lost. ESP-IDF reconnecting in background...");
            } else {
                unsigned long now = millis();
                if (now - lastStatusPrint > 5000UL) {
                    lastStatusPrint = now;
                    Serial.printf("[Core 0] Connecting to %s (status code: %d)...\n", WIFI_SSID, (int)status);
                }
                // Only retry if disconnected for more than 25 seconds
                if (now - lastReconnectAttempt > 25000UL) {
                    lastReconnectAttempt = now;
                    Serial.printf("[Core 0] Retrying Wi-Fi connection to %s ...\n", WIFI_SSID);
                    esp_wifi_disconnect();
                    esp_wifi_connect();
                }
            }
            continue; // Skip HTTP transmission while offline
        }

        if (!wasConnected) {
            wasConnected = true;
            lastReconnectAttempt = millis();
            Serial.printf("[Core 0] Wi-Fi Connected! Local IP: %s | RSSI: %d dBm\n",
                          WiFi.localIP().toString().c_str(), (int)WiFi.RSSI());
        }

        // Safely acquire latest sensor snapshot from Core 1
        float dist = -1.0f;
        bool valid = false;

        portENTER_CRITICAL(&telemetryMux);
        dist = sharedDistanceCm;
        valid = sharedIsValid;
        portEXIT_CRITICAL(&telemetryMux);

        // Build validated JSON payload
        char jsonPayload[160];
        if (valid && dist >= MIN_VALID_DISTANCE_CM && dist <= MAX_VALID_DISTANCE_CM) {
            snprintf(jsonPayload, sizeof(jsonPayload),
                     "{\"device_id\":\"%s\",\"distance_cm\":%.2f,\"status\":\"valid\"}",
                     DEVICE_ID, dist);
        } else {
            // Never send fake or misleading distances for invalid measurements
            snprintf(jsonPayload, sizeof(jsonPayload),
                     "{\"device_id\":\"%s\",\"distance_cm\":null,\"status\":\"unknown\"}",
                     DEVICE_ID);
        }

        // Send HTTP / HTTPS POST request with proper scope lifecycle to prevent dangling pointers
        int httpResponseCode = -1;
        String httpError = "";

        if (fullUrl.startsWith("https://")) {
            WiFiClientSecure secureClient;
            secureClient.setInsecure(); // Permits connection to cloud platforms without hardcoding CA certs
            HTTPClient http;
            if (http.begin(secureClient, fullUrl)) {
                http.addHeader("Content-Type", "application/json");
                http.addHeader("x-api-key", API_KEY);
                http.setTimeout(HTTP_TIMEOUT_MS);
                httpResponseCode = http.POST((uint8_t *)jsonPayload, strlen(jsonPayload));
                if (httpResponseCode <= 0) {
                    httpError = http.errorToString(httpResponseCode);
                }
                http.end();
            }
            secureClient.stop();
        } else {
            WiFiClient plainClient;
            HTTPClient http;
            if (http.begin(plainClient, fullUrl)) {
                http.addHeader("Content-Type", "application/json");
                http.addHeader("x-api-key", API_KEY);
                http.setTimeout(HTTP_TIMEOUT_MS);
                httpResponseCode = http.POST((uint8_t *)jsonPayload, strlen(jsonPayload));
                if (httpResponseCode <= 0) {
                    httpError = http.errorToString(httpResponseCode);
                }
                http.end();
            }
            plainClient.stop();
        }

        if (httpResponseCode >= 200 && httpResponseCode < 300) {
            Serial.printf("[Core 0] Telemetry POST success (HTTP %d) | dist: %.1f cm\n",
                          httpResponseCode, dist);
        } else {
            Serial.printf("[Core 0] HTTP POST failed, code: %d, error: %s\n",
                          httpResponseCode, httpError.c_str());
        }
    }
}
