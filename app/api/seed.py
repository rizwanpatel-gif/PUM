import random
from datetime import datetime, timedelta
from fastapi import APIRouter
from app.database.database import SessionLocal
from app.database.models import (
    Network, Protocol, ProtocolUpgrade,
    BlockchainEvent, RiskAssessment, VolatilityPrediction
)

router = APIRouter()


@router.post("/seed-demo-data")
def seed_demo_data():
    db = SessionLocal()
    try:
        # ── Networks ──────────────────────────────────────────
        nets = [
            ("ethereum", 1,   "https://mainnet.infura.io/v3/demo", "https://etherscan.io"),
            ("polygon",  137, "https://polygon-rpc.com",            "https://polygonscan.com"),
            ("arbitrum", 42161, "https://arb1.arbitrum.io/rpc",     "https://arbiscan.io"),
        ]
        net_objs = {}
        for name, chain_id, rpc, explorer in nets:
            n = db.query(Network).filter_by(name=name).first()
            if not n:
                n = Network(name=name, chain_id=chain_id, rpc_url=rpc,
                            explorer_url=explorer, api_key="demo")
                db.add(n)
                db.flush()
            net_objs[name] = n

        # ── Protocols ─────────────────────────────────────────
        protocols_data = [
            ("Uniswap V3",   "0x1F98431c8aD98523631AE4a59f267346ea31F984", "ethereum", "dex",        "Decentralized exchange protocol"),
            ("Aave V3",      "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9", "ethereum", "lending",    "Decentralized lending protocol"),
            ("Compound V3",  "0xc00e94Cb662C3520282E6f5717214004A7f26888", "ethereum", "lending",    "Algorithmic money market protocol"),
            ("Curve Finance","0xD533a949740bb3306d119CC777fa900bA034cd52", "ethereum", "dex",        "Stablecoin-focused AMM"),
            ("Balancer",     "0xba100000625a3754423978a60c9317c58a424e3D", "ethereum", "dex",        "Automated portfolio manager"),
        ]
        proto_objs = []
        for name, addr, net_name, ptype, desc in protocols_data:
            p = db.query(Protocol).filter_by(address=addr).first()
            if not p:
                p = Protocol(name=name, address=addr,
                             network_id=net_objs[net_name].id,
                             protocol_type=ptype, description=desc,
                             is_active=True)
                db.add(p)
                db.flush()
            proto_objs.append(p)

        # ── Upgrades + Risk + Volatility ──────────────────────
        statuses   = ["active", "pending", "approved", "voting", "failed"]
        upg_types  = ["governance_proposal", "implementation_upgrade",
                      "parameter_change", "security_patch"]
        titles = [
            "Fee tier adjustment for stable pools",
            "Oracle upgrade to Chainlink v2",
            "Governance module migration",
            "Emergency pause mechanism",
            "Liquidity incentive restructure",
            "Smart contract security patch",
            "Cross-chain bridge integration",
            "Parameter update: liquidation threshold",
        ]
        now = datetime.utcnow()

        upgrade_objs = []
        for i, proto in enumerate(proto_objs):
            for j in range(3):
                title  = titles[(i * 3 + j) % len(titles)]
                status = statuses[(i + j) % len(statuses)]
                upg = db.query(ProtocolUpgrade).filter_by(
                    protocol_id=proto.id, title=title
                ).first()
                if not upg:
                    upg = ProtocolUpgrade(
                        protocol_id=proto.id,
                        protocol_name=proto.name,
                        upgrade_type=upg_types[j % len(upg_types)],
                        title=title,
                        description=f"Demo upgrade: {title}",
                        status=status,
                        start_time=now - timedelta(days=random.randint(1, 30)),
                        end_time=now + timedelta(days=random.randint(1, 14)),
                        block_number=random.randint(18_000_000, 20_000_000),
                        transaction_hash=f"0x{'a' * 62}{i:02d}",
                    )
                    db.add(upg)
                    db.flush()
                upgrade_objs.append(upg)

                # Risk assessment
                if not db.query(RiskAssessment).filter_by(upgrade_id=upg.id).first():
                    technical  = random.uniform(10, 90)
                    governance = random.uniform(10, 90)
                    market     = random.uniform(10, 90)
                    liquidity  = random.uniform(10, 90)
                    overall    = (technical + governance + market + liquidity) / 4
                    db.add(RiskAssessment(
                        protocol_id=proto.id,
                        upgrade_id=upg.id,
                        overall_risk_score=overall,
                        technical_risk=technical,
                        governance_risk=governance,
                        market_risk=market,
                        liquidity_risk=liquidity,
                        risk_factors={"technical": technical, "governance": governance,
                                      "market": market, "liquidity": liquidity},
                        recommendations=["Monitor closely", "Review audit reports"],
                    ))

                # Volatility prediction
                if not db.query(VolatilityPrediction).filter_by(upgrade_id=upg.id).first():
                    vol = random.uniform(0.05, 0.55)
                    db.add(VolatilityPrediction(
                        upgrade_id=upg.id,
                        token_address=proto.address,
                        token_symbol=proto.name.split()[0].upper(),
                        prediction_horizon=30,
                        predicted_volatility=vol,
                        confidence_interval_lower=vol * 0.8,
                        confidence_interval_upper=vol * 1.2,
                        model_used="GARCH",
                        model_parameters={"p": 1, "q": 1},
                    ))

        # ── Blockchain Events ─────────────────────────────────
        event_types = ["UpgradeProposed", "VoteCast", "ProposalExecuted",
                       "ParameterChanged", "EmergencyPause"]
        for net_name, net_obj in net_objs.items():
            existing = db.query(BlockchainEvent).filter_by(
                network_id=net_obj.id).count()
            if existing < 5:
                for k in range(8):
                    db.add(BlockchainEvent(
                        network_id=net_obj.id,
                        block_number=random.randint(18_000_000, 20_000_000),
                        transaction_hash=f"0x{'b' * 60}{k:04d}",
                        from_address="0x" + "0" * 40,
                        to_address="0x" + "f" * 40,
                        event_type=event_types[k % len(event_types)],
                        event_data={"demo": True},
                        timestamp=now - timedelta(hours=random.randint(1, 72)),
                    ))

        db.commit()
        return {
            "status": "ok",
            "seeded": {
                "networks": len(net_objs),
                "protocols": len(proto_objs),
                "upgrades": len(upgrade_objs),
            }
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()
