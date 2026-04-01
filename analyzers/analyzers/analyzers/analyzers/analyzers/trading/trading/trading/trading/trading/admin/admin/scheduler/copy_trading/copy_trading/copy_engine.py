import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from models import CopySubscription, CopyTrade

logger = logging.getLogger(__name__)

def create_copy_trade(master_trade_id, subscriber_id, amount):
    # Заглушка
    pass
