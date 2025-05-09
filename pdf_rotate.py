import fitz  # PyMuPDF
from PIL import Image
import pytesseract

def rotate_and_ocr_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    results = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # 자동 회전 감지 및 이미지 회전
        osd = pytesseract.image_to_osd(img)
        rotate = int(osd.split("Rotate:")[1].split("\n")[0])
        rotated_img = img.rotate(360 - rotate, expand=True)

        # OCR 수행
        text = pytesseract.image_to_string(rotated_img, lang='kor+eng')
        results.append((i + 1, text))
    return results


rotate_and_ocr_pdf('./dataset/ocr/02.cropped_코레이트초단기금리혼합자산투자신탁.pdf')