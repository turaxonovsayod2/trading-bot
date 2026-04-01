import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from models import MasterTrader, User, CopySubscription, Trade

logger = logging.getLogger(__name__)

def publish_trade(master_user_id, trade_id):
    session = SessionLocal()
    try:
        master = session.query(MasterTrader).filter(MasterTrader.user_id == master_user_id).first()
        if not master or not master.is_public:
            return
        trade = session.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            return
        subscriptions = session.query(CopySubscription).filter(CopySubscription.master_id == master.user_id).all()
        for sub in subscriptions:
            # Создаём предложение копирования для подписчика
            # Здесь должна быть логика отправки уведомления
            pass
    finally:
        session.close()
