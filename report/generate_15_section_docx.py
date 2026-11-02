"""
Generates a Microsoft Word document (.docx) for the 15-Section Project Report.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tc_pr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'  <w:top w:w="{top}" w:type="dxa"/>'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'  <w:left w:w="{left}" w:type="dxa"/>'
        f'  <w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)

def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    tbl_pr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tbl_pr.append(borders)

def format_table(table, col_widths, headers, rows_data):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="CBD5E1", sz="4")
    
    # Format header
    hdr_cells = table.rows[0].cells
    for i, header_text in enumerate(headers):
        hdr_cells[i].text = header_text
        set_cell_background(hdr_cells[i], "1B365D")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.name = "Calibri"
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            
    # Format rows
    for r_idx, row in enumerate(rows_data):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F8FAFC" if (r_idx % 2 == 1) else "FFFFFF"
        for c_idx, val in enumerate(row):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=100, bottom=100, left=140, right=140)
            p = row_cells[c_idx].paragraphs[0]
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(45, 55, 72)
                
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = Inches(width)

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'  <w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'</w:tcBorders>'
    )
    tc_pr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_report_docx(output_path):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    styles = doc.styles
    normal_style = styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(27, 54, 93)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(43, 108, 176)
        return p

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_after = Pt(12)
    run_t = p_title.add_run("SMART BLIND STICK WITH REAL-TIME OBSTACLE MONITORING AND CLOUD DASHBOARD SYSTEM")
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(18)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(27, 54, 93)

    # 1. INTRODUCTION
    add_h1("1. INTRODUCTION")
    doc.add_paragraph(
        "Visual impairment presents severe challenges to independent mobility, spatial orientation, and personal safety. "
        "Visually impaired individuals face daily navigational hazards such as unexpected obstacles, walls, furniture, and dynamic barriers in their walking path. "
        "Traditional mobility aids, such as standard white canes, only detect obstacles upon direct physical contact and fail to anticipate hazards in advance or detect elevated obstacles at torso or head height. "
        "Furthermore, traditional canes provide no telemetry or status tracking to caregivers or remote monitoring systems."
    )
    doc.add_paragraph(
        "To overcome these critical limitations, this project proposes an IoT-based Smart Blind Stick with Real-Time Obstacle Monitoring and Notification System. "
        "The system integrates an HC-SR04 ultrasonic sensor with a calibrated voltage divider and an intermittent acoustic buzzer module connected to an ESP32 microcontroller. "
        "The stick continuously measures obstacle proximity ahead of the user and produces frequency-modulated acoustic beeps that increase in repetition rate as obstacles approach, warning the user without inducing auditory fatigue. "
        "Simultaneously, the ESP32’s dual-core architecture enables Core 0 to transmit real-time telemetry over Wi-Fi via HTTP POST to a containerized FastAPI backend, persisting records in an SQLite database and streaming live updates to a responsive web dashboard. "
        "This solution delivers an affordable, reliable, non-blocking, and accessible assistive IoT device."
    )

    # 2. AIM OF THE PROJECT
    add_h1("2. AIM OF THE PROJECT")
    doc.add_paragraph(
        "The main aim of this project is to design, develop, and implement an IoT-enabled smart blind stick that continuously detects obstacles ahead using ultrasonic ranging, "
        "provides non-blocking intermittent acoustic alerts to the user, and transmits live telemetry to a containerized cloud backend and real-time dashboard for remote monitoring and logging."
    )

    # 3. OBJECTIVES
    add_h1("3. OBJECTIVES")
    objs = [
        "To measure real-time obstacle distance accurately within a 2 cm to 400 cm range using an HC-SR04 ultrasonic distance sensor.",
        "To protect the 3.3V ESP32 microcontroller from 5V echo pulses using a dedicated 1 kΩ / 1.8 kΩ resistor voltage divider (yielding a safe 3.21V logic level).",
        "To produce intuitive, non-fatiguing acoustic alerts using an intermittent buzzer sequencer that varies beep frequency according to proximity while keeping each beep duration strictly at ~60 ms (never sounding continuously).",
        "To execute non-blocking obstacle sensing and warning on ESP32 Core 1 while asynchronously transmitting telemetry over Wi-Fi on Core 0 via FreeRTOS, ensuring network delays never compromise user safety.",
        "To develop a containerized FastAPI backend with persistent SQLite storage for logging timestamped obstacle telemetry.",
        "To create a responsive, real-time web dashboard displaying live distance gauges, Chart.js time-series graphs, buzzer rhythm simulation, and connection health alerts."
    ]
    for obj in objs:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(obj)

    # 4. EXISTING SYSTEM
    add_h1("4. EXISTING SYSTEM")
    doc.add_paragraph("The traditional and existing methods for visually impaired navigation rely predominantly on mechanical white canes, tactile guide canes, or basic standalone electronic buzzers.")
    doc.add_paragraph("Disadvantages:").runs[0].font.bold = True
    disadvs = [
        "Physical Contact Requirement: Traditional canes only detect obstacles after physical impact has already occurred, risking falls or injuries from elevated or sharp objects.",
        "Auditory Fatigue & Signal Masking: Naive electronic canes emit continuous, harsh buzzing when obstacles are close, causing ear fatigue and masking essential environmental sounds like vehicle horns, traffic, and human speech.",
        "Single-Core Freezing: Basic microcontrollers freeze sensor scanning during Wi-Fi reconnects or HTTP requests, leaving the user unprotected during network stalls.",
        "Lack of Remote Telemetry: No centralized logging, cloud storage, or dashboard exists to monitor device health, navigation events, or safety history.",
        "Inability to Detect Distant Hazards: Manual tapping provides zero advance warning of approaching hazards beyond arm’s reach."
    ]
    for d in disadvs:
        p = doc.add_paragraph(style='List Bullet')
        parts = d.split(":", 1)
        r1 = p.add_run(parts[0] + ":")
        r1.bold = True
        p.add_run(parts[1])

    # 5. PROPOSED SYSTEM
    add_h1("5. PROPOSED SYSTEM")
    doc.add_paragraph(
        "The proposed system introduces an IoT-based smart assistive navigation stick that combines local real-time acoustic obstacle avoidance with containerized cloud telemetry. "
        "The ESP32 DevKit V1 reads time-of-flight pulses from an HC-SR04 sensor, applies a 5-sample median noise filter and a 2 cm hysteresis buffer, and determines the obstacle warning zone (Clear, Warning, Caution, Danger, or Very Close)."
    )
    doc.add_paragraph(
        "An intermittent buzzer algorithm triggers short 60 ms acoustic pulses with variable silence intervals (from 800 ms down to 150 ms) to give intuitive spatial cues. "
        "In the background, a dedicated FreeRTOS task on Core 0 packages distance readings into structured JSON payloads and dispatches them via HTTP POST to a containerized FastAPI backend. "
        "The backend validates the data, stores records in an SQLite database, and serves a modern glassmorphic dashboard with live proximity indicators, time-series charts, and offline alerts. "
        "This architecture ensures complete user safety locally while offering comprehensive remote monitoring."
    )

    # 6. SYSTEM ARCHITECTURE
    add_h1("6. SYSTEM ARCHITECTURE")
    doc.add_paragraph("The system architecture consists of two integrated operational tiers: the Device (Edge) Tier and the Backend / Cloud Tier.")
    
    add_h2("6.1 Hardware Components")
    hw_comps = [
        "ESP32 DevKit V1: Microcontroller with built-in Wi-Fi and dual-core processing for real-time sensing and telemetry.",
        "HC-SR04 Ultrasonic Sensor: Measures obstacle distance accurately from 2 cm to 400 cm.",
        "3-Pin Buzzer Module: Provides variable-frequency intermittent audible pulses (Active-LOW, GPIO 19).",
        "Voltage Divider Resistors (1 kΩ & 1.8 kΩ): Safely steps down the 5.0V ECHO signal to 3.21V for ESP32 GPIO 18.",
        "Breadboard & Jumper Wires: For reliable component prototyping and common ground connections.",
        "Micro-USB Cable / 5V Supply: Powers the ESP32 and attached peripherals via the VIN rail."
    ]
    for c in hw_comps:
        p = doc.add_paragraph(style='List Bullet')
        parts = c.split(":", 1)
        p.add_run(parts[0] + ":").bold = True
        p.add_run(parts[1])

    add_h2("6.2 Software Components")
    sw_comps = [
        "PlatformIO / Arduino Framework: Embedded C++ development toolchain for compiling and flashing the ESP32 firmware.",
        "FreeRTOS: Manages dual-core separation (Core 1 for sensing/buzzer, Core 0 for background Wi-Fi transmission).",
        "FastAPI + SQLite (Cloud/Backend): Lightweight, high-speed asynchronous REST API for data validation and storage.",
        "Dashboard Interface: Glassmorphic web frontend displaying real-time distance gauge, Chart.js curve, and buzzer visualizer.",
        "Docker & Docker Compose: Containerized backend deployment with persistent SQLite host directory mounting."
    ]
    for c in sw_comps:
        p = doc.add_paragraph(style='List Bullet')
        parts = c.split(":", 1)
        p.add_run(parts[0] + ":").bold = True
        p.add_run(parts[1])

    # 7. WORKING PRINCIPLE
    add_h1("7. WORKING PRINCIPLE")
    steps = [
        "Initialization: The ESP32 configures GPIO pins (TRIG on GPIO 5, ECHO on GPIO 18, Buzzer on GPIO 19), silences the buzzer, initializes the median filter, and launches the FreeRTOS telemetry task on Core 0.",
        "Data Acquisition: The ESP32 triggers a 10 µs pulse on GPIO 5, and the HC-SR04 emits an 8-cycle 40 kHz ultrasonic burst, returning an echo pulse proportional to distance.",
        "Data Processing & Safety Scaling: The 5V echo pulse is stepped down to 3.21V via the 1 kΩ / 1.8 kΩ voltage divider. Distance is calculated using the speed of sound and smoothed via a 5-sample median filter with 2 cm hysteresis.",
        "Threshold Check & Acoustic Warning: When an obstacle enters detection zones, the buzzer emits short 60 ms beeps: Warning (61–100 cm: 800 ms cycle), Caution (31–60 cm: 450 ms cycle), Danger (15–30 cm: 250 ms cycle), and Very Close (< 15 cm: 150 ms cycle).",
        "Dual-Core Telemetry: Core 0 asynchronously fetches atomic distance readings via critical sections and transmits JSON payloads via HTTP POST to /api/readings every 1.5 seconds without blocking the buzzer.",
        "Cloud Monitoring & Alerts: The FastAPI backend stores readings in SQLite, and the web dashboard displays live proximity gauges, rolling Chart.js curves, and offline/stale data warnings."
    ]
    for s in steps:
        p = doc.add_paragraph(style='List Bullet')
        parts = s.split(":", 1)
        p.add_run(parts[0] + ":").bold = True
        p.add_run(parts[1])

    # 8. CONNECTION DETAILS
    add_h1("8. CONNECTION DETAILS")
    conn_headers = ["Component", "Pin", "Type", "ESP32 Pin", "Voltage"]
    conn_data = [
        ["HC-SR04", "VCC", "Power", "VIN", "5.0V"],
        ["HC-SR04", "GND", "Ground", "GND", "0V"],
        ["HC-SR04", "TRIG", "Digital Output (from ESP32)", "GPIO 5", "3.3V"],
        ["HC-SR04", "ECHO", "Digital Input (via Divider)", "GPIO 18", "3.21V (Stepped down)"],
        ["Divider R1", "Input", "Resistor (1 kΩ)", "To ECHO pin", "5.0V"],
        ["Divider Node", "Junction", "Intermediate Node", "GPIO 18", "3.21V"],
        ["Divider R2", "Ground", "Resistor (1.8 kΩ)", "GND", "0V"],
        ["Buzzer Module", "VCC", "Power", "VIN / 3.3V", "3.3V – 5.0V"],
        ["Buzzer Module", "GND", "Ground", "GND", "0V"],
        ["Buzzer Module", "I/O (Signal)", "Digital Output (from ESP32)", "GPIO 19", "3.3V (Active-LOW)"]
    ]
    t_conn = doc.add_table(rows=len(conn_data) + 1, cols=5)
    format_table(t_conn, [1.3, 1.0, 1.8, 1.2, 1.2], conn_headers, conn_data)

    # 9. CLOUD & CONTAINER HOSTING
    add_h1("9. CLOUD & CONTAINER HOSTING")
    doc.add_paragraph("The backend server can be hosted on Microsoft Azure, AWS, a local PC, or any cloud VM using Docker containers for portability and reliability.")
    cloud_points = [
        "Host / Cloud VM: Ubuntu-based VM or Windows PC with open port 8000.",
        "Docker Setup: Lightweight container running Python FastAPI and Uvicorn with automated health checks.",
        "Deployment: Automated via docker compose up -d --build with container auto-restart policies.",
        "Data Management: Sensor readings stored persistently in SQLite mounted to the host directory (./data/sensor_readings.db)."
    ]
    for cp in cloud_points:
        p = doc.add_paragraph(style='List Bullet')
        parts = cp.split(":", 1)
        p.add_run(parts[0] + ":").bold = True
        p.add_run(parts[1])

    # 10. RESULTS
    add_h1("10. RESULTS")
    doc.add_paragraph("The implemented system successfully:")
    res_points = [
        "Measures real-time obstacle distance accurately from 2 cm to 400 cm.",
        "Produces intuitive intermittent acoustic warnings without continuous screeching or ear fatigue.",
        "Transmits live obstacle readings via Wi-Fi without pausing or delaying the local buzzer warning.",
        "Stores verified telemetry in a persistent SQLite database.",
        "Displays live proximity gauges, Chart.js time-series curves, and audit tables on the web dashboard.",
        "Enables remote monitoring and detects stale/offline device conditions automatically."
    ]
    for rp in res_points:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(rp)

    # 11. ADVANTAGES
    add_h1("11. ADVANTAGES")
    advs = [
        "Non-fatiguing acoustic safety with fixed 60 ms pulses.",
        "Dual-core FreeRTOS processing prevents network latency from freezing local safety functions.",
        "Hardware circuit protection via 1 kΩ / 1.8 kΩ voltage divider.",
        "Automated persistent logging with zero database configuration.",
        "Low cost, lightweight, and easy to construct.",
        "Remote dashboard visibility for family members and caregivers."
    ]
    for a in advs:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(a)

    # 12. APPLICATIONS
    add_h1("12. APPLICATIONS")
    apps = [
        "Personal Assistive Navigation: Daily indoor and outdoor obstacle avoidance for visually impaired individuals.",
        "Elderly Care & Fall Prevention: Proximity awareness in homes and senior living communities.",
        "Rehabilitation Centers: Navigational training tools for individuals adapting to vision loss.",
        "Low-Visibility Environments: Assistive navigation in smoky, dusty, or dark industrial settings."
    ]
    for ap in apps:
        p = doc.add_paragraph(style='List Bullet')
        parts = ap.split(":", 1)
        p.add_run(parts[0] + ":").bold = True
        p.add_run(parts[1])

    # 13. FUTURE ENHANCEMENTS
    add_h1("13. FUTURE ENHANCEMENTS")
    futs = [
        "Multi-Sensor Array: Downward-facing sensor for steps/curbs and upward-facing sensor for overhead obstacles.",
        "Cellular / LoRaWAN Module: Long-range outdoor telemetry without dependence on local Wi-Fi.",
        "Emergency SOS & GPS: One-touch panic button transmitting live GPS coordinates via SMS.",
        "Haptic Vibration Motor: Handle vibration alerts for users with dual auditory and visual impairments.",
        "Rechargeable Battery & Solar Tip: Integrated 18650 Li-ion battery with TP4056 USB-C charging."
    ]
    for f in futs:
        p = doc.add_paragraph(style='List Bullet')
        parts = f.split(":", 1)
        p.add_run(parts[0] + ":").bold = True
        p.add_run(parts[1])

    # 14. CONCLUSION
    add_h1("14. CONCLUSION")
    doc.add_paragraph(
        "The Smart Blind Stick with Real-Time Obstacle Monitoring and Cloud Dashboard System provides an intelligent, reliable, and life-enhancing assistive navigation solution. "
        "It eliminates the hazards of traditional white canes by detecting obstacles in advance and issuing intermittent acoustic warnings without auditory fatigue. "
        "The dual-core ESP32 architecture ensures that safety warnings are never interrupted by wireless network tasks, while the containerized FastAPI backend and real-time dashboard provide comprehensive remote monitoring. "
        "The project demonstrates a robust, scalable, and affordable foundation for next-generation assistive IoT devices."
    )

    # 15. PROJECT DESIGN
    add_h1("15. PROJECT DESIGN")
    doc.add_paragraph("Data Flow:").runs[0].font.bold = True
    flows = [
        "HC-SR04 Sensor → Voltage Divider → ESP32 Core 1: Ultrasonic pulses measure distance; voltage divider protects GPIO 18; Core 1 applies median filtering and drives intermittent beeps on GPIO 19.",
        "ESP32 Core 1 → Shared State → ESP32 Core 0: Atomic sensor snapshots transferred between cores via FreeRTOS critical sections.",
        "ESP32 Core 0 → Wi-Fi (HTTP POST) → Cloud / Backend: Transmits JSON telemetry to /api/readings every ~1.5s.",
        "FastAPI Backend → SQLite Database: Validates payloads and saves records in persistent storage (./data/sensor_readings.db).",
        "FastAPI Backend → Web Dashboard: Streams live distance values, Chart.js curves, buzzer rhythms, and audit logs to the user's browser."
    ]
    for fl in flows:
        p = doc.add_paragraph(style='List Bullet')
        parts = fl.split(":", 1)
        p.add_run(parts[0] + ":").bold = True
        p.add_run(parts[1])

    # 16. HARDWARE COMPONENTS
    add_h1("16. HARDWARE COMPONENTS")
    hw_img_path = os.path.join(os.path.dirname(__file__), "screenshots", "16_hardware_components.jpg")
    if os.path.exists(hw_img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(hw_img_path, width=Inches(6.2))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        run_cap = p_cap.add_run("Figure 16.1: Key Hardware Components — ESP32 DevKit V1, HC-SR04 Ultrasonic Distance Sensor, 3-Pin Buzzer Module, and 1 kΩ / 1.8 kΩ Resistor Voltage Divider.")
        run_cap.font.size = Pt(9.5)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(74, 85, 104)

    # 17. BLOCK DIAGRAM
    add_h1("17. BLOCK DIAGRAM")
    bd_img_path = os.path.join(os.path.dirname(__file__), "screenshots", "17_block_diagram.jpg")
    if os.path.exists(bd_img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(bd_img_path, width=Inches(6.2))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        run_cap = p_cap.add_run("Figure 17.1: End-to-End System Block Diagram — 4-Layer Architecture showing Physical Sensing Layer, ESP32 Processing & Connectivity Layer, Containerized Cloud Backend Layer, and Real-Time User Interface & Dashboard Layer.")
        run_cap.font.size = Pt(9.5)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(74, 85, 104)

    # 18. PROJECT DEMONSTRATION & DRIVE QR CODE
    add_h1("18. PROJECT DEMONSTRATION & DRIVE QR CODE")
    doc.add_paragraph(
        "Scan the QR code below using any smartphone camera or QR scanner to directly access the official Google Drive repository containing demonstration videos, photos, and project assets:"
    )
    qr_img_path = os.path.join(os.path.dirname(__file__), "screenshots", "project_drive_qr_card.png")
    if os.path.exists(qr_img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(qr_img_path, width=Inches(4.5))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        run_cap = p_cap.add_run("Figure 18.1: Google Drive Repository Link — https://drive.google.com/drive/folders/1jDwdznrfLFV5JZ3gWPFMPzXMmXaBuiK8?usp=drive_link")
        run_cap.font.size = Pt(9.5)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(43, 108, 176)

    doc.save(output_path)
    print(f"[SUCCESS] Saved 18-section Word doc to {output_path}")

if __name__ == "__main__":
    out_p = os.path.join(os.path.dirname(__file__), "smart_blind_stick_complete_report.docx")
    build_report_docx(out_p)
