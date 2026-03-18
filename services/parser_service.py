import re


def normalize_amount(amount_str):
    """Hàm chuẩn hóa số tiền: Biến chữ thành số sạch (Task W2-3.1)"""
    if not amount_str:
        return 0
    # 1. Sửa lỗi AI đọc nhầm: O, o -> 0; l, I -> 1
    clean = amount_str.replace('O', '0').replace('o', '0').replace('l', '1').replace('I', '1')
    # 2. Xóa hết rác: dấu chấm, phẩy, khoảng trắng, chữ 'đ', 'VND'
    clean = re.sub(r'[^\d]', '', clean)
    # 3. Chuyển về số nguyên
    try:
        return int(clean)
    except:
        return 0


import re


def extract_data(text_lines):
    if not text_lines:
        return {'vendor': 'UNKNOWN', 'amount': 0, 'raw_text': []}


    # --- BƯỚC 1: TÌM VENDOR (TÊN QUÁN) ---
    vendor_name = "UNKNOWN"
   
    # 1. Các dòng cần LOẠI TRỪ (Không bao giờ lấy làm tên quán)
    exclude_keywords = ['bàn:', 'số bàn', 'khu vực', 'ngày:', 'giờ:', 'mã hd', 'thu ngân', 'stt', 'phiếu']
   
    # 2. Các dòng ƯU TIÊN (Thấy chữ này là chốt tên quán luôn)
    priority_keywords = ['trà sữa', 'winmart', 'coffee', 'mót', 'tea', 'shop', 'store' , 'Mixue', 'Vé' , 'nước' , 'tiệm']


    potential_vendors = []
   
    # Duyệt 10 dòng đầu của hóa đơn
    for line in text_lines[:10]:
        line_clean = line.strip()
        line_lower = line_clean.lower()
       
        # Nếu dòng chứa từ khóa loại trừ (như Bàn A04) -> Bỏ qua ngay
        if any(ex in line_lower for ex in exclude_keywords):
            continue
           
        # Nếu dòng chứa từ khóa ưu tiên (như Trà sữa Mt) -> Chốt luôn
        if any(pri in line_lower for pri in priority_keywords):
            vendor_name = line_clean
            break
           
        # Nếu không thuộc 2 loại trên và đủ dài thì cho vào danh sách dự phòng
        if len(line_clean) > 3:
            potential_vendors.append(line_clean)


    # Nếu chưa tìm được theo ưu tiên, lấy dòng đầu tiên không bị loại trừ
    if vendor_name == "UNKNOWN" and potential_vendors:
        vendor_name = potential_vendors[0]


    # --- BƯỚC 2: TÌM AMOUNT (SỐ TIỀN) ---
    amount_integer = 0
    # Quét toàn bộ bill để không sót số tiền ở cuối (quan trọng cho WinMart)
    keywords_amount = ['tổng cộng', 'thanh toán', 'thành tiền', 'tổng tiền', 'cộng', 'total']


    for line in text_lines:
        if any(key in line.lower() for key in keywords_amount):
            # Tìm cụm số cuối cùng trong dòng
            nums = re.findall(r'[\dOoIl\.,]+', line)
            if nums:
                val = normalize_amount(nums[-1])
                if val > 1000:
                    amount_integer = val
                    break


    # --- BƯỚC 3: FALLBACK (Nếu không thấy từ khóa tiền) ---
    if amount_integer == 0:
        all_vals = []
        for line in text_lines:
            nums = re.findall(r'[\dOoIl\.,]+', line)
            for n in nums:
                v = normalize_amount(n)
                if v > 1000: all_vals.append(v)
        if all_vals:
            amount_integer = max(all_vals)


    return {
        "vendor": vendor_name,
        "amount": amount_integer,
        "raw_text": text_lines
    }
