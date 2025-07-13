import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from loguru import logger

from app.config import NETWORKS, PROTOCOL_ADDRESSES
from app.database.models import Network, Protocol, BlockchainEvent, ProtocolUpgrade
from app.database.database import SessionLocal


class BlockchainMonitor:
    
    def __init__(self):
        self.web3_connections: Dict[str, Web3] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_running = False
        
    async def initialize(self):
        logger.info("Initializing blockchain monitor...")
        
        for network_name, network_config in NETWORKS.items():
            try:
                w3 = Web3(Web3.HTTPProvider(network_config["rpc_url"]))
                if network_name in ["polygon", "arbitrum"]:
                    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
                
                if w3.is_connected():
                    self.web3_connections[network_name] = w3
                    logger.info(f"Connected to {network_name} network")
                else:
                    logger.warning(f"Failed to connect to {network_name} network")
            except Exception as e:
                logger.error(f"Error connecting to {network_name}: {e}")
        
        self.session = aiohttp.ClientSession()
        
        await self._initialize_database()
        
    async def _initialize_database(self):
        db = SessionLocal()
        try:
            for network_name, network_config in NETWORKS.items():
                existing_network = db.query(Network).filter(
                    Network.name == network_name
                ).first()
                
                if not existing_network:
                    network = Network(
                        name=network_name,
                        chain_id=network_config["chain_id"],
                        rpc_url=network_config["rpc_url"],
                        explorer_url=network_config["explorer"],
                        api_key=network_config["api_key"]
                    )
                    db.add(network)
                    logger.info(f"Added network: {network_name}")
            
            for protocol_name, protocol_address in PROTOCOL_ADDRESSES.items():
                existing_protocol = db.query(Protocol).filter(
                    Protocol.address == protocol_address
                ).first()
                
                if not existing_protocol:
                    network_name = "ethereum"
                    if "polygon" in protocol_name.lower():
                        network_name = "polygon"
                    elif "arbitrum" in protocol_name.lower():
                        network_name = "arbitrum"
                    
                    network = db.query(Network).filter(
                        Network.name == network_name
                    ).first()
                    
                    if network:
                        protocol = Protocol(
                            name=protocol_name,
                            address=protocol_address,
                            network_id=network.id,
                            protocol_type="DeFi Protocol"
                        )
                        db.add(protocol)
                        logger.info(f"Added protocol: {protocol_name}")
            
            db.commit()
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def start_monitoring(self):
        self.is_running = True
        logger.info("Starting blockchain monitoring...")
        
        tasks = []
        for network_name in self.web3_connections.keys():
            task = asyncio.create_task(self._monitor_network(network_name))
            tasks.append(task)
        
        governance_task = asyncio.create_task(self._monitor_governance())
        tasks.append(governance_task)
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
        finally:
            self.is_running = False
    
    async def _monitor_network(self, network_name: str):
        logger.info(f"Starting monitoring for {network_name}")
        
        while self.is_running:
            try:
                w3 = self.web3_connections[network_name]
                latest_block = w3.eth.block_number
                
                for block_num in range(latest_block - 9, latest_block + 1):
                    await self._process_block(network_name, block_num)
                
                await asyncio.sleep(15)
                
            except Exception as e:
                logger.error(f"Error monitoring {network_name}: {e}")
                await asyncio.sleep(30)
    
    async def _process_block(self, network_name: str, block_number: int):
        try:
            w3 = self.web3_connections[network_name]
            block = w3.eth.get_block(block_number, full_transactions=True)
            
            for tx in block.transactions:
                if self._is_protocol_transaction(tx):
                    await self._process_transaction(network_name, tx, block)
                    
        except Exception as e:
            logger.error(f"Error processing block {block_number} on {network_name}: {e}")
    
    def _is_protocol_transaction(self, tx) -> bool:
        protocol_addresses = set(PROTOCOL_ADDRESSES.values())
        return (
            tx.to and tx.to.lower() in protocol_addresses or
            tx.get('from', '').lower() in protocol_addresses
        )
    
    async def _process_transaction(self, network_name: str, tx, block):
        db = SessionLocal()
        try:
            network = db.query(Network).filter(Network.name == network_name).first()
            if not network:
                return
            
            event = BlockchainEvent(
                network_id=network.id,
                block_number=block.number,
                transaction_hash=tx.hash.hex(),
                from_address=tx.get('from', ''),
                to_address=tx.get('to', ''),
                event_type=self._determine_event_type(tx),
                event_data=self._extract_event_data(tx),
                gas_used=tx.get('gas', 0),
                gas_price=tx.get('gasPrice', 0),
                timestamp=datetime.fromtimestamp(block.timestamp)
            )
            
            db.add(event)
            db.commit()
            
            if self._is_upgrade_transaction(tx):
                await self._process_upgrade_event(network_name, tx, block)
                
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _determine_event_type(self, tx) -> str:
        if tx.get('to') in PROTOCOL_ADDRESSES.values():
            return "Protocol_Interaction"
        return "Transfer"
    
    def _extract_event_data(self, tx) -> Dict[str, Any]:
        return {
            "value": str(tx.get('value', 0)),
            "input": tx.get('input', ''),
            "nonce": tx.get('nonce', 0)
        }
    
    def _is_upgrade_transaction(self, tx) -> bool:
        input_data = tx.get('input', '')
        upgrade_signatures = [
            'upgrade', 'propose', 'execute', 'governance'
        ]
        return any(sig in input_data.lower() for sig in upgrade_signatures)
    
    async def _process_upgrade_event(self, network_name: str, tx, block):
        db = SessionLocal()
        try:
            protocol = db.query(Protocol).filter(
                Protocol.address == tx.get('to', '').lower()
            ).first()
            
            if protocol:
                upgrade = ProtocolUpgrade(
                    protocol_id=protocol.id,
                    upgrade_type="implementation_upgrade",
                    title=f"Upgrade on {protocol.name}",
                    description=f"Upgrade transaction: {tx.hash.hex()}",
                    transaction_hash=tx.hash.hex(),
                    block_number=block.number,
                    status="executed",
                    execution_time=datetime.fromtimestamp(block.timestamp),
                    extra_metadata={
                        "gas_used": tx.get('gas', 0),
                        "gas_price": tx.get('gasPrice', 0)
                    }
                )
                
                db.add(upgrade)
                db.commit()
                logger.info(f"Detected upgrade for {protocol.name}")
                
        except Exception as e:
            logger.error(f"Error processing upgrade event: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _monitor_governance(self):
        logger.info("Starting governance monitoring...")
        
        while self.is_running:
            try:
                await self._monitor_snapshot_proposals()
                
                await self._monitor_tally_proposals()
                
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in governance monitoring: {e}")
                await asyncio.sleep(600)
    
    async def _monitor_snapshot_proposals(self):
        if not self.session:
            return
            
        try:
            url = "https://hub.snapshot.org/graphql"
            query = """
            {
                proposals(first: 10, orderBy: "created", orderDirection: desc) {
                    id
                    title
                    body
                    state
                    start
                    end
                    space {
                        id
                        name
                    }
                }
            }
            """
            
            async with self.session.post(url, json={"query": query}) as response:
                if response.status == 200:
                    data = await response.json()
                    await self._process_snapshot_proposals(data.get("data", {}).get("proposals", []))
                    
        except Exception as e:
            logger.error(f"Error monitoring Snapshot: {e}")
    
    async def _process_snapshot_proposals(self, proposals: List[Dict]):
        db = SessionLocal()
        try:
            for proposal in proposals:
                space_id = proposal.get("space", {}).get("id", "")
                if space_id in ["uniswap", "aave", "compound"]:
                    await self._create_governance_proposal(db, proposal, "snapshot")
                    
        except Exception as e:
            logger.error(f"Error processing Snapshot proposals: {e}")
        finally:
            db.close()
    
    async def _monitor_tally_proposals(self):
        pass
    
    async def _create_governance_proposal(self, db, proposal_data: Dict, source: str):
        try:
            protocol_name = proposal_data.get("space", {}).get("name", "")
            protocol = db.query(Protocol).filter(
                Protocol.name.ilike(f"%{protocol_name}%")
            ).first()
            
            if protocol:
                upgrade = ProtocolUpgrade(
                    protocol_id=protocol.id,
                    upgrade_type="governance_proposal",
                    title=proposal_data.get("title", ""),
                    description=proposal_data.get("body", ""),
                    proposal_id=proposal_data.get("id", ""),
                    status=proposal_data.get("state", "pending"),
                    start_time=datetime.fromtimestamp(proposal_data.get("start", 0)),
                    end_time=datetime.fromtimestamp(proposal_data.get("end", 0)),
                    extra_metadata={
                        "source": source,
                        "space_id": proposal_data.get("space", {}).get("id", "")
                    }
                )
                
                db.add(upgrade)
                db.commit()
                logger.info(f"Created governance proposal: {proposal_data.get('title', '')}")
                
        except Exception as e:
            logger.error(f"Error creating governance proposal: {e}")
            db.rollback()
    
    async def stop_monitoring(self):
        self.is_running = False
        if self.session:
            await self.session.close()
        logger.info("Stopped blockchain monitoring")
    
    async def get_latest_events(self, network_name: str, since_time: datetime = None) -> List[Dict]:
        db = SessionLocal()
        try:
            network = db.query(Network).filter(Network.name == network_name).first()
            if not network:
                return []
            query = db.query(BlockchainEvent).filter(
                BlockchainEvent.network_id == network.id
            )
            if since_time:
                query = query.filter(BlockchainEvent.timestamp >= since_time)
            events = query.order_by(BlockchainEvent.timestamp.desc()).all()
            return [
                {
                    "id": event.id,
                    "block_number": event.block_number,
                    "transaction_hash": event.transaction_hash,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp.isoformat()
                }
                for event in events
            ]
        finally:
            db.close()
    
    async def get_protocol_upgrades(self, protocol_name: str = None, limit: int = 20) -> List[Dict]:
        db = SessionLocal()
        try:
            query = db.query(ProtocolUpgrade).join(Protocol)
            if protocol_name:
                query = query.filter(Protocol.name.ilike(f"%{protocol_name}%"))
            upgrades = query.order_by(ProtocolUpgrade.created_at.desc()).limit(limit).all()
            return [
                {
                    "id": upgrade.id,
                    "protocol_name": upgrade.protocol.name,
                    "upgrade_type": upgrade.upgrade_type,
                    "title": upgrade.title,
                    "status": upgrade.status,
                    "created_at": upgrade.created_at.isoformat()
                }
                for upgrade in upgrades
            ]
        finally:
            db.close() 