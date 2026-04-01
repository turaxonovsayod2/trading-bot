import logging
import json
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Импорт наших модулей – если модуль не найден, будут заглушки
try:
    from config import SUPPORTED_NETWORKS, ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY
    from models import User, Trade, ReferralEarning, PartnerBalance, AdminBalance, MasterTrader, CopySubscription, CopyTrade, SecurityEvent, BlockedUser, BlacklistedWallet
    from database import SessionLocal
    from analyzers.anti_scam import analyze as anti_scam_analyze
    from analyzers.smart_money import analyze as smart_money_analyze
    from analyzers.dev_behavior import analyze as dev_behavior_analyze
    from analyzers.social_ai import analyze as social_ai_analyze
    from trading.engine import execute_buy, execute_sell, check_open_positions
    from trading.risk_manager import calculate_position_size, check_stop_loss_take_profit
    from utils.i18n import get_text
    from utils.logger import SecurityLogger
except ImportError as e:
    logging.warning(f"Import error in handlers: {e}. Using stubs.")
    # Заглушки для отсутствующих модулей
    SUPPORTED_NETWORKS = {}
    def anti_scam_analyze(token, network): return {"risk_score": 50, "risk_level": "RISKY", "recommendation": "HOLD", "explanation": "Заглушка"}
    def smart_money_analyze(token, network): return {"score": 50}
    def dev_behavior_analyze(token, network): return {"score": 50}
    def social_ai_analyze(token, network): return {"score": 50}
    def execute_buy(user_id, token, amount, network): return {"success": False, "error": "Заглушка"}
    def execute_sell(trade_id): return {"success": False, "error": "Заглушка"}
    def calculate_position_size(user_id, network): return 0.0
    def check_open_positions(): pass
    def get_text(lang, key, **kwargs): return key
    SecurityLogger = None
    SessionLocal = None
    # Пустые модели, чтобы не ломались импорты
    class User: pass
    class Trade: pass
    class ReferralEarning: pass
    class PartnerBalance: pass
    class AdminBalance: pass
    class MasterTrader: pass
    class CopySubscription: pass
    class CopyTrade: pass
    class SecurityEvent: pass
    class BlockedUser: pass
    class BlacklistedWallet: pass

logger = logging.getLogger(__name__)

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================

async def get_user_language(user_id):
    """Получить язык пользователя из базы данных"""
    if SessionLocal is None:
        return "en"
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        lang = user.language if user else "en"
    finally:
        session.close()
    return lang

