import logging
from datetime import datetime
from sqlalchemy.orm import Session
from models import Trade, User, PartnerBalance, AdminBalance
from config import ADMIN_WALLET_BSC, ADMIN_WALLET_SOLANA, ADMIN_WALLET_TON
from database import SessionLocal

logger = logging.getLogger(__name__)

def execute_buy(user_id, token_address, amount, network):
    """
    Создаёт сделку покупки (только запись в БД, реальная транзакция создаётся в кошельке).
    Возвращает dict с результатом.
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            return {"success": False, "error": "User not found"}

        trade = Trade(
            user_id=user.id,
            token_address=token_address,
            token_symbol="UNKNOWN",
            network=network,
            buy_amount=amount,
            buy_price=0.0,  # будет получено из оракла
            buy_tx_hash="pending",
            status="open"
        )
        session.add(trade)
        session.commit()
        return {"success": True, "trade_id": trade.id}
    except Exception as e:
        logger.error(f"Buy error: {e}")
        return {"success": False, "error": str(e)}
    finally:
        session.close()

def execute_sell(trade_id):
    """
    Закрывает сделку, рассчитывает прибыль и комиссию.
    """
    session = SessionLocal()
    try:
        trade = session.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            return {"success": False, "error": "Trade not found"}

        # Здесь должна быть логика получения цены продажи, но для простоты используем фиктивную
        sell_price = 0.0
        profit = (sell_price - trade.buy_price) * trade.buy_amount
        trade.sell_price = sell_price
        trade.sell_amount = trade.buy_amount
        trade.profit = profit
        trade.status = "closed"
        trade.closed_at = datetime.utcnow()

        if profit > 0:
            commission = profit * 0.01
            trade.fee = commission

            # Начисление админу
            admin_balance = session.query(AdminBalance).filter(AdminBalance.network == trade.network).first()
            if not admin_balance:
                admin_balance = AdminBalance(network=trade.network)
                session.add(admin_balance)
            admin_balance.total_earned += commission * 0.7
            admin_balance.current_balance += commission * 0.7

            # Начисление рефералу
            user = session.query(User).filter(User.id == trade.user_id).first()
            if user and user.referrer_id:
                partner_share = commission * 0.3
                partner_balance = session.query(PartnerBalance).filter(PartnerBalance.user_id == user.referrer_id).first()
                if not partner_balance:
                    partner_balance = PartnerBalance(user_id=user.referrer_id)
                    session.add(partner_balance)
                partner_balance.total_earned += partner_share
                partner_balance.available_balance += partner_share

        session.commit()
        return {"success": True}
    except Exception as e:
        logger.error(f"Sell error: {e}")
        return {"success": False, "error": str(e)}
    finally:
        session.close()

def check_open_positions():
    """
    Периодическая задача: проверяет цены открытых позиций и при достижении SL/TP создаёт транзакцию продажи.
    Здесь только заглушка.
    """
    pass
