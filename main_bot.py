from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import ALLOWED_USERS

# import services để kiểm tra path
from services import ocr_service
from services import parser_service
from services import db_service

import os
import logging
import time
import asyncio
from dotenv import load_dotenv   # <-- thêm dòng này

# đọc biến môi trường từ file .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")   # <-- thay cho TOKEN = "------"
if not TOKEN:
    raise ValueError("❌ Không tìm thấy BOT_TOKEN trong file .env")

from services.db_service import init_db

init_db()

# cấu hình logging
logging.basicConfig(
    level=logging.INFO
)


# ==========================================
# HELPER: chuyển cleaned text -> list dòng sạch
# ==========================================
def cleaned_text_to_lines(ai_cleaned_text: str):
    """
    Chuyển text Gemini trả về thành list[str] để parser dùng được.
    Loại bỏ dòng trống, bullet, markdown cơ bản.
    """
    if not ai_cleaned_text:
        return []

    lines = []
    for line in ai_cleaned_text.splitlines():
        line = line.strip()

        if not line:
            continue

        # bỏ markdown/bullet đơn giản
        line = line.lstrip("-•* ").strip()

        # bỏ dấu table markdown nếu có
        if line.startswith("|") and line.endswith("|"):
            line = line.strip("|").strip()

        if line:
            lines.append(line)

    return lines

# handler /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng bot này.")
        return

    user_name = update.effective_user.first_name

    await update.message.reply_text(
        f"Chào {user_name}, hãy gửi ảnh hóa đơn cho tôi."
    )


# handler nhận ảnh
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    # kiểm tra quyền sử dụng bot
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng bot này.")
        return

    # UX loading
    msg = await update.message.reply_text("⏳ Đang tiền xử lý ảnh...")

    await asyncio.sleep(1)
    await msg.edit_text("🔍 Đang chạy AI đọc chữ...")

    # lấy ảnh từ telegram
    photo = update.message.photo[-1]
    file = await photo.get_file()

    # tạo folder receipts nếu chưa có
    os.makedirs("receipts", exist_ok=True)

    timestamp = int(time.time())
    image_path = f"receipts/{user_id}_{timestamp}.jpg"

    # download ảnh
    await file.download_to_drive(image_path)

    logging.info(f"Saved image at {image_path}")

    await asyncio.sleep(1)
    await msg.edit_text("🧠 Đang phân tích nghiệp vụ...")

    # =========================
    # RUN OCR
    # =========================
    logging.info("Running OCR...")

    ocr_result = ocr_service.process_receipt(image_path)

    text_lines = ocr_result["text_lines"]
    confidence = ocr_result["confidence"]
    ai_cleaned_text = ocr_result.get("ai_cleaned_text", "")  

    logging.info(f"OCR result: {text_lines}")

    # nếu không đọc được chữ
    if not text_lines:
        await msg.edit_text("❌ Không đọc được nội dung từ ảnh.")
        return

 # =========================
    # DÙNG CLEANED TEXT CHO PARSER
    # =========================
    cleaned_lines = cleaned_text_to_lines(ai_cleaned_text)   # <-- THÊM

    if cleaned_lines:
        parsed_data = parser_service.extract_data(cleaned_lines)   # <-- THÊM
    else:
        parsed_data = parser_service.extract_data(text_lines)      # <-- THÊM

    vendor = parsed_data["vendor"]   # <-- THÊM
    amount = parsed_data["amount"]   # <-- THÊM

    # hiển thị tối đa 10 dòng
    preview_text = "\n".join(text_lines[:10])

    # thử cập nhật trạng thái hoàn tất, nếu timeout thì bỏ qua
    try:
        await msg.edit_text("✅ OCR hoàn tất, đang lưu dữ liệu...")
    except Exception as e:
        logging.warning(f"Không thể edit loading message: {e}")

    # gửi message mới thay vì edit nguyên nội dung dài
    await update.message.reply_text(
        f"📄 OCR đọc được:\n\n{preview_text}\n\n🔎 Confidence: {confidence}"
    )

# =========================
    # PARSE DATA (Não của Hải ở đây!)
    # =========================
    parsed_data = parser_service.extract_data(text_lines)
    vendor = parsed_data["vendor"]
    amount = parsed_data["amount"]


    # 1. Gọi Parser để trích xuất thông tin
    parsed_data = parser_service.extract_data(text_lines)
    vendor = parsed_data["vendor"]
    amount = parsed_data["amount"]


    # 2. Lưu vào Database với dữ liệu đã trích xuất
    expense_id = db_service.insert_expense(
        user_id=user_id,
        vendor=vendor,
        amount=amount,
        image_path=image_path,
        raw_text_list=text_lines
    )


    logging.info(f"Saved expense ID: {expense_id}")


    # 3. Phản hồi thông tin chi tiết cho người dùng
    await update.message.reply_text(
        f"✅ Đã lưu hóa đơn thành công!\n"
        f"🏢 Cửa hàng: {vendor}\n"
        f"💰 Số tiền: {amount:,} VND"
    )

# tạo bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("BizBot đang chạy...")

app.run_polling()