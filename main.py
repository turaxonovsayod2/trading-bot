
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Проверяем наличие токена
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not set in environment variables")
    exit(1)

# Импортируем handlers (папка bot/handlers.py)
try:
    import bot.handlers as handlers
except ImportError as e:
    logger.error(f"Failed to import handlers: {e}")
    # Создаём простую заглушку, чтобы бот запустился
    class handlers:
        async def start(update, context): await update.message.reply_text("Бот запущен (упрощённый режим)")
        # Остальные методы – заглушки
        language = connect_wallet = analyze = buy = sell = portfolio = partner = profile = settings = set_sl = set_tp = set_risk = set_network = auto_trade = top_traders = copy = copy_on = copy_off = copy_percent = copy_auto = help_command = callback_handler = start

# Создаём приложение Telegram
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Регистрируем команды
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

# FastAPI для webhook
app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return JSONResponse({"ok": True})

@app.get("/")
async def root():
    return {"status": "Bot is running"}

def run_web():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_web()
