/**
 * @file config.h
 * @brief Configuration parameters for Smart Blind Stick Wi-Fi and Backend Telemetry.
 */

#pragma once

// ============================================================================
// 1. WI-FI NETWORK CREDENTIALS
// ============================================================================
// Primary Wi-Fi network (Mobile Hotspot)
#define WIFI_SSID              "OPPO F21 Pro 5G"
#define WIFI_PASSWORD          "Oppo1234"

// ============================================================================
// 2. BACKEND SERVER CONFIGURATION
// ============================================================================
// CRITICAL WINDOWS NETWORKING NOTE:
// Do NOT use "localhost" or "127.0.0.1" here!
// On the ESP32, "localhost" refers to the ESP32 itself, NOT your computer.
// You MUST use your computer's reachable IPv4 address on the local network.
//
// Laptop Wi-Fi IPv4 address on phone hotspot: 10.30.115.161
#define BACKEND_BASE_URL "http://10.30.115.161:8000"
#define BACKEND_ENDPOINT "/api/readings"

// ============================================================================
// 3. DEVICE & TELEMETRY SETTINGS
// ============================================================================
// Unique device identifier for this stick
#define DEVICE_ID        "blind-stick-01"

// Telemetry transmit interval (ms)
#define TELEMETRY_INTERVAL_MS 1500UL

// HTTP client timeout (ms)
#define HTTP_TIMEOUT_MS  1200
