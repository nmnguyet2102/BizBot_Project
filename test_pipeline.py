from services import ocr_service
from services import parser_service

test_image = "receipts/test_bill.jpg"

print("1. Đang chạy OCR Service...")
try:
    ocr_data = ocr_service.process_receipt(test_image)
    print(f"-> OCR Confidence: {ocr_data['confidence']}")
except Exception as e:
    print("❌ OCR failed:", e)
    exit()

print("\n2. BẢN OCR THÔ:")
print(ocr_data["text_lines_raw"])

print("\n3. BẢN ĐÃ ĐƯỢC GEMINI LÀM SẠCH:")
print(ocr_data["ai_cleaned_text"])

print("\n4. Đang chạy Parser Service...")
try:
    cleaned_lines = ocr_data["ai_cleaned_text"].splitlines()
    parsed_data = parser_service.extract_data(cleaned_lines)

    print("\n5. KẾT QUẢ CUỐI CÙNG:")
    print(parsed_data)
except Exception as e:
    print("❌ Parser failed:", e)
    exit()