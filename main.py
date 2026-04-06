
import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Токен берем из переменной окружения BOT_TOKEN
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Токен бота не найден. Добавьте BOT_TOKEN в Secrets Replit.")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('✅ Бот работает! Отправьте /help для списка команд.')

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Доступные команды:\n/start - приветствие\n/help - помощь')

# Запуск бота
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    print('Бот запущен и слушает сообщения...')
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
