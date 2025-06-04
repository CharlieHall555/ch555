import qrcode #type: ignore
from qrcode.constants import ERROR_CORRECT_M #type: ignore
from PIL import UnidentifiedImageError

def generate_qr(data: str, filename: str = "qr.png") -> bool:
    try:
        qr = qrcode.QRCode(
            version=2,
            error_correction=ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        return True

    except (ValueError, UnidentifiedImageError, OSError) as e:
        print(f"[QR ERROR] Failed to generate QR code: {e}")
        return False
    