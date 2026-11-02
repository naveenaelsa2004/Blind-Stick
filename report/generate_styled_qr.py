"""
Generates a presentation card version of the QR code with clear text labels
suitable for printing or inserting into project reports / posters.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def generate_styled_qr():
    raw_qr_path = os.path.join(os.path.dirname(__file__), "screenshots", "project_drive_qr_code.png")
    if not os.path.exists(raw_qr_path):
        return

    qr_img = Image.open(raw_qr_path).convert("RGB")
    # Resize QR code nicely for a card
    qr_size = 500
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

    card_w = 640
    card_h = 760
    card = Image.new("RGB", (card_w, card_h), color="#FFFFFF")
    draw = ImageDraw.Draw(card)

    # Outer border
    draw.rounded_rectangle([(10, 10), (card_w - 10, card_h - 10)], radius=20, outline="#1B365D", width=3)
    # Header bar
    draw.rounded_rectangle([(14, 14), (card_w - 14, 85)], radius=16, fill="#1B365D")

    # Load default font
    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_sub = ImageFont.truetype("arial.ttf", 15)
        font_link = ImageFont.truetype("consola.ttf", 12)
    except Exception:
        font_title = font_sub = font_link = ImageFont.load_default()

    # Title text
    draw.text((card_w / 2, 48), "PROJECT RESOURCES & DEMO DRIVE", font=font_title, fill="#FFFFFF", anchor="mm")
    
    # Paste QR code
    card.paste(qr_img, ((card_w - qr_size) // 2, 115))

    # Instructions text
    draw.text((card_w / 2, 650), "Scan with your smartphone camera to access", font=font_sub, fill="#4A5568", anchor="mm")
    draw.text((card_w / 2, 678), "IoT Smart Blind Stick Demonstration Files & Video", font=font_title, fill="#1B365D", anchor="mm")
    draw.text((card_w / 2, 715), "https://drive.google.com/drive/folders/1jDwdznrfLFV5JZ3gWPFMPzXMmXaBuiK8", font=font_link, fill="#718096", anchor="mm")

    out_paths = [
        os.path.join(os.path.dirname(__file__), "screenshots", "project_drive_qr_card.png"),
        os.path.join(os.path.dirname(__file__), "project_drive_qr_card.png"),
        r"C:\Users\binua\.gemini\antigravity-ide\brain\ab9415a7-8e11-46de-8e83-16ce158507f0\project_drive_qr_card.png"
    ]
    for p in out_paths:
        card.save(p, "PNG")
        print(f"[SUCCESS] Saved styled QR card to {p}")

if __name__ == "__main__":
    generate_styled_qr()
