import os
from datetime import datetime, timedelta
from app.database.database import SessionLocal
from app.database.models import Network, BlockchainEvent

def get_or_create_network(db, name, chain_id, rpc_url, explorer_url, api_key=None):
    network = db.query(Network).filter_by(name=name).first()
    if not network:
        network = Network(
            name=name,
            chain_id=chain_id,
            rpc_url=rpc_url,
            explorer_url=explorer_url,
            api_key=api_key or "test_key"
        )
        db.add(network)
        db.commit()
    return network

def seed_blockchain_events():
    db = SessionLocal()
    now = datetime.utcnow()
    networks = [
        {
            "name": "ethereum",
            "chain_id": 1,
            "rpc_url": "https://mainnet.infura.io/v3/test",
            "explorer_url": "https://etherscan.io"
        },
        {
            "name": "polygon",
            "chain_id": 137,
            "rpc_url": "https://polygon-rpc.com",
            "explorer_url": "https://polygonscan.com"
        },
        {
            "name": "arbitrum",
            "chain_id": 42161,
            "rpc_url": "https://arb1.arbitrum.io/rpc",
            "explorer_url": "https://arbiscan.io"
        }
    ]
    for net in networks:
        network = get_or_create_network(db, **net)
        for i in range(10):
            event = BlockchainEvent(
                network_id=network.id,
                block_number=10000000 + i,
                transaction_hash=f"0x{network.name}{i:064d}"[-66:],
                from_address=f"0xfrom{network.name}{i:04d}"[-42:],
                to_address=f"0xto{network.name}{i:04d}"[-42:],
                event_type="Upgrade" if i % 2 == 0 else "Transfer",
                event_data={"info": f"Sample event {i} for {network.name}"},
                gas_used=21000 + i * 10,
                gas_price=100 + i,
                timestamp=now - timedelta(minutes=10 * i)
            )
            db.add(event)
    db.commit()
    db.close()
    print("Seeded blockchain events for ethereum, polygon, and arbitrum.")

if __name__ == "__main__":
    seed_blockchain_events() 