import os
from datetime import datetime, timedelta
from app.database.database import SessionLocal
from app.database.models import MarketData

def seed_market_data(token_address, token_symbol, start_price=100.0, days=30):
    db = SessionLocal()
    base_time = datetime.utcnow() - timedelta(days=days)
    for i in range(days):
        price = start_price + i * 0.5
        timestamp = base_time + timedelta(days=i)
        market_data = MarketData(
            token_address=token_address,
            token_symbol=token_symbol,
            price=price,
            volume_24h=100000 + i * 1000,
            market_cap=1000000 + i * 10000,
            price_change_24h=0.5,
            price_change_7d=2.0,
            data_source="seed_script",
            timestamp=timestamp
        )
        db.add(market_data)
    db.commit()
    db.close()
    print(f"Seeded {days} days of price data for {token_symbol} ({token_address})")

if __name__ == "__main__":
    seed_market_data("0x1234567890123456789012345678901234567890", "TEST")
    seed_market_data("0x123", "TEST123") 