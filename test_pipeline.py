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

print("\n2. Đang chạy Parser Service...")
try:
    parsed_data = parser_service.extract_data(ocr_data["text_lines"])
    print("\n3. KẾT QUẢ CUỐI CÙNG:")
    print(parsed_data)
except Exception as e:
    print("❌ Parser failed:", e)
    exit()