from paddleocr import PaddleOCR
import os

print("--- Đang khởi tạo AI... Lần đầu sẽ mất 1-3 phút để tải Model ---")
# Lệnh này sẽ tự động tải các file model nặng khoảng 100-150MB
ocr = PaddleOCR(use_angle_cls=True, lang='vi') 

print("--- THÀNH CÔNG: Model AI đã sẵn sàng! ---")
