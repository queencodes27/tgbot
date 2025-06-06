import os
from io import BytesIO
from telegram.ext import Updater, MessageHandler, Filters
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext

from PIL import Image
import pytesseract

# 🔐 Your Telegram bot token here
BOT_TOKEN = 7999619955:AAETSNdxrqG7bx0-ux17XjYe0lphvdSQbO0

# 🔎 Keywords for file type identification
RC_KEYWORDS = ['rate confirmation', 'rateconfirm', 'rc']
BOL_KEYWORDS = ['bill of lading', 'billoflading', 'bol']
POD_HINTS = ['signed', 'signature', 'delivered']

# 🔍 Function to classify the document
def classify_document(file_name):
    name = file_name.lower().replace(" ", "").replace("_", "")

    if any(k in name for k in RC_KEYWORDS):
        return 'Rate Confirmation'
    elif any(k in name for k in BOL_KEYWORDS):
        return 'Bill of Lading'
    elif any(hint in name for hint in POD_HINTS):
        return 'POD (signed BOL)'
    return 'Unknown'

# 📥 Handle incoming docs
def handle_document(update: Update, context: CallbackContext):
    document = update.message.document
    file_name = document.file_name

    doc_type = classify_document(file_name)

    if doc_type != 'Unknown':
        file = document.get_file()
        file_stream = BytesIO()
        file.download(out=file_stream)
        file_stream.seek(0)

        try:
            image = Image.open(file_stream)
            extracted_text = pytesseract.image_to_string(image)

            print(f"\n📄 OCR for {file_name} ({doc_type}):\n{extracted_text}\n")
            update.message.reply_text(f"✅ Extracted text from {doc_type}:\n{extracted_text[:400]}...")
        except Exception as e:
            update.message.reply_text(f"⚠️ Couldn't process {doc_type}. Possibly not an image.")
            print(f"Error: {e}")
    else:
        update.message.reply_text("⚠️ File skipped: not recognized as BOL, RC, or POD.")

# ▶️ Start bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.document, handle_document))

    print("🚀 Bot running... waiting for Rate Confirmations, BOLs, or PODs")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
