from paddleocr import PaddleOCR
import os

# Khởi tạo AI
ocr = PaddleOCR(use_angle_cls=True, lang='vi', enable_mkldnn=False)

def process_receipt(img_path):
    print(f"--- BẮT ĐẦU ĐỌC ẢNH ---")
    
    # 1. Quét ảnh
    result = ocr.ocr(img_path)
    
    text_lines = []
    avg_conf = 0.95 # Mặc định
    
    # 2. Bóc tách dữ liệu chuẩn xác cho PaddleOCR bản mới
    if result and len(result) > 0:
        res_data = result[0]
        
        # Nếu AI trả về Dictionary (Bản mới)
        if isinstance(res_data, dict) and 'rec_texts' in res_data:
            text_lines = res_data['rec_texts']        # Lấy toàn bộ chữ
            scores = res_data.get('rec_scores', [])   # Lấy độ tin cậy
            if scores:
                avg_conf = sum(scores) / len(scores)
                
        # Nếu AI trả về List (Bản cũ - phòng hờ)
        elif isinstance(res_data, list):
            scores = []
            for line in res_data:
                text_lines.append(line[1][0])
                scores.append(line[1][1])
            if scores:
                avg_conf = sum(scores) / len(scores)

    return {
        "text_lines": text_lines,
        "confidence": round(avg_conf, 2)
    }

if __name__ == "__main__":
    print("\n" + "="*50)
    duong_dan_anh = input("Kéo-Thả ảnh vào đây rồi nhấn Enter: ")
    duong_dan_anh = duong_dan_anh.strip('"').strip("'").strip()
    
    ket_qua = process_receipt(duong_dan_anh)
    
    print("\n--- KẾT QUẢ NGHIỆM THU CUỐI CÙNG ---")
    print(ket_qua)
    print("="*50 + "\n")