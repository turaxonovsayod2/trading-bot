
import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Импорт ваших обработчиков и конфигурации
try:
    from config import BOT_TOKEN
    import bot.handlers as handlers
except ImportError as e:
    logging.error(f"Ошибка импорта: {e}. Убедитесь, что файлы config.py и bot/handlers.py существуют.")
    exit(1)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан. Добавьте переменную окружения BOT_TOKEN.")

# Создаём приложение Telegram
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Регистрируем команды (все, что есть в handlers)
telegram_app.add_handler(CommandHandler("start", handlers.start))
telegram_app.add_handler(CommandHandler("language", handlers.language))
telegram_app.add_handler(CommandHandler("connect_wallet", handlers.connect_wallet))
telegram_app.add_handler(CommandHandler("analyze", handlers.analyze))
telegram_app.add_handler(CommandHandler("buy", handlers.buy))
telegram_app.add_handler(CommandHandler("sell", handlers.sell))
telegram_app.add_handler(CommandHandler("portfolio", handlers.portfolio))
telegram_app.add_handler(CommandHandler("partner", handlers.partner))
telegram_app.add_handler(CommandHandler("profile", handlers.profile))
telegram_app.add_handler(CommandHandler("settings", handlers.settings))
telegram_app.add_handler(CommandHandler("set_sl", handlers.set_sl))
telegram_app.add_handler(CommandHandler("set_tp", handlers.set_tp))
telegram_app.add_handler(CommandHandler("set_risk", handlers.set_risk))
telegram_app.add_handler(CommandHandler("set_network", handlers.set_network))
telegram_app.add_handler(CommandHandler("auto_trade", handlers.auto_trade))
telegram_app.add_handler(CommandHandler("top_traders", handlers.top_traders))
telegram_app.add_handler(CommandHandler("copy", handlers.copy))
telegram_app.add_handler(CommandHandler("copy_on", handlers.copy_on))
telegram_app.add_handler(CommandHandler("copy_off", handlers.copy_off))
telegram_app.add_handler(CommandHandler("copy_percent", handlers.copy_percent))
telegram_app.add_handler(CommandHandler("copy_auto", handlers.copy_auto))
telegram_app.add_handler(CommandHandler("help", handlers.help_command))
telegram_app.add_handler(CallbackQueryHandler(handlers.callback_handler))

# Функция запуска бота в отдельном потоке
def run_bot():
    logging.info("Telegram бот запущен и слушает сообщения...")
    telegram_app.run_polling()

# Flask приложение для Render (чтобы сервер не засыпал)
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Bot is running!"

@flask_app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    # Запускаем бота в потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)
