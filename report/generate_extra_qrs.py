"""
Generate high-resolution QR codes and styled presentation cards for two Google Drive links.
"""

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

LINKS = [
    {
        "id": "1",
        "name": "drive_link_1",
        "title": "GOOGLE DRIVE FOLDER 1",
        "url": "https://drive.google.com/drive/folders/1xyFk-MT4DJ4EPudN9JjP-7Hhe8eImwMh?usp=sharing"
    },
    {
        "id": "2",
        "name": "drive_link_2",
        "title": "GOOGLE DRIVE FOLDER 2",
        "url": "https://drive.google.com/drive/folders/1Z_5tSDZdyBbMItuwsdzHpX0Go_jkkdMP?usp=sharing"
    }
]

ARTIFACT_DIR = r"C:\Users\binua\.gemini\antigravity-ide\brain\ab9415a7-8e11-46de-8e83-16ce158507f0"
REPORT_DIR = os.path.dirname(__file__)
SCREENSHOTS_DIR = os.path.join(REPORT_DIR, "screenshots")

def create_qr_codes():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    for item in LINKS:
        url = item["url"]
        name = item["name"]
        title = item["title"]

        # 1. Generate Raw QR Code (High Resolution, Level H error correction)
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=4
        )
        qr.add_data(url)
        qr.make(fit=True)
        raw_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # Save raw QR
        raw_path = os.path.join(SCREENSHOTS_DIR, f"qr_{name}.png")
        raw_qr.save(raw_path, "PNG")
        raw_qr.save(os.path.join(ARTIFACT_DIR, f"qr_{name}.png"), "PNG")
        print(f"[SUCCESS] Saved raw QR to {raw_path}")

        # 2. Generate Presentation Styled Card
        qr_size = 500
        resized_qr = raw_qr.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

        card_w = 640
        card_h = 760
        card = Image.new("RGB", (card_w, card_h), color="#FFFFFF")
        draw = ImageDraw.Draw(card)

        # Outer border
        draw.rounded_rectangle([(10, 10), (card_w - 10, card_h - 10)], radius=20, outline="#1B365D", width=3)
        # Header bar
        draw.rounded_rectangle([(14, 14), (card_w - 14, 85)], radius=16, fill="#1B365D")

        try:
            font_title = ImageFont.truetype("arial.ttf", 22)
            font_sub = ImageFont.truetype("arial.ttf", 15)
            font_link = ImageFont.truetype("consola.ttf", 11)
        except Exception:
            font_title = font_sub = font_link = ImageFont.load_default()

        # Header title
        draw.text((card_w / 2, 48), title, font=font_title, fill="#FFFFFF", anchor="mm")

        # Paste QR
        card.paste(resized_qr, ((card_w - qr_size) // 2, 115))

        # Bottom text
        draw.text((card_w / 2, 650), "Scan with your smartphone camera to access", font=font_sub, fill="#4A5568", anchor="mm")
        draw.text((card_w / 2, 678), "Google Drive Project Resource Folder", font=font_title, fill="#1B365D", anchor="mm")
        # Shortened URL display for neatness
        display_url = url if len(url) <= 60 else url[:58] + "..."
        draw.text((card_w / 2, 715), display_url, font=font_link, fill="#718096", anchor="mm")

        card_path = os.path.join(SCREENSHOTS_DIR, f"qr_card_{name}.png")
        card.save(card_path, "PNG")
        card.save(os.path.join(ARTIFACT_DIR, f"qr_card_{name}.png"), "PNG")
        print(f"[SUCCESS] Saved styled card to {card_path}")

if __name__ == "__main__":
    create_qr_codes()
