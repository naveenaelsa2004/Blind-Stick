"""
Generate a clean, high-resolution QR code for the Google Drive project link.
"""

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

URL = "https://drive.google.com/drive/folders/1jDwdznrfLFV5JZ3gWPFMPzXMmXaBuiK8?usp=drive_link"

def generate_qr():
    # Setup QR code generator with high error correction
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(URL)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Save to report/screenshots and report/
    paths = [
        os.path.join(os.path.dirname(__file__), "screenshots", "project_drive_qr_code.png"),
        os.path.join(os.path.dirname(__file__), "project_drive_qr_code.png"),
        r"C:\Users\binua\.gemini\antigravity-ide\brain\ab9415a7-8e11-46de-8e83-16ce158507f0\project_drive_qr_code.png"
    ]

    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        img.save(p, "PNG")
        print(f"[SUCCESS] Saved QR code to {p}")

if __name__ == "__main__":
    generate_qr()
