import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import PartnerBalance, User, WithdrawalRequest
from trading.engine import execute_withdrawal

logger = logging.getLogger(__name__)

def process_weekly_payouts():
    """
    Выплачивает партнёрам с балансом >= 10 USDT.
    Выполняется раз в неделю (по расписанию).
    """
    session = SessionLocal()
    try:
        partners = session.query(PartnerBalance).filter(PartnerBalance.available_balance >= 10).all()
        for partner in partners:
            user = session.query(User).filter(User.id == partner.user_id).first()
            if user and user.preferred_network:
                # Создаём заявку на вывод
                withdrawal = WithdrawalRequest(
                    user_id=user.id,
                    amount=partner.available_balance,
                    network=user.preferred_network,
                    wallet_address=getattr(user, f"{user.preferred_network}_wallet"),
                    type="partner",
                    status="pending"
                )
                session.add(withdrawal)
                # Обнуляем баланс
                partner.available_balance = 0
        session.commit()
        logger.info(f"Weekly payouts processed: {len(partners)} partners")
    except Exception as e:
        logger.error(f"Payout error: {e}")
    finally:
        session.close()
