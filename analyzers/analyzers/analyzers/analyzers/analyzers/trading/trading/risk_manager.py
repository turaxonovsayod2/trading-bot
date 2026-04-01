import logging
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal

logger = logging.getLogger(__name__)

def calculate_position_size(user_id, network):
    """
    Возвращает максимальную сумму для сделки на основе настроек пользователя.
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            return 0.0
        # Предполагаем, что у пользователя есть баланс в USD (должен храниться в БД)
        # Для простоты возвращаем фиксированное значение
        return 100.0  # placeholder
    finally:
        session.close()

def check_stop_loss_take_profit(trade, current_price):
    """
    Проверяет, достигнут ли стоп-лосс или тейк-профит.
    """
    profit_percent = (current_price - trade.buy_price) / trade.buy_price * 100
    user = trade.user
    if profit_percent >= user.take_profit_percent:
        return "take_profit"
    if profit_percent <= -user.stop_loss_percent:
        return "stop_loss"
    return None
