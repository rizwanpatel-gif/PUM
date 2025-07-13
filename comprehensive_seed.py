import os
import random
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import (
    Network, Protocol, ProtocolUpgrade, BlockchainEvent, 
    RiskAssessment, VolatilityPrediction, LiquidityPrediction,
    MarketData, SentimentData, ExecutionGuidance
)
from app.database.database import Base

engine = create_engine("sqlite:///./pum.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_networks():
    db = SessionLocal()
    
    networks_data = [
        {
            "name": "ethereum",
            "chain_id": 1,
            "rpc_url": "https://mainnet.infura.io/v3/test",
            "explorer_url": "https://etherscan.io",
            "api_key": "test_key"
        },
        {
            "name": "polygon",
            "chain_id": 137,
            "rpc_url": "https://polygon-rpc.com",
            "explorer_url": "https://polygonscan.com",
            "api_key": "test_key"
        },
        {
            "name": "arbitrum",
            "chain_id": 42161,
            "rpc_url": "https://arb1.arbitrum.io/rpc",
            "explorer_url": "https://arbiscan.io",
            "api_key": "test_key"
        }
    ]
    
    for net_data in networks_data:
        existing = db.query(Network).filter_by(name=net_data["name"]).first()
        if not existing:
            network = Network(**net_data)
            db.add(network)
    
    db.commit()
    db.close()
    print("✓ Networks seeded")

def seed_protocols():
    db = SessionLocal()
    
    ethereum = db.query(Network).filter_by(name="ethereum").first()
    polygon = db.query(Network).filter_by(name="polygon").first()
    arbitrum = db.query(Network).filter_by(name="arbitrum").first()
    
    protocols_data = [
        {
            "name": "Uniswap V3",
            "address": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
            "network_id": ethereum.id,
            "protocol_type": "DEX",
            "description": "Decentralized exchange protocol"
        },
        {
            "name": "Aave V3",
            "address": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
            "network_id": ethereum.id,
            "protocol_type": "Lending",
            "description": "Decentralized lending protocol"
        },
        {
            "name": "Compound V3",
            "address": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
            "network_id": ethereum.id,
            "protocol_type": "Lending",
            "description": "Decentralized lending protocol"
        },
        {
            "name": "Curve Finance",
            "address": "0xD533a949740bb3306d119CC777fa900bA034cd52",
            "network_id": ethereum.id,
            "protocol_type": "DEX",
            "description": "Stablecoin exchange protocol"
        },
        {
            "name": "Balancer",
            "address": "0xba100000625a3754423978a60c9317c58a424e3D",
            "network_id": ethereum.id,
            "protocol_type": "DEX",
            "description": "Automated portfolio manager"
        }
    ]
    
    for protocol_data in protocols_data:
        existing = db.query(Protocol).filter_by(address=protocol_data["address"]).first()
        if not existing:
            protocol = Protocol(**protocol_data)
            db.add(protocol)
    
    db.commit()
    db.close()
    print("✓ Protocols seeded")

def seed_protocol_upgrades():
    db = SessionLocal()
    
    protocols = db.query(Protocol).all()
    upgrade_types = ["governance_proposal", "implementation_upgrade", "parameter_change", "emergency_pause"]
    statuses = ["pending", "active", "passed", "failed", "executed"]
    
    now = datetime.utcnow()
    
    for i, protocol in enumerate(protocols):
        for j in range(3):
            upgrade = ProtocolUpgrade(
                protocol_id=protocol.id,
                upgrade_type=random.choice(upgrade_types),
                title=f"Upgrade {j+1} for {protocol.name}",
                description=f"This is upgrade {j+1} for {protocol.name} with detailed description",
                proposal_id=f"PROP-{protocol.id}-{j+1}",
                status=random.choice(statuses),
                start_time=now - timedelta(days=random.randint(1, 30)),
                end_time=now + timedelta(days=random.randint(1, 30)),
                execution_time=now + timedelta(days=random.randint(1, 7)) if random.choice([True, False]) else None,
                block_number=18000000 + random.randint(1, 1000),
                transaction_hash=f"0x{random.randint(1000000, 9999999):x}",
                extra_metadata={"version": f"v{i+1}.{j+1}", "impact": "medium"}
            )
            db.add(upgrade)
    
    db.commit()
    db.close()
    print("✓ Protocol upgrades seeded")

def seed_blockchain_events():
    db = SessionLocal()
    
    networks = db.query(Network).all()
    protocols = db.query(Protocol).all()
    
    now = datetime.utcnow()
    event_types = ["Upgrade", "Transfer", "Approval", "Emergency_Pause", "Security_Patch"]
    
    for network in networks:
        for i in range(20):
            protocol = random.choice(protocols)
            event = BlockchainEvent(
                network_id=network.id,
                block_number=10000000 + random.randint(1, 10000),
                transaction_hash=f"0x{random.randint(1000000, 9999999):x}",
                from_address=f"0x{random.randint(1000000, 9999999):x}",
                to_address=protocol.address,
                event_type=random.choice(event_types),
                event_data={"info": f"Sample event {i} for {network.name}"},
                gas_used=21000 + random.randint(1, 100000),
                gas_price=100 + random.randint(1, 1000),
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440))
            )
            db.add(event)
    
    db.commit()
    db.close()
    print("✓ Blockchain events seeded")

