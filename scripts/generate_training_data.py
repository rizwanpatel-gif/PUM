import random
import asyncio
from datetime import datetime, timedelta
from app.database.database import SessionLocal
from app.database.models import (
    Protocol, ProtocolUpgrade, RiskAssessment, VolatilityPrediction,
    MarketData, BlockchainEvent, Network
)

def generate_training_data():
    db = SessionLocal()
    
    try:
        print("Generating comprehensive training data...")
        
        networks = db.query(Network).all()
        if not networks:
            print("Creating networks...")
            networks = [
                Network(name="ethereum", rpc_url="https://mainnet.infura.io/v3/your_key", 
                       explorer_url="https://api.etherscan.io/api", is_active=True),
                Network(name="polygon", rpc_url="https://polygon-rpc.com", 
                       explorer_url="https://api.polygonscan.com/api", is_active=True),
                Network(name="arbitrum", rpc_url="https://arb1.arbitrum.io/rpc", 
                       explorer_url="https://api.arbiscan.io/api", is_active=True)
            ]
            for network in networks:
                db.add(network)
            db.commit()
        
        protocols = db.query(Protocol).all()
        if len(protocols) < 20:
            print("Creating protocols...")
            protocol_names = [
                "Uniswap", "Aave", "Compound", "Curve", "SushiSwap", "Balancer",
                "Yearn Finance", "MakerDAO", "Synthetix", "1inch", "PancakeSwap",
                "dYdX", "Olympus DAO", "Convex Finance", "Frax Finance", "Alchemix",
                "Rari Capital", "Badger DAO", "Fei Protocol", "Terra"
            ]
            
            for i, name in enumerate(protocol_names):
                if i >= len(protocols):
                    protocol = Protocol(
                        name=name,
                        address=f"0x{random.randint(1000000000000000000000000000000000000000, 9999999999999999999999999999999999999999):040x}",
                        network_id=random.choice(networks).id,
                        protocol_type=random.choice(["DEX", "Lending", "Yield", "Stablecoin", "Derivatives"]),
                        description=f"{name} is a leading DeFi protocol",
                        is_active=True
                    )
                    db.add(protocol)
            db.commit()
            protocols = db.query(Protocol).all()
        
        upgrades = db.query(ProtocolUpgrade).all()
        if len(upgrades) < 50:
            print("Creating protocol upgrades...")
            upgrade_types = ["governance", "implementation", "parameter_change", "security_update"]
            statuses = ["active", "pending", "completed", "failed"]
            
            for i in range(50 - len(upgrades)):
                protocol = random.choice(protocols)
                upgrade = ProtocolUpgrade(
                    protocol_id=protocol.id,
                    upgrade_type=random.choice(upgrade_types),
                    title=f"{protocol.name} Upgrade {i+1}",
                    description=f"Major upgrade for {protocol.name} protocol",
                    status=random.choice(statuses),
                    start_time=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                    end_time=datetime.utcnow() + timedelta(days=random.randint(1, 60)),
                    execution_time=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 90))
                )
                db.add(upgrade)
            db.commit()
            upgrades = db.query(ProtocolUpgrade).all()
        
        risk_assessments = db.query(RiskAssessment).all()
        if len(risk_assessments) < len(upgrades):
            print("Creating risk assessments...")
            risk_targets = [
                ("low", 5, (5, 20, 10, 15)),
                ("medium", 5, (40, 50, 55, 60)),
                ("high", 5, (80, 85, 90, 95))
            ]
            used_upgrades = set()
            for category, count, values in risk_targets:
                for _ in range(count):
                    upgrade = random.choice([u for u in upgrades if u.id not in used_upgrades])
                    used_upgrades.add(upgrade.id)
                    technical_risk, governance_risk, market_risk, liquidity_risk = values
                    overall_risk = 0.25 * (technical_risk + governance_risk + market_risk + liquidity_risk)
                    risk_assessment = RiskAssessment(
                        protocol_id=upgrade.protocol_id,
                        upgrade_id=upgrade.id,
                        overall_risk_score=overall_risk,
                        technical_risk=technical_risk,
                        governance_risk=governance_risk,
                        market_risk=market_risk,
                        liquidity_risk=liquidity_risk,
                        risk_factors={
                            "smart_contract_complexity": random.uniform(0, 100),
                            "governance_participation": random.uniform(0, 100),
                            "market_volatility": random.uniform(0, 100),
                            "liquidity_concentration": random.uniform(0, 100)
                        },
                        recommendations=[
                            "Monitor governance proposals closely",
                            "Diversify portfolio exposure",
                            "Set appropriate stop losses",
                            "Consider hedging strategies"
                        ],
                        assessment_time=datetime.utcnow()
                    )
                    db.add(risk_assessment)
            for upgrade in upgrades:
                if not any(ra.upgrade_id == upgrade.id for ra in risk_assessments) and upgrade.id not in used_upgrades:
                    technical_risk = random.uniform(20, 80)
                    governance_risk = random.uniform(15, 75)
                    market_risk = random.uniform(25, 85)
                    liquidity_risk = random.uniform(10, 70)
                    overall_risk = 0.25 * (technical_risk + governance_risk + market_risk + liquidity_risk)
                    risk_assessment = RiskAssessment(
                        protocol_id=upgrade.protocol_id,
                        upgrade_id=upgrade.id,
                        overall_risk_score=overall_risk,
                        technical_risk=technical_risk,
                        governance_risk=governance_risk,
                        market_risk=market_risk,
                        liquidity_risk=liquidity_risk,
                        risk_factors={
                            "smart_contract_complexity": random.uniform(0, 100),
                            "governance_participation": random.uniform(0, 100),
                            "market_volatility": random.uniform(0, 100),
                            "liquidity_concentration": random.uniform(0, 100)
                        },
                        recommendations=[
                            "Monitor governance proposals closely",
                            "Diversify portfolio exposure",
                            "Set appropriate stop losses",
                            "Consider hedging strategies"
                        ],
                        assessment_time=datetime.utcnow()
                    )
                    db.add(risk_assessment)
            db.commit()
        
        volatility_predictions = db.query(VolatilityPrediction).all()
        if len(volatility_predictions) < len(upgrades):
            print("Creating volatility predictions...")
            for upgrade in upgrades:
                if not any(vp.upgrade_id == upgrade.id for vp in volatility_predictions):
                    predicted_volatility = random.uniform(0.1, 0.8)
                    confidence_interval = predicted_volatility * 0.2
                    
                    volatility_prediction = VolatilityPrediction(
                        upgrade_id=upgrade.id,
                        token_address=upgrade.protocol.address,
                        token_symbol=upgrade.protocol.name[:3].upper(),
                        prediction_horizon=30,
                        predicted_volatility=predicted_volatility,
                        confidence_interval_lower=max(0, predicted_volatility - confidence_interval),
                        confidence_interval_upper=predicted_volatility + confidence_interval,
                        model_used="GARCH(1,1)",
                        model_parameters={
                            "omega": random.uniform(0.001, 0.01),
                            "alpha": random.uniform(0.05, 0.15),
                            "beta": random.uniform(0.8, 0.95)
                        },
                        prediction_time=datetime.utcnow()
                    )
                    db.add(volatility_prediction)
            db.commit()
        
        market_data_count = db.query(MarketData).count()
        if market_data_count < 1000:
            print("Creating market data...")
            for protocol in protocols:
                for i in range(50):
                    market_data = MarketData(
                        token_address=protocol.address,
                        token_symbol=protocol.name[:3].upper(),
                        price=random.uniform(1, 1000),
                        volume_24h=random.uniform(1000000, 100000000),
                        market_cap=random.uniform(10000000, 1000000000),
                        price_change_24h=random.uniform(-20, 20),
                        price_change_7d=random.uniform(-50, 50),
                        data_source="CoinGecko",
                        timestamp=datetime.utcnow() - timedelta(days=i)
                    )
                    db.add(market_data)
            db.commit()
        
        events_count = db.query(BlockchainEvent).count()
        if events_count < 500:
            print("Creating blockchain events...")
            event_types = ["upgrade_proposed", "upgrade_executed", "governance_vote", "parameter_change"]
            
            for i in range(500 - events_count):
                event = BlockchainEvent(
                    network_id=random.choice(networks).id,
                    event_type=random.choice(event_types),
                    from_address=random.choice(protocols).address,
                    to_address=random.choice(protocols).address,
                    transaction_hash=f"0x{random.randint(1000000000000000000000000000000000000000, 9999999999999999999999999999999999999999):064x}",
                    block_number=random.randint(15000000, 20000000),
                    event_data={
                        "proposal_id": random.randint(1, 1000),
                        "votes_for": random.randint(1000, 10000),
                        "votes_against": random.randint(100, 1000)
                    },
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                db.add(event)
            db.commit()
        
        print(f"✅ Training data generation complete!")
        print(f"   - Protocols: {len(db.query(Protocol).all())}")
        print(f"   - Upgrades: {len(db.query(ProtocolUpgrade).all())}")
        print(f"   - Risk Assessments: {len(db.query(RiskAssessment).all())}")
        print(f"   - Volatility Predictions: {len(db.query(VolatilityPrediction).all())}")
        print(f"   - Market Data: {db.query(MarketData).count()}")
        print(f"   - Blockchain Events: {db.query(BlockchainEvent).count()}")
        
    except Exception as e:
        print(f"Error generating training data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    generate_training_data() 