import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def analyze(token_address, network):
    """
    Анализирует токен на наличие скам‑признаков.
    Возвращает dict с risk_score (0-100) и пояснениями.
    """
    try:
        # Базовые данные через Dexscreener
        dexscreener_url = f"https://api.dexscreener.com/latest/dex/token/{token_address}"
        response = requests.get(dexscreener_url, timeout=10)
        data = response.json()
        pairs = data.get("pairs", [])
        if not pairs:
            return {"risk_score": 50, "risk_level": "RISKY", "recommendation": "HOLD", "explanation": "Токен не найден на Dexscreener."}

        # Берём первую пару
        pair = pairs[0]
        liquidity = pair.get("liquidity", {}).get("usd", 0)
        volume = pair.get("volume", {}).get("h24", 0)
        price_change = pair.get("priceChange", {}).get("h24", 0)

        # Простая эвристика
        risk_score = 50
        explanation = []

        if liquidity < 5000:
            risk_score -= 20
            explanation.append("Низкая ликвидность (<5000 USD)")
        else:
            risk_score += 10

        if volume < 10000:
            risk_score -= 10
            explanation.append("Низкий 24h объём")
        else:
            risk_score += 5

        if abs(price_change) > 50:
            risk_score -= 15
            explanation.append("Экстремальная волатильность >50% за 24ч")

        if "honeypot" in pair.get("info", {}).get("honeypot", "").lower():
            risk_score = 0
            explanation.append("Обнаружен honeypot (подозрение)")

        # Нормализуем риск‑скор
        risk_score = max(0, min(100, risk_score))

        if risk_score >= 80:
            risk_level = "GOOD"
            rec = "BUY"
        elif risk_score >= 60:
            risk_level = "OK"
            rec = "BUY"
        elif risk_score >= 30:
            risk_level = "RISKY"
            rec = "HOLD"
        else:
            risk_level = "SCAM"
            rec = "SELL"

        explanation_text = ", ".join(explanation) if explanation else "Нет явных признаков скама."

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recommendation": rec,
            "explanation": explanation_text
        }
    except Exception as e:
        logger.error(f"Anti-scam error: {e}")
        return {"risk_score": 50, "risk_level": "RISKY", "recommendation": "HOLD", "explanation": "Ошибка анализа."}