def seed_market_data():
    db = SessionLocal()
    
    protocols = db.query(Protocol).all()
    now = datetime.utcnow()
    
    for protocol in protocols:
        base_price = random.uniform(10, 1000)
        for i in range(30):
            price = base_price + random.uniform(-10, 10)
            market_data = MarketData(
                token_address=protocol.address,
                token_symbol=protocol.name[:5].upper(),
                price=price,
                volume_24h=random.uniform(100000, 10000000),
                market_cap=random.uniform(1000000, 1000000000),
                price_change_24h=random.uniform(-20, 20),
                price_change_7d=random.uniform(-50, 50),
                data_source="seed_script",
                timestamp=datetime.utcnow() - timedelta(days=30-i)
            )
            db.add(market_data)
    
    db.commit()
    db.close()
    print("✓ Market data seeded")

def seed_risk_assessments():
    db = SessionLocal()
    
    upgrades = db.query(ProtocolUpgrade).all()
    
    risk_levels = [30, 60, 90]
    for i, upgrade in enumerate(upgrades):
        risk_score = risk_levels[i % 3]
        
        technical_risk = random.uniform(20, 80)
        governance_risk = random.uniform(20, 80)
        market_risk = random.uniform(20, 80)
        liquidity_risk = random.uniform(20, 80)
        
        overall_risk = (technical_risk + governance_risk + market_risk + liquidity_risk) / 4
        
        risk_factors = {
            "technical": {
                "complexity": random.uniform(0, 1),
                "security_audit": random.choice([True, False]),
                "bug_bounties": random.choice([True, False])
            },
            "governance": {
                "voter_participation": random.uniform(0, 1),
                "proposal_success_rate": random.uniform(0, 1),
                "quorum_met": random.choice([True, False])
            },
            "market": {
                "volatility": random.uniform(0, 1),
                "correlation": random.uniform(-1, 1),
                "liquidity": random.uniform(0, 1)
            },
            "liquidity": {
                "tvl_concentration": random.uniform(0, 1),
                "dex_volume": random.uniform(0, 1),
                "slippage": random.uniform(0, 1)
            }
        }
        
        recommendations = [
            "Monitor governance participation closely",
            "Consider hedging strategies for high volatility",
            "Diversify liquidity across multiple pools",
            "Review smart contract security measures"
        ]
        
        assessment = RiskAssessment(
            protocol_id=upgrade.protocol_id,
            upgrade_id=upgrade.id,
            overall_risk_score=overall_risk,
            technical_risk=technical_risk,
            governance_risk=governance_risk,
            market_risk=market_risk,
            liquidity_risk=liquidity_risk,
            risk_factors=risk_factors,
            recommendations=recommendations
        )
        db.add(assessment)
    
    db.commit()
    db.close()
    print("✓ Risk assessments seeded")

