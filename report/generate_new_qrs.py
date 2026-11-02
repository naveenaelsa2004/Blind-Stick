"""
Generate high-resolution QR codes and styled presentation cards for the new Google Drive links.
"""

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

LINKS = [
    {
        "id": "3",
        "name": "drive_link_3",
        "title": "GOOGLE DRIVE FOLDER 3",
        "folder_id": "1BYDtsUYnU5CRxEyEe4lXGRItUqmKNhJP",
        "url": "https://drive.google.com/drive/folders/1BYDtsUYnU5CRxEyEe4lXGRItUqmKNhJP?usp=sharing"
    },
    {
        "id": "4",
        "name": "drive_link_4",
        "title": "GOOGLE DRIVE FOLDER 4",
        "folder_id": "1iIufR3-ZIm6OWTfjONE30WsZAWHG082i",
        "url": "https://drive.google.com/drive/folders/1iIufR3-ZIm6OWTfjONE30WsZAWHG082i?usp=sharing"
    }
]

ARTIFACT_DIR = r"C:\Users\binua\.gemini\antigravity-ide\brain\ab9415a7-8e11-46de-8e83-16ce158507f0"
REPORT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(REPORT_DIR, "screenshots")
PROJECT_ROOT = os.path.abspath(os.path.join(REPORT_DIR, ".."))

def generate_qr_suite():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    results = []

    for item in LINKS:
        url = item["url"]
        name = item["name"]
        title = item["title"]

        # 1. Generate Raw QR Code (High-Resolution, Level H Error Correction)
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=4
        )
        qr.add_data(url)
        qr.make(fit=True)
        raw_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # File paths for raw QR
        raw_name = f"qr_{name}.png"
        raw_paths = [
            os.path.join(SCREENSHOTS_DIR, raw_name),
            os.path.join(REPORT_DIR, raw_name),
            os.path.join(ARTIFACT_DIR, raw_name)
        ]
        for p in raw_paths:
            raw_qr.save(p, "PNG")
        print(f"[OK] Saved raw QR: {raw_paths[0]}")

        # 2. Generate Presentation Styled Card (640 x 760)
        qr_size = 500
        resized_qr = raw_qr.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

        card_w = 640
        card_h = 760
        card = Image.new("RGB", (card_w, card_h), color="#FFFFFF")
        draw = ImageDraw.Draw(card)

        # Outer rounded border
        draw.rounded_rectangle([(10, 10), (card_w - 10, card_h - 10)], radius=20, outline="#1B365D", width=3)
        # Navy blue header bar
        draw.rounded_rectangle([(14, 14), (card_w - 14, 85)], radius=16, fill="#1B365D")

        # Fonts
        try:
            font_title = ImageFont.truetype("arial.ttf", 22)
            font_sub = ImageFont.truetype("arial.ttf", 15)
            font_link = ImageFont.truetype("consola.ttf", 11)
        except Exception:
            font_title = font_sub = font_link = ImageFont.load_default()

        # Header Title
        draw.text((card_w / 2, 48), title, font=font_title, fill="#FFFFFF", anchor="mm")

        # Center QR Code
        card.paste(resized_qr, ((card_w - qr_size) // 2, 115))

        # Bottom Descriptions
        draw.text((card_w / 2, 650), "Scan with your smartphone camera to access", font=font_sub, fill="#4A5568", anchor="mm")
        draw.text((card_w / 2, 678), "Google Drive Project Resource Folder", font=font_title, fill="#1B365D", anchor="mm")
        
        display_url = url if len(url) <= 60 else url[:58] + "..."
        draw.text((card_w / 2, 715), display_url, font=font_link, fill="#718096", anchor="mm")

        # File paths for styled card
        card_name = f"qr_card_{name}.png"
        card_paths = [
            os.path.join(SCREENSHOTS_DIR, card_name),
            os.path.join(REPORT_DIR, card_name),
            os.path.join(ARTIFACT_DIR, card_name)
        ]
        for p in card_paths:
            card.save(p, "PNG")
        print(f"[OK] Saved styled card: {card_paths[0]}")

        results.append({
            "title": title,
            "url": url,
            "raw_qr_path": raw_paths[0],
            "card_path": card_paths[0],
            "raw_name": raw_name,
            "card_name": card_name
        })

    return results

if __name__ == "__main__":
    generate_qr_suite()
