from app.core.volatility import VolatilityPredictor
from app.database.database import SessionLocal
from app.database.models import VolatilityPrediction
from datetime import datetime, timedelta
import asyncio

PROTOCOLS = [
    {"name": "Uniswap V3", "token_address": "0x1F98431c8aD98523631AE4a59f267346ea31F984", "symbol": "UNI"},
    {"name": "Aave V3", "token_address": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9", "symbol": "AAVE"},
    {"name": "Compound V3", "token_address": "0xc00e94Cb662C3520282E6f5717214004A7f26888", "symbol": "COMP"},
    {"name": "Curve Finance", "token_address": "0xD533a949740bb3306d119CC777fa900bA034cd52", "symbol": "CRV"},
]

async def main():
    predictor = VolatilityPredictor()
    db = SessionLocal()
    now = datetime.utcnow()
    for protocol in PROTOCOLS:
        for days_ago in range(7, 0, -1):
            prediction_time = now - timedelta(days=days_ago)
            predicted_vol = 0.2 + 0.1 * days_ago
            pred = VolatilityPrediction(
                upgrade_id=None,
                token_address=protocol["token_address"],
                token_symbol=protocol["symbol"],
                prediction_horizon=1,
                predicted_volatility=predicted_vol,
                confidence_interval_lower=predicted_vol * 0.8,
                confidence_interval_upper=predicted_vol * 1.2,
                model_used="demo",
                model_parameters={},
                prediction_time=prediction_time,
                created_at=prediction_time
            )
            db.add(pred)
    db.commit()
    db.close()
    print("Seeded volatility predictions for all protocols.")

if __name__ == "__main__":
    asyncio.run(main()) 