def seed_volatility_predictions():
    db = SessionLocal()
    
    upgrades = db.query(ProtocolUpgrade).all()
    
    for upgrade in upgrades:
        for horizon in [7, 14, 30]:
            prediction = VolatilityPrediction(
                upgrade_id=upgrade.id,
                token_address=upgrade.protocol.address,
                token_symbol=upgrade.protocol.name[:5].upper(),
                prediction_horizon=horizon,
                predicted_volatility=random.uniform(0.1, 0.8),
                confidence_interval_lower=random.uniform(0.05, 0.6),
                confidence_interval_upper=random.uniform(0.2, 1.0),
                model_used=random.choice(["GARCH", "EGARCH", "GJR-GARCH"]),
                model_parameters={"alpha": random.uniform(0, 1), "beta": random.uniform(0, 1)}
            )
            db.add(prediction)
    
    db.commit()
    db.close()
    print("✓ Volatility predictions seeded")

def seed_liquidity_predictions():
    db = SessionLocal()
    
    upgrades = db.query(ProtocolUpgrade).all()
    
    for upgrade in upgrades:
        for horizon in [7, 14, 30]:
            prediction = LiquidityPrediction(
                upgrade_id=upgrade.id,
                protocol_address=upgrade.protocol.address,
                prediction_horizon=horizon,
                predicted_tvl_change=random.uniform(-50, 100),
                predicted_volume_change=random.uniform(-30, 200),
                confidence_interval_lower=random.uniform(-80, 50),
                confidence_interval_upper=random.uniform(0, 150),
                model_used=random.choice(["ARIMA", "Prophet", "LSTM"]),
                model_parameters={"order": [1, 1, 1], "seasonal": [1, 1, 1, 12]}
            )
            db.add(prediction)
    
    db.commit()
    db.close()
    print("✓ Liquidity predictions seeded")

def seed_sentiment_data():
    db = SessionLocal()
    
    protocols = db.query(Protocol).all()
    sources = ["Twitter", "Reddit", "Discord", "Telegram"]
    
    now = datetime.utcnow()
    
    for protocol in protocols:
        for i in range(10):
            sentiment = SentimentData(
                protocol_id=protocol.id,
                source=random.choice(sources),
                sentiment_score=random.uniform(-1, 1),
                sentiment_label=random.choice(["positive", "negative", "neutral"]),
                text_content=f"Sample sentiment text for {protocol.name}",
                user_count=random.randint(100, 10000),
                engagement_metrics={"likes": random.randint(10, 1000), "shares": random.randint(5, 500)},
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 168))
            )
            db.add(sentiment)
    
    db.commit()
    db.close()
    print("✓ Sentiment data seeded")

def seed_execution_guidance():
    db = SessionLocal()
    
    upgrades = db.query(ProtocolUpgrade).all()
    action_types = ["buy", "sell", "hold", "hedge"]
    timing_recommendations = ["immediate", "wait", "specific_time"]
    
    for upgrade in upgrades:
        guidance = ExecutionGuidance(
            upgrade_id=upgrade.id,
            action_type=random.choice(action_types),
            token_address=upgrade.protocol.address,
            token_symbol=upgrade.protocol.name[:5].upper(),
            recommended_quantity=random.uniform(0.1, 10.0),
            entry_price_range={"min": random.uniform(10, 100), "max": random.uniform(100, 200)},
            exit_price_range={"min": random.uniform(50, 150), "max": random.uniform(150, 300)},
            timing_recommendation=random.choice(timing_recommendations),
            confidence_level=random.uniform(0.5, 0.95),
            risk_reward_ratio=random.uniform(1.5, 5.0),
            reasoning=f"Based on analysis of {upgrade.upgrade_type} for {upgrade.protocol.name}"
        )
        db.add(guidance)
    
    db.commit()
    db.close()
    print("✓ Execution guidance seeded")

def main():
    print("Starting comprehensive database seeding...")
    
    try:
        seed_networks()
        seed_protocols()
        seed_protocol_upgrades()
        seed_blockchain_events()
        seed_market_data()
        seed_risk_assessments()
        seed_volatility_predictions()
        seed_liquidity_predictions()
        seed_sentiment_data()
        seed_execution_guidance()
        
        print("\n✅ All data seeded successfully!")
        print("The dashboard should now display graphs and recommendations.")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 