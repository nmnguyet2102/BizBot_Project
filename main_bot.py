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

# cấu hình logging
logging.basicConfig(level=logging.INFO)


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

    logging.info(f"OCR result: {text_lines}")

    # nếu không đọc được chữ
    if not text_lines:
        await msg.edit_text("❌ Không đọc được nội dung từ ảnh.")
        return

    # hiển thị tối đa 10 dòng
    preview_text = "\n".join(text_lines[:10])

    await msg.edit_text(
        f"📄 OCR đọc được:\n\n{preview_text}\n\n🔎 Confidence: {confidence}"
    )

# tạo bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("BizBot đang chạy...")

app.run_polling()