async def get_or_create_user(update: Update):
    """Создать пользователя, если его нет в базе"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    if SessionLocal is None:
        return None
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            referral_code = f"ref_{user_id}"
            user = User(
                telegram_id=user_id,
                username=username,
                referral_code=referral_code,
                trial_end=datetime.utcnow() + timedelta(days=3)
            )
            session.add(user)
            session.commit()
            logger.info(f"New user registered: {username} ({user_id})")
        else:
            if user.username != username:
                user.username = username
                session.commit()
    finally:
        session.close()
    return user

def get_user_by_id(user_id):
    if SessionLocal is None:
        return None
    session = SessionLocal()
    try:
        return session.query(User).filter(User.telegram_id == user_id).first()
    finally:
        session.close()

async def get_user_referral_link(user_id, bot_username):
    user = get_user_by_id(user_id)
    if user and user.referral_code:
        return f"https://t.me/{bot_username}?start={user.referral_code}"
    return ""

# ===================== ОСНОВНЫЕ ОБРАБОТЧИКИ =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_or_create_user(update)
    lang = await get_user_language(update.effective_user.id)

    # Проверка реферального кода
    if context.args and user:
        ref_code = context.args[0]
        if ref_code.startswith("ref_"):
            try:
                referrer_id = int(ref_code.split("_")[1])
                if referrer_id != user.telegram_id and SessionLocal:
                    session = SessionLocal()
                    try:
                        referrer = session.query(User).filter(User.telegram_id == referrer_id).first()
                        if referrer and not user.referrer_id:
                            user.referrer_id = referrer.id
                            session.commit()
                            logger.info(f"User {user.telegram_id} referred by {referrer_id}")
                    finally:
                        session.close()
            except:
                pass

    text = get_text(lang, "welcome_message")
    await update.message.reply_text(text)

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi")],
        [InlineKeyboardButton("🇵🇭 Filipino", callback_data="lang_tl")],
        [InlineKeyboardButton("🇳🇬 Nigeria English", callback_data="lang_ng")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your language / Выберите язык:", reply_markup=reply_markup)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    if data.startswith("lang_") and SessionLocal:
        lang = data.split("_")[1]
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if user:
                user.language = lang
                session.commit()
                text = get_text(lang, "language_changed")
                await query.edit_message_text(text)
            else:
                await query.edit_message_text("Error: user not found")
        finally:
            session.close()

async def connect_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Подключение кошелька в разработке. Пожалуйста, используйте MetaMask/Phantom/Tonkeeper.")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите адрес токена. Пример: /analyze 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")
        return

    token = context.args[0]
    # Определяем сеть по префиксу
    if token.startswith("0x"):
        network = "bsc"
    elif token.startswith(("EQD", "UQD")):
        network = "ton"
    else:
        network = "solana"

    anti_scam = anti_scam_analyze(token, network)
    smart_money = smart_money_analyze(token, network)
    dev_behavior = dev_behavior_analyze(token, network)
    social_ai = social_ai_analyze(token, network)

    # Примерный расчёт риск-скора
    risk_score = (anti_scam.get("risk_score", 50) +
                  smart_money.get("score", 50) +
                  dev_behavior.get("score", 50) +
                  social_ai.get("score", 50)) // 4

    if risk_score >= 80:
        level = "GOOD"
    elif risk_score >= 60:
        level = "OK"
    elif risk_score >= 30:
        level = "RISKY"
    else:
        level = "SCAM"

    text = f"🔍 Анализ токена {token}\n\n"
    text += f"Риск-скор: {risk_score} ({level})\n"
    text += f"Рекомендация: {anti_scam.get('recommendation', 'HOLD')}\n"
    text += f"Пояснение: {anti_scam.get('explanation', 'Нет данных')}\n"
    await update.message.reply_text(text)

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /buy <адрес> <сумма> (например, /buy 0x... 0.5)")
        return
    token = context.args[0]
    amount = context.args[1]
    await update.message.reply_text(f"Покупка {amount} токена {token} (в разработке).")

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /sell <адрес>")
        return
    token = context.args[0]
    await update.message.reply_text(f"Продажа токена {token} (в разработке).")

async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if SessionLocal is None:
        await update.message.reply_text("Портфель временно недоступен.")
        return
    session = SessionLocal()
    try:
        trades = session.query(Trade).filter(Trade.user_id == user_id, Trade.status == "open").all()
        if not trades:
            await update.message.reply_text("У вас нет открытых позиций.")
            return
        text = "📊 Ваш портфель:\n"
        for t in trades:
            text += f"• {t.token_symbol} ({t.network}): {t.buy_amount} куплено по {t.buy_price}\n"
        await update.message.reply_text(text)
    finally:
        session.close()

async def partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if SessionLocal is None:
        await update.message.reply_text("Партнёрская статистика временно недоступна.")
        return
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await update.message.reply_text("Пользователь не найден.")
            return
        referrers = session.query(User).filter(User.referrer_id == user.id).count()
        balance = session.query(PartnerBalance).filter(PartnerBalance.user_id == user.id).first()
        total_earned = balance.total_earned if balance else 0
        available = balance.available_balance if balance else 0
        withdrawn = balance.withdrawn if balance else 0

        bot_username = (await update.get_bot()).username
        text = f"🤝 Ваша партнёрская статистика:\n"
        text += f"Приглашено: {referrers}\n"
        text += f"Всего заработано: {total_earned:.2f} USDT\n"
        text += f"Доступно для вывода: {available:.2f} USDT\n"
        text += f"Выведено: {withdrawn:.2f} USDT\n"
        text += f"Ваша реферальная ссылка: {await get_user_referral_link(user_id, bot_username)}"
        await update.message.reply_text(text)
    finally:
        session.close()

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if SessionLocal is None:
        await update.message.reply_text("Профиль временно недоступен.")
        return
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await update.message.reply_text("Пользователь не найден.")
            return
        text = f"👤 Ваш профиль\n"
        text += f"Ранг: {user.rank.upper()}\n"
        text += f"Торговый объём: {user.trading_volume:.2f} USDT\n"
        text += f"Бонус к реферальной комиссии: +{int(user.rank_bonus_referral*100)}%\n"
        text += f"Снижение комиссии бота: -{int(user.rank_bonus_fee*100)}%\n"
        await update.message.reply_text(text)
    finally:
        session.close()

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user_by_id(user_id)
    if not user:
        await update.message.reply_text("Пользователь не найден.")
        return
    text = f"⚙️ Текущие настройки:\n"
    text += f"Стоп-лосс: {user.stop_loss_percent}%\n"
    text += f"Тейк-профит: {user.take_profit_percent}%\n"
    text += f"Риск на сделку: {user.risk_per_trade_percent}%\n"
    text += f"Автоторговля: {'Включена' if user.auto_trade_enabled else 'Выключена'}\n"
    text += f"Порог авто-покупки: {'GOOD' if user.auto_buy_threshold == 80 else 'OK'}\n"
    text += f"Сеть: {user.preferred_network.upper()}\n"
    await update.message.reply_text(text)

async def set_sl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /set_sl <процент> (1-50)")
        return
    try:
        sl = float(context.args[0])
        if sl < 1 or sl > 50:
            raise ValueError
        user_id = update.effective_user.id
        if SessionLocal is None:
            await update.message.reply_text("База данных недоступна.")
            return
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            user.stop_loss_percent = sl
            session.commit()
            await update.message.reply_text(f"Стоп-лосс установлен на {sl}%.")
        finally:
            session.close()
    except:
        await update.message.reply_text("Ошибка: введите число от 1 до 50.")

async def set_tp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /set_tp <процент> (10-200)")
        return
    try:
        tp = float(context.args[0])
        if tp < 10 or tp > 200:
            raise ValueError
        user_id = update.effective_user.id
        if SessionLocal is None:
            await update.message.reply_text("База данных недоступна.")
            return
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            user.take_profit_percent = tp
            session.commit()
            await update.message.reply_text(f"Тейк-профит установлен на {tp}%.")
        finally:
            session.close()
    except:
        await update.message.reply_text("Ошибка: введите число от 10 до 200.")

async def set_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /set_risk <процент> (1-50)")
        return
    try:
        risk = float(context.args[0])
        if risk < 1 or risk > 50:
            raise ValueError
        user_id = update.effective_user.id
        if SessionLocal is None:
            await update.message.reply_text("База данных недоступна.")
            return
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            user.risk_per_trade_percent = risk
            session.commit()
            await update.message.reply_text(f"Риск на сделку установлен на {risk}%.")
        finally:
            session.close()
    except:
        await update.message.reply_text("Ошибка: введите число от 1 до 50.")

async def set_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /set_network bsc|solana|ton")
        return
    net = context.args[0].lower()
    if net not in SUPPORTED_NETWORKS:
        await update.message.reply_text("Поддерживаемые сети: bsc, solana, ton")
        return
    user_id = update.effective_user.id
    if SessionLocal is None:
        await update.message.reply_text("База данных недоступна.")
        return
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        user.preferred_network = net
        session.commit()
        await update.message.reply_text(f"Сеть установлена: {net.upper()}")
    finally:
        session.close()

async def auto_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /auto_trade on|off  или /auto_trade threshold 60|80")
        return
    cmd = context.args[0].lower()
    user_id = update.effective_user.id
    if SessionLocal is None:
        await update.message.reply_text("База данных недоступна.")
        return
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if cmd == "on":
            user.auto_trade_enabled = True
            await update.message.reply_text("Автоторговля включена.")
        elif cmd == "off":
            user.auto_trade_enabled = False
            await update.message.reply_text("Автоторговля выключена.")
        elif cmd == "threshold":
            if len(context.args) < 2:
                await update.message.reply_text("Укажите порог: 60 или 80")
                return
            thr = int(context.args[1])
            if thr not in (60, 80):
                await update.message.reply_text("Порог может быть только 60 (OK) или 80 (GOOD)")
                return
            user.auto_buy_threshold = thr
            await update.message.reply_text(f"Порог авто-покупки установлен на {thr} ({'OK' if thr==60 else 'GOOD'})")
        else:
            await update.message.reply_text("Неверная команда.")
        session.commit()
    finally:
        session.close()

async def top_traders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if SessionLocal is None:
        await update.message.reply_text("Рейтинг временно недоступен.")
        return
    session = SessionLocal()
    try:
        top = session.query(User).order_by(User.trading_volume.desc()).limit(10).all()
        text = "🏆 Топ трейдеров по объёму:\n"
        for i, u in enumerate(top, 1):
            text += f"{i}. @{u.username or u.telegram_id} — {u.trading_volume:.2f} USDT\n"
        await update.message.reply_text(text)
    finally:
        session.close()

async def copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Copy-trading: используйте /copy_on <ID трейдера> для подписки, /copy_off для отписки, /copy_percent <ID> <процент> для настройки, /copy_auto <ID> on/off для авто-копирования.")

async def copy_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /copy_on <ID трейдера>")
        return
    try:
        master_id = int(context.args[0])
    except:
        await update.message.reply_text("ID трейдера должен быть числом.")
        return
    subscriber_id = update.effective_user.id
    if SessionLocal is None:
        await update.message.reply_text("Копирование временно недоступно.")
        return
    session = SessionLocal()
    try:
        master = session.query(User).filter(User.telegram_id == master_id).first()
        if not master:
            await update.message.reply_text("Трейдер не найден.")
            return
        sub = session.query(CopySubscription).filter(CopySubscription.subscriber_id == subscriber_id, CopySubscription.master_id == master.id).first()
        if sub:
            await update.message.reply_text("Вы уже подписаны на этого трейдера.")
            return
        new_sub = CopySubscription(subscriber_id=subscriber_id, master_id=master.id, copy_percent=100.0, auto_copy=False)
        session.add(new_sub)
        session.commit()
        await update.message.reply_text(f"Вы подписались на @{master.username}.")
    finally:
        session.close()

async def copy_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /copy_off <ID трейдера>")
        return
    try:
        master_id = int(context.args[0])
    except:
        await update.message.reply_text("ID трейдера должен быть числом.")
        return
    subscriber_id = update.effective_user.id
    if SessionLocal is None:
        await update.message.reply_text("Копирование временно недоступно.")
        return
    session = SessionLocal()
    try:
        sub = session.query(CopySubscription).filter(CopySubscription.subscriber_id == subscriber_id, CopySubscription.master_id == master_id).first()
        if sub:
            session.delete(sub)
            session.commit()
            await update.message.reply_text("Вы отписались.")
        else:
            await update.message.reply_text("Подписка не найдена.")
    finally:
        session.close()

async def copy_percent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /copy_percent <ID трейдера> <процент (1-100)>")
        return
    try:
        master_id = int(context.args[0])
        percent = float(context.args[1])
        if percent < 1 or percent > 100:
            raise ValueError
    except:
        await update.message.reply_text("Неверный формат. Пример: /copy_percent 123456 50")
        return
    subscriber_id = update.effective_user.id
    if SessionLocal is None:
        await update.message.reply_text("Копирование временно недоступно.")
        return
    session = SessionLocal()
    try:
        sub = session.query(CopySubscription).filter(CopySubscription.subscriber_id == subscriber_id, CopySubscription.master_id == master_id).first()
        if sub:
            sub.copy_percent = percent
            session.commit()
            await update.message.reply_text(f"Процент копирования установлен на {percent}%.")
        else:
            await update.message.reply_text("Подписка не найдена.")
    finally:
        session.close()

async def copy_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /copy_auto <ID трейдера> on|off")
        return
    try:
        master_id = int(context.args[0])
        mode = context.args[1].lower()
        if mode not in ("on", "off"):
            raise ValueError
    except:
        await update.message.reply_text("Неверный формат. Пример: /copy_auto 123456 on")
        return
    auto = mode == "on"
    subscriber_id = update.effective_user.id
    if SessionLocal is None:
        await update.message.reply_text("Копирование временно недоступно.")
        return
    session = SessionLocal()
    try:
        sub = session.query(CopySubscription).filter(CopySubscription.subscriber_id == subscriber_id, CopySubscription.master_id == master_id).first()
        if sub:
            sub.auto_copy = auto
            session.commit()
            await update.message.reply_text(f"Автокопирование {'включено' if auto else 'выключено'}.")
        else:
            await update.message.reply_text("Подписка не найдена.")
    finally:
        session.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🤖 Доступные команды:
/start — регистрация
/language — выбор языка
/connect_wallet — подключить кошелёк
/analyze <адрес> — анализ токена
/buy <адрес> <сумма> — ручная покупка
/sell <адрес> — продажа позиции
/portfolio — портфель
/partner — партнёрская статистика
/profile — ваш профиль
/settings — текущие настройки
/set_sl <процент> — установить стоп-лосс
/set_tp <процент> — установить тейк-профит
/set_risk <процент> — установить риск на сделку
/set_network bsc/solana/ton — выбрать сеть
/auto_trade on/off — включить/выключить автоторговлю
/auto_trade threshold 60|80 — порог авто-покупки
/top_traders — рейтинг трейдеров
/copy — меню копирования
/help — эта справка
"""
    await update.message.reply_text(text)
