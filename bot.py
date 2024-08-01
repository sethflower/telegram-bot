import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import sqlite3
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def create_db():
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS images
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 number TEXT UNIQUE, 
                 file_id TEXT)''')
    conn.commit()
    conn.close()

def add_image(number, file_id):
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO images (number, file_id) VALUES (?, ?)", (number, file_id))
    conn.commit()
    conn.close()

def get_image_file_id(number):
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute("SELECT file_id FROM images WHERE number=?", (number,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправьте номер, и я пришлю соответствующую картинку. Вы также можете использовать команду /add, чтобы добавить новую картинку.')

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    file_id = get_image_file_id(text)
    if file_id:
        update.message.reply_photo(photo=file_id)
    else:
        update.message.reply_text('Извините, нет картинки с таким номером.')

def add(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        number = context.args[0]
        file_id = update.message.reply_to_message.photo[-1].file_id
        add_image(number, file_id)
        update.message.reply_text(f'Картинка с номером {number} добавлена.')
    else:
        update.message.reply_text('Ответьте на сообщение с картинкой и укажите номер в команде, например, /add 123.')

def main() -> None:
    create_db()
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add, pass_args=True))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
