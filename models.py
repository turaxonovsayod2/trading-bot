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
    trading_volume = Column(Numeric(18, 8), default=0)
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

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token_address = Column(String(100))
    token_symbol = Column(String(50))
    network = Column(String(20))
    buy_amount = Column(Numeric(18, 8))
    buy_price = Column(Numeric(18, 8))
    buy_tx_hash = Column(String(100))
    sell_amount = Column(Numeric(18, 8), nullable=True)
    sell_price = Column(Numeric(18, 8), nullable=True)
    sell_tx_hash = Column(String(100), nullable=True)
    profit = Column(Numeric(18, 8), nullable=True)
    fee = Column(Numeric(18, 8), nullable=True)
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

class ReferralEarning(Base):
    __tablename__ = "referral_earnings"
    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey("users.id"))
    referred_user_id = Column(Integer, ForeignKey("users.id"))
    trade_id = Column(Integer, ForeignKey("trades.id"))
    amount = Column(Numeric(18, 8))
    network = Column(String(20))
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

class PartnerBalance(Base):
    __tablename__ = "partner_balances"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    total_earned = Column(Numeric(18, 8), default=0)
    available_balance = Column(Numeric(18, 8), default=0)
    withdrawn = Column(Numeric(18, 8), default=0)

class AdminBalance(Base):
    __tablename__ = "admin_balances"
    id = Column(Integer, primary_key=True)
    network = Column(String(20), unique=True)
    total_earned = Column(Numeric(18, 8), default=0)
    paid_to_partners = Column(Numeric(18, 8), default=0)
    withdrawn = Column(Numeric(18, 8), default=0)
    current_balance = Column(Numeric(18, 8), default=0)

class MasterTrader(Base):
    __tablename__ = "master_traders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    is_public = Column(Boolean, default=False)
    total_subscribers = Column(Integer, default=0)
    total_copied_volume = Column(Numeric(18,8), default=0)

class CopySubscription(Base):
    __tablename__ = "copy_subscriptions"
    id = Column(Integer, primary_key=True)
    subscriber_id = Column(Integer, ForeignKey("users.id"))
    master_id = Column(Integer, ForeignKey("users.id"))
    copy_percent = Column(Float, default=100.0)
    auto_copy = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CopyTrade(Base):
    __tablename__ = "copy_trades"
    id = Column(Integer, primary_key=True)
    master_trade_id = Column(Integer, ForeignKey("trades.id"))
    subscriber_trade_id = Column(Integer, ForeignKey("trades.id"))
    subscriber_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Numeric(18,8))
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class SecurityEvent(Base):
    __tablename__ = "security_events"
    id = Column(Integer, primary_key=True)
    event_type = Column(String(100))
    severity = Column(String(20))
    details = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)

class BlockedUser(Base):
    __tablename__ = "blocked_users"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    reason = Column(String(200))
    blocked_until = Column(DateTime)

class BlacklistedWallet(Base):
    __tablename__ = "blacklisted_wallets"
    id = Column(Integer, primary_key=True)
    wallet_address = Column(String(100), unique=True)
    network = Column(String(20))
    reason = Column(String(200))
