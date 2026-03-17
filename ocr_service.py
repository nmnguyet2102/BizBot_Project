import os
import cv2
from paddleocr import PaddleOCR
import google.generativeai as genai 

# ==========================================
# CẤU HÌNH AI
# ==========================================
# 1. Cấu hình Gemini (Não bộ sửa lỗi)
genai.configure(api_key="AIzaSyDtZjE8PMI7K3IlclpTEaI5nHQhHvsPN5c")
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. Khởi tạo PaddleOCR (Đôi mắt đọc ảnh)
ocr = PaddleOCR(use_angle_cls=True, lang='vi', enable_mkldnn=False)

def process_receipt(img_path):
    print(f"--- BẮT ĐẦU ĐỌC ẢNH ---")
    
    text_lines = []
    avg_conf = 0.95 
    image_input = img_path 

    # ==========================================
    # 1. TIỀN XỬ LÝ ẢNH BẰNG OPENCV 
    # ==========================================
    try:
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError("OpenCV không thể đọc dữ liệu ảnh.")

        img_resized = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        processed_img = cv2.convertScaleAbs(gray, alpha=1.3, beta=0)
        processed_img = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2BGR)

        image_input = processed_img
        print("- Xử lý OpenCV: Đã phóng to và tăng tương phản.")

    except Exception as e:
        print(f"- CẢNH BÁO: Lỗi OpenCV ({e}), dùng ảnh gốc.")
        image_input = img_path 


    # ==========================================
    # 2. ĐỌC CHỮ BẰNG PADDLEOCR (BẢN NHÁP)
    # ==========================================
    result = ocr.ocr(image_input)
    
    if result and len(result) > 0 and result[0] is not None:
        res_data = result[0]
        
        if isinstance(res_data, dict) and 'rec_texts' in res_data:
            text_lines = res_data['rec_texts']        
            scores = res_data.get('rec_scores', [])   
            if scores:
                avg_conf = sum(scores) / len(scores)
                
        elif isinstance(res_data, list):
            scores = []
            for line in res_data:
                if len(line) > 1 and len(line[1]) > 1:
                    text_lines.append(line[1][0])
                    scores.append(line[1][1])
            if scores:
                avg_conf = sum(scores) / len(scores)

    # ==========================================
    # 3. NẮN LỖI BẰNG GEMINI AI (BẢN SẠCH)
    # ==========================================
    if not text_lines:
        ai_cleaned_text = "Lỗi: Không tìm thấy chữ nào trên hóa đơn."
    else:
        van_ban_nhap = "\n".join(text_lines)
        
  
        prompt = f"""
        Dưới đây là văn bản được quét bằng OCR từ một tờ hóa đơn ở Việt Nam.
        Do giấy in nhiệt bị mờ, văn bản bị sai lỗi chính tả hoặc bay mất dấu.
        
        Nhiệm vụ của bạn:
        1. Điền lại các dấu tiếng Việt và sửa lỗi chính tả cho tự nhiên nhất.
        2. ĐẶC BIỆT CHÚ Ý: Các chữ cái đơn lẻ như 'M', 'L' đứng cuối tên món ăn là Size (Kích cỡ) đồ uống. Tuyệt đối giữ nguyên là 'M' hoặc 'L', KHÔNG được tự ý sửa thành chữ hay từ khác.
        3. Tuyệt đối GIỮ NGUYÊN các con số (giá tiền, số lượng, ngày tháng, mã).
        4. Trình bày lại thành một danh sách (hoặc bảng) gọn gàng.
        5. KHÔNG giải thích gì thêm, chỉ trả về nội dung hóa đơn.
        
        Văn bản quét thô:
        {van_ban_nhap}
        """
        
        try:
            response = model.generate_content(prompt)
            ai_cleaned_text = response.text
        except Exception as e:
            print(f"- Lỗi kết nối API Gemini: {e}")
            ai_cleaned_text = van_ban_nhap 

    return {
        "text_lines_raw": text_lines,
        "confidence": round(avg_conf, 2),
        "ai_cleaned_text": ai_cleaned_text
    }

if __name__ == "__main__":
    print("\n" + "="*50)
    duong_dan_anh = input("Kéo-Thả ảnh vào đây rồi nhấn Enter: ")
    duong_dan_anh = duong_dan_anh.strip('"').strip("'").strip()
    
    ket_qua = process_receipt(duong_dan_anh)
    
    print("\n========= HÓA ĐƠN =========")
    print(ket_qua["ai_cleaned_text"])
    print("===============================================\n")