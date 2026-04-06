import os
import logging
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler
from bot.handlers import start, help_command  # и другие ваши обработчики

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    # регистрируем все ваши команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))
    # ... остальные
    app.run_polling()

flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Bot is running"

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)
