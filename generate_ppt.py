"""
Script to generate the 8-page PowerPoint Presentation (.pptx) for:
IoT-Based Smart Blind Stick for Visually Impaired People
Author: Naveena Elsa Koshy
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # 16:9 Widescreen dimensions: 13.333 x 7.5 inches
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette Definitions
    C_NAVY = RGBColor(15, 23, 42)        # Slate 900
    C_CARD_BG = RGBColor(248, 250, 252)  # Slate 50
    C_CARD_BORDER = RGBColor(203, 213, 225) # Slate 300
    C_BLUE = RGBColor(2, 132, 199)       # Sky 600
    C_CYAN = RGBColor(6, 182, 212)       # Cyan 500
    C_DARK = RGBColor(30, 41, 59)        # Slate 800
    C_BODY = RGBColor(51, 65, 85)        # Slate 700
    C_MUTED = RGBColor(100, 116, 139)    # Slate 500
    C_WHITE = RGBColor(255, 255, 255)
    C_GREEN = RGBColor(22, 163, 74)      # Emerald 600
    C_YELLOW = RGBColor(202, 138, 4)     # Amber 600
    C_ORANGE = RGBColor(234, 88, 12)     # Orange 600
    C_RED = RGBColor(220, 38, 38)        # Red 600
    C_BLUE_LIGHT = RGBColor(224, 242, 254)

    # Image Paths
    img_hardware = r"d:\Blind Stick\report\screenshots\16_hardware_components.jpg"
    img_block_diag = r"d:\Blind Stick\report\screenshots\17_block_diagram.jpg"
    img_dashboard = r"d:\Blind Stick\report\screenshots\06_dashboard.png"
    img_qr = r"d:\Blind Stick\report\screenshots\project_drive_qr_card.png"

    # Helper: Add Standard Header
    def add_header(slide, page_num, section_tag, main_title):
        # Header container bar
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = C_NAVY
        top_bar.line.fill.background()

        # Accent line under header
        accent_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06))
        accent_line.fill.solid()
        accent_line.fill.fore_color.rgb = C_BLUE
        accent_line.line.fill.background()

        # Section tag & main title in text frame
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(10.5), Inches(0.95))
        tf = tx_box.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0)
        tf.margin_bottom = Inches(0)
        tf.margin_left = Inches(0)
        tf.margin_right = Inches(0)

        p_tag = tf.paragraphs[0]
        p_tag.text = section_tag.upper()
        p_tag.font.name = "Segoe UI"
        p_tag.font.size = Pt(10.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = C_CYAN

        p_title = tf.add_paragraph()
        p_title.text = main_title
        p_title.font.name = "Segoe UI"
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = C_WHITE

        # Slide page indicator badge (top right)
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.6), Inches(0.35), Inches(1.0), Inches(0.45))
        badge.fill.solid()
        badge.fill.fore_color.rgb = RGBColor(30, 41, 59)
        badge.line.color.rgb = C_CYAN
        badge.line.width = Pt(1)
        b_tf = badge.text_frame
        b_tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        b_p = b_tf.paragraphs[0]
        b_p.text = f"{page_num} / 8"
        b_p.alignment = PP_ALIGN.CENTER
        b_p.font.name = "Segoe UI"
        b_p.font.size = Pt(11)
        b_p.font.bold = True
        b_p.font.color.rgb = C_WHITE

        # Bottom subtle footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(11.733), Inches(0.3))
        ftf = footer_box.text_frame
        ftf.margin_top = Inches(0)
        ftf.margin_bottom = Inches(0)
        ftf.margin_left = Inches(0)
        ftf.margin_right = Inches(0)
        fp = ftf.paragraphs[0]
        fp.text = "IoT-Based Smart Blind Stick | Dual-Core FreeRTOS & Cloud IoT Telemetry | Naveena Elsa Koshy"
        fp.font.name = "Segoe UI"
        fp.font.size = Pt(9.5)
        fp.font.color.rgb = C_MUTED

    # Helper: Create Styled Card Shape
    def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    # =========================================================================
    # SLIDE 1: FRONT PAGE (TITLE SLIDE)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)

    # Dark gradient background simulation
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_NAVY
    bg1.line.fill.background()

    # Left accent colored bar
    left_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.25), Inches(7.5))
    left_bar.fill.solid()
    left_bar.fill.fore_color.rgb = C_CYAN
    left_bar.line.fill.background()

    # Academic Project Badge
    badge_proj = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.7), Inches(4.5), Inches(0.42))
    badge_proj.fill.solid()
    badge_proj.fill.fore_color.rgb = RGBColor(30, 41, 59)
    badge_proj.line.color.rgb = C_CYAN
    badge_proj.line.width = Pt(1)
    b_tf = badge_proj.text_frame
    b_tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    bp = b_tf.paragraphs[0]
    bp.text = "  IoT & EMBEDDED SYSTEMS CAPSTONE PROJECT  "
    bp.alignment = PP_ALIGN.CENTER
    bp.font.name = "Segoe UI"
    bp.font.size = Pt(10)
    bp.font.bold = True
    bp.font.color.rgb = C_CYAN

    # Main Project Title
    tbox1 = slide1.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(8.5), Inches(2.2))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "IoT-Based Smart Blind Stick\nfor Visually Impaired People"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(33)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Dual-Core FreeRTOS Edge Computing, Cloud IoT Telemetry & Real-Time Monitoring"
    p1_sub.font.name = "Segoe UI"
    p1_sub.font.size = Pt(14)
    p1_sub.font.color.rgb = C_CYAN
    p1_sub.space_before = Pt(10)

    # 4 Tech Pills under title
    tech_pills = [
        ("ESP32 Dual-Core (240MHz)", C_BLUE_LIGHT, C_BLUE),
        ("FreeRTOS Task Isolation", RGBColor(220, 252, 231), C_GREEN),
        ("FastAPI & Render Cloud", RGBColor(254, 249, 195), C_YELLOW),
        ("Glassmorphic Dashboard", RGBColor(255, 237, 213), C_ORANGE)
    ]
    pill_x = Inches(1.0)
    for text, bg, fg in tech_pills:
        pill = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pill_x, Inches(3.75), Inches(2.05), Inches(0.38))
        pill.fill.solid()
        pill.fill.fore_color.rgb = bg
        pill.line.fill.background()
        ptf = pill.text_frame
        ptf.vertical_anchor = MSO_ANCHOR.MIDDLE
        pp = ptf.paragraphs[0]
        pp.text = text
        pp.alignment = PP_ALIGN.CENTER
        pp.font.name = "Segoe UI"
        pp.font.size = Pt(9.5)
        pp.font.bold = True
        pp.font.color.rgb = fg
        pill_x += Inches(2.15)

    # Student / Institutional Metadata Card (Left-bottom)
    meta_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(4.35), Inches(8.3), Inches(2.45))
    meta_card.fill.solid()
    meta_card.fill.fore_color.rgb = RGBColor(30, 41, 59)
    meta_card.line.color.rgb = RGBColor(51, 65, 85)
    meta_card.line.width = Pt(1)

    mtf = meta_card.text_frame
    mtf.margin_left = Inches(0.35)
    mtf.margin_top = Inches(0.25)
    mtf.margin_right = Inches(0.35)

    mp0 = mtf.paragraphs[0]
    mp0.text = "ACADEMIC PROJECT SUBMISSION"
    mp0.font.name = "Segoe UI"
    mp0.font.size = Pt(11)
    mp0.font.bold = True
    mp0.font.color.rgb = C_CYAN

    details = [
        ("Student / Author:", "Naveena Elsa Koshy"),
        ("Course / Degree:", "Master of Computer Applications (MCA)"),
        ("Department:", "Department of Computer Applications"),
        ("Institution:", "Amal Jyothi College of Engineering (AJCE)"),
        ("Academic Year:", "2026 – 2027  |  Submission: October 2026")
    ]
    for label, val in details:
        mp = mtf.add_paragraph()
        mp.space_before = Pt(4)
        run_lbl = mp.add_run()
        run_lbl.text = f"{label:<22} "
        run_lbl.font.name = "Segoe UI"
        run_lbl.font.size = Pt(11)
        run_lbl.font.bold = True
        run_lbl.font.color.rgb = RGBColor(226, 232, 240)

        run_val = mp.add_run()
        run_val.text = val
        run_val.font.name = "Segoe UI"
        run_val.font.size = Pt(11)
        run_val.font.color.rgb = C_WHITE

    # Right Card: Project QR Code Card for evaluator review
    if os.path.exists(img_qr):
        qr_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.65), Inches(1.3), Inches(2.75), Inches(5.5))
        qr_card.fill.solid()
        qr_card.fill.fore_color.rgb = RGBColor(30, 41, 59)
        qr_card.line.color.rgb = C_CYAN
        qr_card.line.width = Pt(1.5)

        qtf = qr_card.text_frame
        qtf.margin_top = Inches(0.2)
        qp1 = qtf.paragraphs[0]
        qp1.text = "PROJECT DRIVE & CODE"
        qp1.alignment = PP_ALIGN.CENTER
        qp1.font.name = "Segoe UI"
        qp1.font.size = Pt(10)
        qp1.font.bold = True
        qp1.font.color.rgb = C_CYAN

        slide1.shapes.add_picture(img_qr, Inches(9.85), Inches(1.85), width=Inches(2.35))

        lbl_box = slide1.shapes.add_textbox(Inches(9.75), Inches(5.95), Inches(2.55), Inches(0.75))
        ltf = lbl_box.text_frame
        ltf.word_wrap = True
        lp = ltf.paragraphs[0]
        lp.text = "Scan QR Code for live Drive repository, test logs & cloud dashboard"
        lp.alignment = PP_ALIGN.CENTER
        lp.font.name = "Segoe UI"
        lp.font.size = Pt(9)
        lp.font.color.rgb = RGBColor(203, 213, 225)

    # =========================================================================
    # SLIDE 2: INTRODUCTION (PAGE 1) — BACKGROUND & PROBLEM STATEMENT
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, 2, "Introduction (1/2)", "Background, Need & The Problem Statement")

    # 3 Distinct Problem Cards across the width
    cards_data_s2 = [
        (
            "1. GLOBAL CONTEXT & ASSISTIVE NEED",
            C_BLUE,
            [
                ("WHO Global Health Data: ", "Over 2.2 billion people suffer from vision impairment or blindness globally, severely restricting independent mobility."),
                ("White Cane Limitations: ", "Traditional white canes provide ground-touch feedback only; they fail to detect elevated, head-level, or dynamic obstacles before physical collision."),
                ("Economic Barrier: ", "Guide dogs and proprietary electronic aids cost upwards of $40,000, creating an urgent demand for low-cost, off-the-shelf smart solutions.")
            ]
        ),
        (
            "2. THE AUDITORY FATIGUE PROBLEM",
            C_ORANGE,
            [
                ("Shrill Continuous Alarms: ", "Naive smart cane designs trigger continuous buzzing whenever an obstacle is detected, overwhelming the user's ears."),
                ("Signal Masking Danger: ", "Continuous shrill tones drown out ambient environmental acoustics such as approaching vehicles, traffic signals, and footsteps."),
                ("Acoustic Ergonomics Required: ", "A non-fatiguing, intermittent pulsing rhythm is required that conveys proximity urgency without continuous sound.")
            ]
        ),
        (
            "3. NETWORK BLOCKING & LATENCY RISK",
            C_RED,
            [
                ("Single-Threaded Bottlenecks: ", "On standard microcontrollers, Wi-Fi handshakes or HTTP socket timeouts cause 1–3 second execution halts."),
                ("Safety Loop Freezes: ", "If ultrasonic distance sensing is blocked during network stalls, the user is left completely unprotected while walking."),
                ("Dual-Core Necessity: ", "Local obstacle detection and warning must be completely decoupled from cloud telemetry through hard task isolation.")
            ]
        )
    ]

    card_w = Inches(3.75)
    card_gap = Inches(0.3)
    card_x = Inches(0.8)
    card_y = Inches(1.45)
    card_h = Inches(5.45)

    for title, accent_color, bullets in cards_data_s2:
        card = add_card(slide2, card_x, card_y, card_w, card_h)
        # Accent top bar for card
        c_top = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_x, card_y, card_w, Inches(0.12))
        c_top.fill.solid()
        c_top.fill.fore_color.rgb = accent_color
        c_top.line.fill.background()

        ctf = card.text_frame
        ctf.margin_left = Inches(0.25)
        ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(0.3)

        cp0 = ctf.paragraphs[0]
        cp0.text = title
        cp0.font.name = "Segoe UI"
        cp0.font.size = Pt(12)
        cp0.font.bold = True
        cp0.font.color.rgb = accent_color

        for b_lead, b_body in bullets:
            bp = ctf.add_paragraph()
            bp.space_before = Pt(14)
            r1 = bp.add_run()
            r1.text = "• " + b_lead
            r1.font.name = "Segoe UI"
            r1.font.size = Pt(10.5)
            r1.font.bold = True
            r1.font.color.rgb = C_DARK

            r2 = bp.add_run()
            r2.text = b_body
            r2.font.name = "Segoe UI"
            r2.font.size = Pt(10)
            r2.font.color.rgb = C_BODY

        card_x += card_w + card_gap

    # =========================================================================
    # SLIDE 3: INTRODUCTION (PAGE 2) — PROPOSED SOLUTION & OBJECTIVES
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, 3, "Introduction (2/2)", "Proposed Solution & Project Objectives")

    # Left Column: Proposed Architectural Solution (Inches 5.7 wide)
    sol_card = add_card(slide3, Inches(0.8), Inches(1.45), Inches(5.7), Inches(5.45))
    s_top = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(5.7), Inches(0.12))
    s_top.fill.solid()
    s_top.fill.fore_color.rgb = C_BLUE
    s_top.line.fill.background()

    stf = sol_card.text_frame
    stf.margin_left = Inches(0.3)
    stf.margin_right = Inches(0.3)
    stf.margin_top = Inches(0.3)

    sp0 = stf.paragraphs[0]
    sp0.text = "THE PROPOSED ASSISTIVE IoT SOLUTION"
    sp0.font.name = "Segoe UI"
    sp0.font.size = Pt(13)
    sp0.font.bold = True
    sp0.font.color.rgb = C_BLUE

    sol_items = [
        ("Dual-Core FreeRTOS Hardware Isolation:", "Core 1 is dedicated 100% to 40ms ultrasonic obstacle scanning and acoustic alerts. Core 0 runs background network telemetry without ever preempting Core 1."),
        ("Distance-Scaled Pulsed Beep Modulation:", "Replaces continuous alarms with intermittent beeps. Silent gap scales dynamically: 800ms (Warning), 400ms (Caution), 150ms (Danger), maintaining ambient awareness."),
        ("High-Performance Cloud Data Pipeline:", "Containerized Python FastAPI microservice deployed on Render (Singapore region) ingestion endpoint with secure API key verification."),
        ("Glassmorphic Remote Caregiver Dashboard:", "Real-time web monitoring interface providing live distance readouts, audio-visual rhythm simulation, Chart.js trend lines, and SQLite audit records.")
    ]

    for lead, desc in sol_items:
        p = stf.add_paragraph()
        p.space_before = Pt(12)
        r1 = p.add_run()
        r1.text = "✔  " + lead + " "
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = C_DARK

        r2 = p.add_run()
        r2.text = desc
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(10)
        r2.font.color.rgb = C_BODY

    # Right Column: Core Engineering Objectives (Inches 5.7 wide)
    obj_card = add_card(slide3, Inches(6.8), Inches(1.45), Inches(5.7), Inches(5.45))
    o_top = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.45), Inches(5.7), Inches(0.12))
    o_top.fill.solid()
    o_top.fill.fore_color.rgb = C_GREEN
    o_top.line.fill.background()

    otf = obj_card.text_frame
    otf.margin_left = Inches(0.3)
    otf.margin_right = Inches(0.3)
    otf.margin_top = Inches(0.3)

    op0 = otf.paragraphs[0]
    op0.text = "PRIMARY ENGINEERING OBJECTIVES"
    op0.font.name = "Segoe UI"
    op0.font.size = Pt(13)
    op0.font.bold = True
    op0.font.color.rgb = C_GREEN

    objectives = [
        ("Preserve Working Hardware Wiring:", "Build the solution on standard ESP32 DevKit V1, HC-SR04, and Active-LOW buzzer without requiring board re-spinning or complex peripherals."),
        ("Zero-Latency Real-Time Guarantee:", "Ensure obstacle scanning executes strictly every 40ms regardless of whether Wi-Fi is connecting, connected, or offline."),
        ("Robust Payload Validation:", "Implement strict Pydantic schemas validating device ID, distance bounds (2–400 cm), and sensor statuses before database commit."),
        ("Persistent Cloud & Edge Storage:", "Utilize SQLite with indexed timestamps and Write-Ahead Logging (WAL) to support seamless time-series auditing across reboots."),
        ("Low-Latency Cloud Deployment:", "Deploy backend to Render Singapore region (<500ms RTT in India) to eliminate cloud lag and dashboard staleness.")
    ]

    for lead, desc in objectives:
        p = otf.add_paragraph()
        p.space_before = Pt(10)
        r1 = p.add_run()
        r1.text = "🎯  " + lead + " "
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = C_DARK

        r2 = p.add_run()
        r2.text = desc
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(10)
        r2.font.color.rgb = C_BODY

    # =========================================================================
    # SLIDE 4: COMPONENTS — HARDWARE & SOFTWARE STACK
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, 4, "System Components", "Comprehensive Hardware & Software Stack")

    # Left Panel: Hardware Stack & Embedded Photo (Inches 5.7 wide)
    hw_card = add_card(slide4, Inches(0.8), Inches(1.45), Inches(5.7), Inches(5.45))
    h_top = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(5.7), Inches(0.12))
    h_top.fill.solid()
    h_top.fill.fore_color.rgb = C_BLUE
    h_top.line.fill.background()

    htf = hw_card.text_frame
    htf.margin_left = Inches(0.25)
    htf.margin_right = Inches(0.25)
    htf.margin_top = Inches(0.25)

    hp0 = htf.paragraphs[0]
    hp0.text = "PHYSICAL HARDWARE MODULES"
    hp0.font.name = "Segoe UI"
    hp0.font.size = Pt(12.5)
    hp0.font.bold = True
    hp0.font.color.rgb = C_BLUE

    # Hardware components list
    hw_specs = [
        ("ESP32 DevKit V1:", "Xtensa Dual-Core 32-bit LX6 @ 240MHz, 520KB SRAM, 4MB Flash, Integrated 2.4GHz Wi-Fi (802.11 b/g/n)"),
        ("HC-SR04 Ultrasonic:", "2cm to 400cm measurement range, 15° beam angle, 10µs trigger pulse, 40kHz acoustic burst"),
        ("Active Buzzer Module:", "3-Pin Active-LOW acoustic module, pulsed frequency modulation, 85dB SPL alert"),
        ("Power & Interconnects:", "Regulated 5V/3.3V DC power rail, solderless breadboard & jumper leads")
    ]
    for name, spec in hw_specs:
        p = htf.add_paragraph()
        p.space_before = Pt(4)
        r1 = p.add_run()
        r1.text = "• " + name + " "
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = C_DARK
        r2 = p.add_run()
        r2.text = spec
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(9)
        r2.font.color.rgb = C_BODY

    # Embed Hardware Photo at bottom of hardware card
    if os.path.exists(img_hardware):
        slide4.shapes.add_picture(img_hardware, Inches(1.05), Inches(4.35), width=Inches(5.2), height=Inches(2.35))

    # Right Panel: Software, Cloud & Network Stack (Inches 5.7 wide)
    sw_card = add_card(slide4, Inches(6.8), Inches(1.45), Inches(5.7), Inches(5.45))
    sw_top = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.45), Inches(5.7), Inches(0.12))
    sw_top.fill.solid()
    sw_top.fill.fore_color.rgb = C_CYAN
    sw_top.line.fill.background()

    swtf = sw_card.text_frame
    swtf.margin_left = Inches(0.3)
    swtf.margin_right = Inches(0.3)
    swtf.margin_top = Inches(0.25)

    swp0 = swtf.paragraphs[0]
    swp0.text = "SOFTWARE, CLOUD & NETWORK ARCHITECTURE"
    swp0.font.name = "Segoe UI"
    swp0.font.size = Pt(12.5)
    swp0.font.bold = True
    swp0.font.color.rgb = C_CYAN

    sw_components = [
        ("FreeRTOS Real-Time Kernel:", "Symmetric Multiprocessing (SMP) on ESP32, task pinning (`xTaskCreatePinnedToCore`), critical section spinlocks (`portENTER_CRITICAL`), 10KB TLS stack."),
        ("Python 3.11 & FastAPI:", "High-throughput asynchronous ASGI microservice, Pydantic type validation, CORS middleware, REST endpoints (`/api/health`, `/api/readings`, `/api/latest`)."),
        ("Render Cloud Platform (Singapore):", "Native cloud web service deployed in Singapore (`sin`) region closest to India; SSL/TLS 1.3 termination, zero server maintenance, continuous git deployments."),
        ("SQLite Storage Engine:", "Zero-configuration relational database with persistent file storage, parameterized SQL queries preventing injection, indexed timestamps for fast queries."),
        ("Glassmorphic Web UI & Chart.js:", "Unified HTML5/Vanilla CSS frontend with glassmorphism effects, live distance gauge, audio-visual beep simulator, and 50-point time-series graphing.")
    ]

    for title, desc in sw_components:
        p = swtf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "⚡ " + title + " "
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(10)
        r1.font.bold = True
        r1.font.color.rgb = C_DARK

        r2 = p.add_run()
        r2.text = desc
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = C_BODY

    # =========================================================================
    # SLIDE 5: BLOCK DIAGRAM — ARCHITECTURE & DATA FLOW
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, 5, "System Architecture", "End-to-End Block Diagram & Data Pipeline")

    # Embedded Block Diagram Image (Top half)
    if os.path.exists(img_block_diag):
        slide5.shapes.add_picture(img_block_diag, Inches(0.8), Inches(1.35), width=Inches(11.733), height=Inches(3.4))

    # 3 Architecture Tier Cards across the bottom half
    bd_tiers = [
        (
            "TIER 1: EDGE SENSING & ACTUATION",
            C_BLUE,
            [
                "HC-SR04 emits 40kHz pulse on 10µs trigger; measures high-pulse return time on Echo pin.",
                "ESP32 Core 1 executes 25Hz non-blocking scan loop and moving median digital filter.",
                "Active-LOW buzzer outputs distance-proportional pulsed acoustic tones (60ms ON pulses)."
            ]
        ),
        (
            "TIER 2: DUAL-CORE DECOUPLING",
            C_CYAN,
            [
                "Core 0 FreeRTOS background task connects to WPA2/WPA3 mobile hotspot asynchronously.",
                "Atomic shared memory transfer between Core 1 and Core 0 via spinlock mutexes.",
                "WiFiClientSecure establishes TLS 1.3 connection to Render cloud over HTTPS."
            ]
        ),
        (
            "TIER 3: CLOUD INGESTION & UI",
            C_GREEN,
            [
                "FastAPI validates payload schema & verifies 'x-api-key' secret header before commit.",
                "SQLite stores timestamped telemetry with indexed keys for instant historical lookups.",
                "Real-time glassmorphic dashboard polls '/api/latest' with sub-second live updates."
            ]
        )
    ]

    tier_x = Inches(0.8)
    tier_w = Inches(3.75)
    tier_gap = Inches(0.24)
    tier_y = Inches(4.9)
    tier_h = Inches(2.05)

    for title, accent_color, points in bd_tiers:
        card = add_card(slide5, tier_x, tier_y, tier_w, tier_h)
        c_top = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, tier_x, tier_y, tier_w, Inches(0.08))
        c_top.fill.solid()
        c_top.fill.fore_color.rgb = accent_color
        c_top.line.fill.background()

        ctf = card.text_frame
        ctf.margin_left = Inches(0.2)
        ctf.margin_right = Inches(0.2)
        ctf.margin_top = Inches(0.15)

        cp0 = ctf.paragraphs[0]
        cp0.text = title
        cp0.font.name = "Segoe UI"
        cp0.font.size = Pt(10)
        cp0.font.bold = True
        cp0.font.color.rgb = accent_color

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(3)
            r = p.add_run()
            r.text = "• " + pt
            r.font.name = "Segoe UI"
            r.font.size = Pt(8.5)
            r.font.color.rgb = C_BODY

        tier_x += tier_w + tier_gap

    # =========================================================================
    # SLIDE 6: WORKING (PAGE 1) — EDGE SENSING & ACOUSTIC CONTROL
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, 6, "Working Mechanism (1/2)", "Edge Ultrasonic Sensing & Multi-Zone Acoustic Warning")

    # Column 1: Ultrasonic Timing & Digital Filtering (Inches 3.7 wide)
    w1_card = add_card(slide6, Inches(0.8), Inches(1.45), Inches(3.7), Inches(5.45))
    w1_top = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(3.7), Inches(0.12))
    w1_top.fill.solid()
    w1_top.fill.fore_color.rgb = C_BLUE
    w1_top.line.fill.background()

    w1_tf = w1_card.text_frame
    w1_tf.margin_left = Inches(0.25)
    w1_tf.margin_right = Inches(0.25)
    w1_tf.margin_top = Inches(0.25)

    w1_p0 = w1_tf.paragraphs[0]
    w1_p0.text = "1. ULTRASONIC SENSING ENGINE"
    w1_p0.font.name = "Segoe UI"
    w1_p0.font.size = Pt(11.5)
    w1_p0.font.bold = True
    w1_p0.font.color.rgb = C_BLUE

    w1_points = [
        ("Speed of Sound Formula:", "Distance = (Echo Time × 0.0343 cm/µs) ÷ 2. Measures round-trip transit of 40 kHz acoustic waves."),
        ("10µs Clean Trigger Pulse:", "Pin 5 (TRIG) is pulsed for exactly 10 microseconds, initiating 8 cycles of ultrasonic burst."),
        ("Echo Timeout Guarding:", "Pin 18 (ECHO) times out at 30,000 µs (~5.1 meters) preventing task deadlocks on unreflected pings."),
        ("Moving Window Filtering:", "Maintains a 5-sample ring buffer. Removes stray acoustic spikes, multipath reflections, and phantom echoes."),
        ("25 Hz Real-Time Loop:", "Executes every 40 ms consistently on Core 1 without using blocking delay functions.")
    ]
    for lead, desc in w1_points:
        p = w1_tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + lead + " "
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = C_DARK
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(9)
        r2.font.color.rgb = C_BODY

    # Column 2: 4-Zone Proximity Classification Table (Inches 4.1 wide)
    w2_card = add_card(slide6, Inches(4.75), Inches(1.45), Inches(4.1), Inches(5.45))
    w2_top = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.75), Inches(1.45), Inches(4.1), Inches(0.12))
    w2_top.fill.solid()
    w2_top.fill.fore_color.rgb = C_ORANGE
    w2_top.line.fill.background()

    w2_tf = w2_card.text_frame
    w2_tf.margin_left = Inches(0.25)
    w2_tf.margin_right = Inches(0.25)
    w2_tf.margin_top = Inches(0.25)

    w2_p0 = w2_tf.paragraphs[0]
    w2_p0.text = "2. 4-ZONE ACOUSTIC MODULATION"
    w2_p0.font.name = "Segoe UI"
    w2_p0.font.size = Pt(11.5)
    w2_p0.font.bold = True
    w2_p0.font.color.rgb = C_ORANGE

    zones = [
        ("ZONE 1: CLEAR (> 100 cm)", "Buzzer: OFF (Completely Silent)", "User walks freely; zero acoustic disturbance; battery conservation.", C_GREEN),
        ("ZONE 2: WARNING (70 – 100 cm)", "Pulsing Interval: 800 ms", "60 ms beep every 800 ms. Alerts user of an approaching distant object.", C_YELLOW),
        ("ZONE 3: CAUTION (40 – 70 cm)", "Pulsing Interval: 400 ms", "Moderate pulsing rhythm. User prepares to alter walking heading.", C_ORANGE),
        ("ZONE 4: DANGER (< 40 cm)", "Pulsing Interval: 150 ms", "Urgent rapid pulsed tone. Warns of immediate collision risk within arm reach.", C_RED)
    ]
    for z_title, z_rate, z_desc, z_col in zones:
        p_t = w2_tf.add_paragraph()
        p_t.space_before = Pt(8)
        rt = p_t.add_run()
        rt.text = "■ " + z_title
        rt.font.name = "Segoe UI"
        rt.font.size = Pt(10)
        rt.font.bold = True
        rt.font.color.rgb = z_col

        p_r = w2_tf.add_paragraph()
        p_r.space_before = Pt(1)
        rr = p_r.add_run()
        rr.text = "   Rate: " + z_rate
        rr.font.name = "Segoe UI"
        rr.font.size = Pt(9)
        rr.font.bold = True
        rr.font.color.rgb = C_DARK

        p_d = w2_tf.add_paragraph()
        p_d.space_before = Pt(1)
        rd = p_d.add_run()
        rd.text = "   Context: " + z_desc
        rd.font.name = "Segoe UI"
        rd.font.size = Pt(8.5)
        rd.font.color.rgb = C_BODY

    # Column 3: Fail-Safe State Machine & Non-Blocking Design (Inches 3.5 wide)
    w3_card = add_card(slide6, Inches(9.1), Inches(1.45), Inches(3.433), Inches(5.45))
    w3_top = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(9.1), Inches(1.45), Inches(3.433), Inches(0.12))
    w3_top.fill.solid()
    w3_top.fill.fore_color.rgb = C_GREEN
    w3_top.line.fill.background()

    w3_tf = w3_card.text_frame
    w3_tf.margin_left = Inches(0.25)
    w3_tf.margin_right = Inches(0.25)
    w3_tf.margin_top = Inches(0.25)

    w3_p0 = w3_tf.paragraphs[0]
    w3_p0.text = "3. NON-BLOCKING SAFETY LOOP"
    w3_p0.font.name = "Segoe UI"
    w3_p0.font.size = Pt(11.5)
    w3_p0.font.bold = True
    w3_p0.font.color.rgb = C_GREEN

    safety_points = [
        ("millis() State Controller:", "Eliminates `delay()` calls completely. Buzzer state toggles by comparing `currentMillis - lastBeepToggleTime`."),
        ("Constant 60ms Pulse Width:", "Beep duration remains exactly 60ms; only the silent gap length adjusts. Prevents auditory fatigue."),
        ("Active-LOW Polarity Handling:", "Inverts logic for 3-pin buzzer modules. Pin is pre-biased HIGH before pinMode activation, eliminating boot shrieks."),
        ("Fail-Safe Sensor Guard:", "Out-of-range (>400cm) or timed-out pings set status to UNKNOWN, silencing buzzer to avoid false collision alerts.")
    ]
    for lead, desc in safety_points:
        p = w3_tf.add_paragraph()
        p.space_before = Pt(10)
        r1 = p.add_run()
        r1.text = "✔ " + lead + " "
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = C_DARK
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(9)
        r2.font.color.rgb = C_BODY

    # =========================================================================
    # SLIDE 7: WORKING (PAGE 2) — CLOUD TELEMETRY & DASHBOARD
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, 7, "Working Mechanism (2/2)", "Cloud IoT Pipeline, HTTPS Telemetry & Remote Monitoring")

    # Left Column: Cloud Telemetry Pipeline Card (Inches 5.7 wide)
    c_pipe = add_card(slide7, Inches(0.8), Inches(1.45), Inches(5.7), Inches(5.45))
    cp_top = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(5.7), Inches(0.12))
    cp_top.fill.solid()
    cp_top.fill.fore_color.rgb = C_BLUE
    cp_top.line.fill.background()

    cptf = c_pipe.text_frame
    cptf.margin_left = Inches(0.25)
    cptf.margin_right = Inches(0.25)
    cptf.margin_top = Inches(0.25)

    cpp0 = cptf.paragraphs[0]
    cpp0.text = "SECURE CLOUD TELEMETRY PIPELINE"
    cpp0.font.name = "Segoe UI"
    cpp0.font.size = Pt(12)
    cpp0.font.bold = True
    cpp0.font.color.rgb = C_BLUE

    pipeline_steps = [
        ("Core 0 FreeRTOS Daemon Task:", "Executes asynchronously every 1.5 seconds with 10 KB stack. Pulls snapshot of distance from Core 1 via spinlock critical section."),
        ("WPA2/WPA3 Hotspot Compatibility:", "ESP-IDF station config enforces Protected Management Frames (PMF) and SAE-PWE, enabling connections to 5G smartphone hotspots."),
        ("MbedTLS Cloud HTTPS Client:", "Uses `WiFiClientSecure` with non-blocking TLS 1.3 handshake to `https://smart-blind-stick-backend.onrender.com`."),
        ("Header-Based API Key Security:", "Telemetry payload transmits secret header `x-api-key: blind-stick-secret-key-2026`. Unauthorized requests return HTTP 401."),
        ("Pydantic Ingestion & SQLite Commit:", "FastAPI validates JSON payload (`device_id`, `distance_cm`, `status`). Persists to SQLite with indexed microsecond timestamps.")
    ]
    for lead, desc in pipeline_steps:
        p = cptf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "🔒 " + lead + " "
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = C_DARK
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(9)
        r2.font.color.rgb = C_BODY

    # Right Column: Dashboard Features & Embedded Screenshot (Inches 5.7 wide)
    dash_card = add_card(slide7, Inches(6.8), Inches(1.45), Inches(5.7), Inches(5.45))
    dp_top = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.45), Inches(5.7), Inches(0.12))
    dp_top.fill.solid()
    dp_top.fill.fore_color.rgb = C_CYAN
    dp_top.line.fill.background()

    dtf = dash_card.text_frame
    dtf.margin_left = Inches(0.25)
    dtf.margin_right = Inches(0.25)
    dtf.margin_top = Inches(0.25)

    dp0 = dtf.paragraphs[0]
    dp0.text = "REAL-TIME GLASSMORPHIC DASHBOARD"
    dp0.font.name = "Segoe UI"
    dp0.font.size = Pt(12)
    dp0.font.bold = True
    dp0.font.color.rgb = C_CYAN

    # Embedded Dashboard Screenshot
    if os.path.exists(img_dashboard):
        slide7.shapes.add_picture(img_dashboard, Inches(7.05), Inches(1.95), width=Inches(5.2), height=Inches(2.75))

    # Dashboard Features text below screenshot
    dash_feat_box = slide7.shapes.add_textbox(Inches(7.0), Inches(4.85), Inches(5.3), Inches(1.9))
    dftf = dash_feat_box.text_frame
    dftf.word_wrap = True
    dftf.margin_top = Inches(0)
    dftf.margin_bottom = Inches(0)
    dftf.margin_left = Inches(0)
    dftf.margin_right = Inches(0)

    dash_features = [
        ("Sub-Second Telemetry Refresh:", "Polls `/api/latest` every 1000ms. Displays live distance readout with dynamic color indicator (Green/Yellow/Orange/Red)."),
        ("Live Chart.js Trend Plotting:", "Graphs last 50 telemetry readings chronologically with safe zone threshold guides."),
        ("Audio-Visual Buzzer Mimicry:", "Simulates the stick's pulsing buzzer rhythm in real time on the web browser for remote caregivers.")
    ]
    for i, (lead, desc) in enumerate(dash_features):
        p = dftf.paragraphs[0] if i == 0 else dftf.add_paragraph()
        p.space_before = Pt(3) if i > 0 else Pt(0)
        r1 = p.add_run()
        r1.text = "• " + lead + " "
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(9)
        r1.font.bold = True
        r1.font.color.rgb = C_DARK
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = C_BODY

    # =========================================================================
    # SLIDE 8: CONCLUSION — ACHIEVEMENTS, ADVANTAGES & FUTURE ROADMAP
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, 8, "Conclusion & Roadmap", "Project Summary, Engineering Impact & Future Enhancements")

    # 3 Cards for Conclusion
    cards_data_s8 = [
        (
            "1. KEY PROJECT ACHIEVEMENTS",
            C_GREEN,
            [
                ("End-to-End Operational System: ", "Successfully designed, coded, and physically tested on ESP32 DevKit V1 hardware over COM3."),
                ("Dual-Core Concurrency Validated: ", "Zero interference between ultrasonic safety beeping on Core 1 and cloud HTTPS POST on Core 0."),
                ("Low-Latency Cloud Deployment: ", "Render Singapore instance verified live with SQLite persistence and under 500ms round-trip latency."),
                ("100% Automated Test Pass: ", "Full test suite validates API contracts, schema validation, and health monitoring endpoints.")
            ]
        ),
        (
            "2. ENGINEERING ADVANTAGES",
            C_BLUE,
            [
                ("Acoustic Ergonomics: ", "Intermittent pulsing eliminates sensory fatigue while keeping ambient hearing alert for vehicle horns."),
                ("Network Fail-Safe Resilience: ", "The cane functions autonomously even in areas with zero Wi-Fi, hotspot dropouts, or server lag."),
                ("Cost-Effective Assistive Aid: ", "Built using off-the-shelf components costing under $15, making it universally accessible."),
                ("Caregiver Visibility: ", "Enables remote family members to monitor user activity, obstacle incidents, and stick operational status.")
            ]
        ),
        (
            "3. FUTURE ROADMAP & ENHANCEMENTS",
            C_CYAN,
            [
                ("ToF Solid-State LiDAR: ", "Addition of optical Time-of-Flight sensors to detect transparent glass partitions and downward drop-offs (puddle/stair detection)."),
                ("Edge AI Voice Announcements: ", "Integration of ESP-ADF audio codec or DFPlayer Mini to speak obstacle distance ('Obstacle at 50 centimeters')."),
                ("GPS & GSM Emergency SOS: ", "Equipping a panic push-button with SIM800L module to transmit real-time GPS coordinates via SMS to family."),
                ("Haptic Grip Actuation: ", "Adding eccentric vibrating motor in handle for dual tactile-acoustic sensory feedback in loud areas.")
            ]
        )
    ]

    card_w = Inches(3.75)
    card_gap = Inches(0.3)
    card_x = Inches(0.8)
    card_y = Inches(1.45)
    card_h = Inches(5.45)

    for title, accent_color, bullets in cards_data_s8:
        card = add_card(slide8, card_x, card_y, card_w, card_h)
        c_top = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_x, card_y, card_w, Inches(0.12))
        c_top.fill.solid()
        c_top.fill.fore_color.rgb = accent_color
        c_top.line.fill.background()

        ctf = card.text_frame
        ctf.margin_left = Inches(0.25)
        ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(0.3)

        cp0 = ctf.paragraphs[0]
        cp0.text = title
        cp0.font.name = "Segoe UI"
        cp0.font.size = Pt(11.5)
        cp0.font.bold = True
        cp0.font.color.rgb = accent_color

        for b_lead, b_body in bullets:
            bp = ctf.add_paragraph()
            bp.space_before = Pt(12)
            r1 = bp.add_run()
            r1.text = "✔ " + b_lead
            r1.font.name = "Segoe UI"
            r1.font.size = Pt(10)
            r1.font.bold = True
            r1.font.color.rgb = C_DARK

            r2 = bp.add_run()
            r2.text = b_body
            r2.font.name = "Segoe UI"
            r2.font.size = Pt(9.5)
            r2.font.color.rgb = C_BODY

        card_x += card_w + card_gap

    # Save presentations
    output_path_root = r"d:\Blind Stick\smart_blind_stick_presentation.pptx"
    output_path_report = r"d:\Blind Stick\report\smart_blind_stick_presentation.pptx"
    prs.save(output_path_root)
    prs.save(output_path_report)
    print(f"Presentation saved successfully to:\n1. {output_path_root}\n2. {output_path_report}")
    print(f"Total Slides: {len(prs.slides)}")

if __name__ == "__main__":
    create_presentation()
