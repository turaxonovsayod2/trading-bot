
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set!")

# Импортируем твои обработчики команд из папки bot
import bot.handlers as handlers

# Создаём приложение Telegram
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Регистрируем команды
telegram_app.add_handler(CommandHandler("start", handlers.start))
# Добавь сюда другие обработчики команд, например:
# telegram_app.add_handler(CommandHandler("help", handlers.help_command))
# ... и так далее

# Создаём FastAPI приложение для Webhook
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
