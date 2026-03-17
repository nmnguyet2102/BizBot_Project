import re

def extract_data(text_lines):
    # 1. Nếu text_lines rỗng
    if not text_lines:
        return {'vendor': 'UNKNOWN', 'amount': 0, 'raw_text': []}

    # 2. TÌM VENDOR (Thông minh hơn)
    # Loại bỏ các dòng có chứa từ khóa liên quan đến tiền trước khi tìm dòng dài nhất
    money_keywords = ['tổng', 'total', 'thanh toán', 'cộng', 'tiền', 'vnđ', 'vnd']
    potential_vendors = []
    
    for line in text_lines[:3]: # Xét 3 dòng đầu
        # Nếu dòng đó KHÔNG chứa từ khóa tiền bạc thì mới coi là Vendor tiềm năng
        if not any(key in line.lower() for key in money_keywords):
            potential_vendors.append(line)
    
    if potential_vendors:
        vendor_name = max(potential_vendors, key=len)
    else:
        vendor_name = text_lines[0] # Nếu dòng nào cũng có từ khóa thì lấy đại dòng đầu tiên

    # 3. TÌM AMOUNT
    amount_integer = 0
    found_amount = False
    target_keywords = ['Tổng', 'Total', 'Thanh toán', 'Cộng']

    for line in text_lines:
        if any(key.lower() in line.lower() for key in target_keywords):
            # Chuẩn hóa: O -> 0, xóa dấu cách, chấm, phẩy, chữ đ
            clean_line = line.upper().replace('O', '0')
            clean_line = re.sub(r'[^\d]', '', clean_line) # Chỉ giữ lại số
            
            if clean_line:
                amount_integer = int(clean_line)
                found_amount = True
                break

    # 4. FALLBACK AMOUNT: Lấy số lớn nhất nếu không tìm thấy từ khóa
    if not found_amount:
        all_numbers = []
        for line in text_lines:
            clean = line.upper().replace('O', '0')
            nums = re.findall(r'\d+', clean.replace('.', '').replace(',', ''))
            all_numbers.extend([int(n) for n in nums])
        if all_numbers:
            amount_integer = max(all_numbers)

    # OUTPUT 
    return {
        "vendor": vendor_name,
        "amount": amount_integer,
        "raw_text": text_lines
    }

if __name__ == "__main__":
    test_data = ['HIGHLANDS COFFEE', '10/03/2026', 'Tổng cộng: 5O.000đ']
    result = extract_data(test_data)
    print("--- KẾT QUẢ THỬ NGHIỆM MỚI ---")
    print(result)