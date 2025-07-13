import sqlite3
import random
import json
from datetime import datetime, timedelta

def seed_database():
    conn = sqlite3.connect('pum.db')
    cursor = conn.cursor()
    
    print("Seeding database...")
    
    networks = [
        (1, "ethereum", 1, "https://mainnet.infura.io/v3/test", "https://etherscan.io", "test_key"),
        (2, "polygon", 137, "https://polygon-rpc.com", "https://polygonscan.com", "test_key"),
        (3, "arbitrum", 42161, "https://arb1.arbitrum.io/rpc", "https://arbiscan.io", "test_key")
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO networks (id, name, chain_id, rpc_url, explorer_url, api_key, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
    """, [(n[0], n[1], n[2], n[3], n[4], n[5], datetime.utcnow(), datetime.utcnow()) for n in networks])
    
    protocols = [
        (1, "Uniswap V3", "0x1F98431c8aD98523631AE4a59f267346ea31F984", 1, "DEX", "Decentralized exchange protocol"),
        (2, "Aave V3", "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9", 1, "Lending", "Decentralized lending protocol"),
        (3, "Compound V3", "0xc00e94Cb662C3520282E6f5717214004A7f26888", 1, "Lending", "Decentralized lending protocol"),
        (4, "Curve Finance", "0xD533a949740bb3306d119CC777fa900bA034cd52", 1, "DEX", "Stablecoin exchange protocol"),
        (5, "Balancer", "0xba100000625a3754423978a60c9317c58a424e3D", 1, "DEX", "Automated portfolio manager")
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO protocols (id, name, address, network_id, protocol_type, description, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
    """, [(p[0], p[1], p[2], p[3], p[4], p[5], datetime.utcnow(), datetime.utcnow()) for p in protocols])
    
    upgrade_types = ["governance_proposal", "implementation_upgrade", "parameter_change", "emergency_pause"]
    statuses = ["pending", "active", "passed", "failed", "executed"]
    now = datetime.utcnow()
    
    upgrades = []
    for protocol_id in range(1, 6):
        for j in range(3):
            upgrade_id = protocol_id * 10 + j
            start_time = now - timedelta(days=random.randint(1, 30))
            end_time = now + timedelta(days=random.randint(1, 30))
            
            upgrades.append((
                upgrade_id, protocol_id, random.choice(upgrade_types),
                f"Upgrade {j+1} for Protocol {protocol_id}",
                f"This is upgrade {j+1} with detailed description",
                f"PROP-{protocol_id}-{j+1}",
                random.choice(statuses),
                start_time, end_time,
                now + timedelta(days=random.randint(1, 7)) if random.choice([True, False]) else None,
                18000000 + random.randint(1, 1000),
                f"0x{random.randint(1000000, 9999999):x}",
                json.dumps({"version": f"v{protocol_id}.{j+1}", "impact": "medium"}),
                now, now
            ))
    
    cursor.executemany("""
        INSERT OR IGNORE INTO protocol_upgrades 
        (id, protocol_id, upgrade_type, title, description, proposal_id, status, 
         start_time, end_time, execution_time, block_number, transaction_hash, 
         extra_metadata, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, upgrades)
    
    risk_assessments = []
    for upgrade_id in range(1, 16):
        technical_risk = random.uniform(20, 80)
        governance_risk = random.uniform(20, 80)
        market_risk = random.uniform(20, 80)
        liquidity_risk = random.uniform(20, 80)
        overall_risk = (technical_risk + governance_risk + market_risk + liquidity_risk) / 4
        
        risk_factors = {
            "technical": {"complexity": random.uniform(0, 1), "security": random.uniform(0, 1)},
            "governance": {"participation": random.uniform(0, 1), "success_rate": random.uniform(0, 1)},
            "market": {"volatility": random.uniform(0, 1), "correlation": random.uniform(-1, 1)},
            "liquidity": {"concentration": random.uniform(0, 1), "volume": random.uniform(0, 1)}
        }
        
        recommendations = [
            "Monitor governance participation closely",
            "Consider hedging strategies for high volatility",
            "Diversify liquidity across multiple pools"
        ]
        
        risk_assessments.append((
            upgrade_id, (upgrade_id - 1) // 3 + 1, overall_risk,
            technical_risk, governance_risk, market_risk, liquidity_risk,
            json.dumps(risk_factors), json.dumps(recommendations), now, now
        ))
    
    cursor.executemany("""
        INSERT OR IGNORE INTO risk_assessments 
        (upgrade_id, protocol_id, overall_risk_score, technical_risk, governance_risk, 
         market_risk, liquidity_risk, risk_factors, recommendations, assessment_time, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, risk_assessments)
    
    market_data = []
    for protocol_id in range(1, 6):
        protocol_address = protocols[protocol_id-1][2]
        base_price = random.uniform(10, 1000)
        
        for i in range(30):
            price = base_price + random.uniform(-10, 10)
            timestamp = now - timedelta(days=30-i)
            
            market_data.append((
                protocol_address, protocols[protocol_id-1][1][:5].upper(),
                price, random.uniform(100000, 10000000),
                random.uniform(1000000, 1000000000),
                random.uniform(-20, 20), random.uniform(-50, 50),
                "seed_script", timestamp, now
            ))
    
    cursor.executemany("""
        INSERT OR IGNORE INTO market_data 
        (token_address, token_symbol, price, volume_24h, market_cap, 
         price_change_24h, price_change_7d, data_source, timestamp, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, market_data)
    
    volatility_predictions = []
    for upgrade_id in range(1, 16):
        for horizon in [7, 14, 30]:
            volatility_predictions.append((
                upgrade_id, protocols[(upgrade_id-1)//3][2], protocols[(upgrade_id-1)//3][1][:5].upper(),
                horizon, random.uniform(0.1, 0.8),
                random.uniform(0.05, 0.6), random.uniform(0.2, 1.0),
                random.choice(["GARCH", "EGARCH", "GJR-GARCH"]),
                json.dumps({"alpha": random.uniform(0, 1), "beta": random.uniform(0, 1)}),
                now, now
            ))
    
    cursor.executemany("""
        INSERT OR IGNORE INTO volatility_predictions 
        (upgrade_id, token_address, token_symbol, prediction_horizon, predicted_volatility,
         confidence_interval_lower, confidence_interval_upper, model_used, model_parameters,
         prediction_time, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, volatility_predictions)
    
    execution_guidance = []
    action_types = ["buy", "sell", "hold", "hedge"]
    timing_recommendations = ["immediate", "wait", "specific_time"]
    
    for upgrade_id in range(1, 16):
        execution_guidance.append((
            upgrade_id, random.choice(action_types),
            protocols[(upgrade_id-1)//3][2], protocols[(upgrade_id-1)//3][1][:5].upper(),
            random.uniform(0.1, 10.0),
            json.dumps({"min": random.uniform(10, 100), "max": random.uniform(100, 200)}),
            json.dumps({"min": random.uniform(50, 150), "max": random.uniform(150, 300)}),
            random.choice(timing_recommendations),
            random.uniform(0.5, 0.95), random.uniform(1.5, 5.0),
            f"Based on analysis of upgrade {upgrade_id}",
            now, now
        ))
    
    cursor.executemany("""
        INSERT OR IGNORE INTO execution_guidance 
        (upgrade_id, action_type, token_address, token_symbol, recommended_quantity,
         entry_price_range, exit_price_range, timing_recommendation, confidence_level,
         risk_reward_ratio, reasoning, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, execution_guidance)
    
    conn.commit()
    conn.close()
    
    print("✅ Database seeded successfully!")
    print("The dashboard should now display graphs and recommendations.")

if __name__ == "__main__":
    seed_database() 