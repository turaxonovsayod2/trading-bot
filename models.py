
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Numeric, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String(100))
    registered_at = Column(DateTime, default=datetime.utcnow)
    trial_end = Column(DateTime)
    subscription_active = Column(Boolean, default=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referral_code = Column(String(50), unique=True)
    language = Column(String(2), default="en")
    rank = Column(String(20), default="novice")
    trading_volume = Column(Numeric(18,8), default=0)
    rank_bonus_referral = Column(Float, default=0.0)
    rank_bonus_fee = Column(Float, default=0.0)
    auto_buy_threshold = Column(Integer, default=80)
    stop_loss_percent = Column(Float, default=20.0)
    take_profit_percent = Column(Float, default=50.0)
    risk_per_trade_percent = Column(Float, default=5.0)
    auto_trade_enabled = Column(Boolean, default=False)
    preferred_network = Column(String(20), default="bsc")
    bsc_wallet = Column(String(100), nullable=True)
    solana_wallet = Column(String(100), nullable=True)
    ton_wallet = Column(String(100), nullable=True)

# Остальные модели (Trade, ReferralEarning и т.д.) можно добавить позже, для базовой работы хватит User
