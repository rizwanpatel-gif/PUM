import random
from app.database.database import SessionLocal
from app.database.models import ProtocolUpgrade, RiskAssessment

def randomize_risk_scores():
    db = SessionLocal()
    upgrades = db.query(ProtocolUpgrade).all()
    for upgrade in upgrades:
        ra = db.query(RiskAssessment).filter_by(upgrade_id=upgrade.id).first()
        if not ra:
            ra = RiskAssessment(upgrade_id=upgrade.id, protocol_id=upgrade.protocol_id)
            db.add(ra)
        technical = random.uniform(0, 100)
        governance = random.uniform(0, 100)
        market = random.uniform(0, 100)
        liquidity = random.uniform(0, 100)
        overall = 0.25 * (technical + governance + market + liquidity)
        ra.technical_risk = technical
        ra.governance_risk = governance
        ra.market_risk = market
        ra.liquidity_risk = liquidity
        ra.overall_risk_score = overall
        ra.risk_factors = {
            "technical": technical,
            "governance": governance,
            "market": market,
            "liquidity": liquidity
        }
    db.commit()
    db.close()
    print("Randomized risk scores for all upgrades.")

if __name__ == "__main__":
    randomize_risk_scores() 