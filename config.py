import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

ADMIN_WALLET_BSC = os.getenv("ADMIN_WALLET_BSC")
ADMIN_WALLET_SOLANA = os.getenv("ADMIN_WALLET_SOLANA")
ADMIN_WALLET_TON = os.getenv("ADMIN_WALLET_TON")

ADMIN_PRIVATE_KEY_BSC = os.getenv("ADMIN_PRIVATE_KEY_BSC")
ADMIN_PRIVATE_KEY_SOLANA = os.getenv("ADMIN_PRIVATE_KEY_SOLANA")
ADMIN_PRIVATE_KEY_TON = os.getenv("ADMIN_PRIVATE_KEY_TON")

TON_API_KEY = os.getenv("TON_API_KEY")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

SUPPORTED_NETWORKS = {
    "bsc": {
        "name": "BNB Chain",
        "rpc": "https://bsc-dataseed.binance.org/",
        "dex": "PancakeSwap",
        "router": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
        "native_currency": "BNB",
        "explorer": "https://bscscan.com/tx/",
        "type": "evm"
    },
    "solana": {
        "name": "Solana",
        "rpc": "https://api.mainnet-beta.solana.com",
        "dex": "Jupiter",
        "jupiter_api": "https://quote-api.jup.ag/v6",
        "native_currency": "SOL",
        "explorer": "https://solscan.io/tx/",
        "type": "non-evm"
    },
    "ton": {
        "name": "TON",
        "rpc": "https://toncenter.com/api/v2/jsonRPC",
        "dex": "STON.fi",
        "stonfi_api": "https://api.ston.fi/v1",
        "native_currency": "TON",
        "explorer": "https://tonscan.org/tx/",
        "type": "non-evm"
    }
}
