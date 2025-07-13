"""
Governance tracking and proposal monitoring.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger

from app.database.models import ProtocolUpgrade, Protocol
from app.database.database import SessionLocal
from app.config import settings


class GovernanceTracker:
    """Track governance proposals and voting patterns."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession()
        
    async def track_snapshot_proposals(self, space_id: str) -> List[Dict]:
        """Track Snapshot governance proposals."""
        if not self.session:
            await self.initialize()
            
        try:
            # Snapshot GraphQL query
            query = """
            {
                proposals(first: 20, where: {space: "%s"}, orderBy: "created", orderDirection: desc) {
                    id
                    title
                    body
                    choices
                    start
                    end
                    snapshot
                    state
                    author
                    scores
                    scores_total
                    votes
                    space {
                        id
                        name
                        symbol
                    }
                }
            }
            """ % space_id
            
            url = "https://hub.snapshot.org/graphql"
            async with self.session.post(url, json={"query": query}) as response:
                if response.status == 200:
                    data = await response.json()
                    proposals = data.get("data", {}).get("proposals", [])
                    
                    # Process and store proposals
                    processed_proposals = []
                    for proposal in proposals:
                        processed_proposal = await self._process_snapshot_proposal(proposal)
                        if processed_proposal:
                            processed_proposals.append(processed_proposal)
                    
                    return processed_proposals
                else:
                    logger.error(f"Error fetching Snapshot proposals: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error tracking Snapshot proposals: {e}")
            return []
    
    async def _process_snapshot_proposal(self, proposal_data: Dict) -> Optional[Dict]:
        """Process a Snapshot proposal."""
        try:
            db = SessionLocal()
            
            # Find or create protocol
            space_id = proposal_data.get("space", {}).get("id", "")
            protocol = db.query(Protocol).filter(
                Protocol.name.ilike(f"%{space_id}%")
            ).first()
            
            if not protocol:
                # Create new protocol entry
                protocol = Protocol(
                    name=proposal_data.get("space", {}).get("name", space_id),
                    address="",  # Snapshot doesn't have contract addresses
                    network_id=1,  # Default to Ethereum
                    protocol_type="Governance Protocol"
                )
                db.add(protocol)
                db.commit()
            
            # Check if proposal already exists
            existing_proposal = db.query(ProtocolUpgrade).filter(
                ProtocolUpgrade.proposal_id == proposal_data.get("id", "")
            ).first()
            
            if existing_proposal:
                # Update existing proposal
                existing_proposal.status = proposal_data.get("state", "pending")
                existing_proposal.updated_at = datetime.utcnow()
                db.commit()
                return None  # Already processed
            
            # Create new proposal
            proposal = ProtocolUpgrade(
                protocol_id=protocol.id,
                upgrade_type="governance_proposal",
                title=proposal_data.get("title", ""),
                description=proposal_data.get("body", ""),
                proposal_id=proposal_data.get("id", ""),
                status=proposal_data.get("state", "pending"),
                start_time=datetime.fromtimestamp(proposal_data.get("start", 0)),
                end_time=datetime.fromtimestamp(proposal_data.get("end", 0)),
                extra_metadata={
                    "source": "snapshot",
                    "space_id": space_id,
                    "choices": proposal_data.get("choices", []),
                    "scores": proposal_data.get("scores", []),
                    "scores_total": proposal_data.get("scores_total", 0),
                    "votes": proposal_data.get("votes", 0),
                    "author": proposal_data.get("author", "")
                }
            )
            
            db.add(proposal)
            db.commit()
            
            return {
                "id": proposal.id,
                "title": proposal.title,
                "protocol_name": protocol.name,
                "status": proposal.status,
                "start_time": proposal.start_time.isoformat(),
                "end_time": proposal.end_time.isoformat(),
                "votes": proposal_data.get("votes", 0),
                "scores_total": proposal_data.get("scores_total", 0)
            }
            
        except Exception as e:
            logger.error(f"Error processing Snapshot proposal: {e}")
            return None
        finally:
            db.close()
    
    async def track_tally_proposals(self, governance_address: str) -> List[Dict]:
        """Track Tally governance proposals."""
        if not self.session:
            await self.initialize()
            
        try:
            # Tally API endpoint
            url = f"https://api.tally.xyz/governance/{governance_address}/proposals"
            
            headers = {}
            if settings.tally_api_key:
                headers["Authorization"] = f"Bearer {settings.tally_api_key}"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    proposals = data.get("data", [])
                    
                    processed_proposals = []
                    for proposal in proposals:
                        processed_proposal = await self._process_tally_proposal(proposal)
                        if processed_proposal:
                            processed_proposals.append(processed_proposal)
                    
                    return processed_proposals
                else:
                    logger.error(f"Error fetching Tally proposals: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error tracking Tally proposals: {e}")
            return []
    
    async def _process_tally_proposal(self, proposal_data: Dict) -> Optional[Dict]:
        """Process a Tally proposal."""
        try:
            db = SessionLocal()
            
            # Find protocol by governance address
            governance_address = proposal_data.get("governance", {}).get("address", "")
            protocol = db.query(Protocol).filter(
                Protocol.address == governance_address
            ).first()
            
            if not protocol:
                logger.warning(f"Protocol not found for governance address: {governance_address}")
                return None
            
            # Check if proposal already exists
            existing_proposal = db.query(ProtocolUpgrade).filter(
                ProtocolUpgrade.proposal_id == proposal_data.get("id", "")
            ).first()
            
            if existing_proposal:
                # Update existing proposal
                existing_proposal.status = proposal_data.get("status", "pending")
                existing_proposal.updated_at = datetime.utcnow()
                db.commit()
                return None
            
            # Create new proposal
            proposal = ProtocolUpgrade(
                protocol_id=protocol.id,
                upgrade_type="governance_proposal",
                title=proposal_data.get("title", ""),
                description=proposal_data.get("description", ""),
                proposal_id=proposal_data.get("id", ""),
                status=proposal_data.get("status", "pending"),
                start_time=datetime.fromisoformat(proposal_data.get("startTime", "").replace("Z", "+00:00")),
                end_time=datetime.fromisoformat(proposal_data.get("endTime", "").replace("Z", "+00:00")),
                extra_metadata={
                    "source": "tally",
                    "governance_address": governance_address,
                    "proposer": proposal_data.get("proposer", ""),
                    "for_votes": proposal_data.get("forVotes", 0),
                    "against_votes": proposal_data.get("againstVotes", 0),
                    "abstain_votes": proposal_data.get("abstainVotes", 0)
                }
            )
            
            db.add(proposal)
            db.commit()
            
            return {
                "id": proposal.id,
                "title": proposal.title,
                "protocol_name": protocol.name,
                "status": proposal.status,
                "start_time": proposal.start_time.isoformat(),
                "end_time": proposal.end_time.isoformat(),
                "for_votes": proposal_data.get("forVotes", 0),
                "against_votes": proposal_data.get("againstVotes", 0)
            }
            
        except Exception as e:
            logger.error(f"Error processing Tally proposal: {e}")
            return None
        finally:
            db.close()
    
    async def analyze_voting_patterns(self, protocol_id: int, days: int = 90) -> Dict[str, Any]:
        """Analyze voting patterns for a protocol."""
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            proposals = db.query(ProtocolUpgrade).filter(
                ProtocolUpgrade.protocol_id == protocol_id,
                ProtocolUpgrade.upgrade_type == "governance_proposal",
                ProtocolUpgrade.created_at >= cutoff_date
            ).all()
            
            if not proposals:
                return {
                    "protocol_id": protocol_id,
                    "total_proposals": 0,
                    "success_rate": 0.0,
                    "average_participation": 0.0,
                    "voting_trends": {}
                }
            
            # Calculate metrics
            total_proposals = len(proposals)
            successful_proposals = len([p for p in proposals if p.status == "passed"])
            success_rate = successful_proposals / total_proposals
            
            # Calculate average participation
            total_votes = 0
            for proposal in proposals:
                extra_metadata = proposal.extra_metadata or {}
                if "votes" in extra_metadata:
                    total_votes += extra_metadata["votes"]
                elif "for_votes" in extra_metadata and "against_votes" in extra_metadata:
                    total_votes += extra_metadata["for_votes"] + extra_metadata["against_votes"]
            
            average_participation = total_votes / total_proposals if total_proposals > 0 else 0
            
            # Analyze voting trends
            voting_trends = {
                "recent_success_rate": 0.0,
                "participation_trend": "stable"
            }
            
            recent_proposals = [p for p in proposals if p.created_at >= datetime.utcnow() - timedelta(days=30)]
            if recent_proposals:
                recent_successful = len([p for p in recent_proposals if p.status == "passed"])
                voting_trends["recent_success_rate"] = recent_successful / len(recent_proposals)
            
            return {
                "protocol_id": protocol_id,
                "total_proposals": total_proposals,
                "success_rate": success_rate,
                "average_participation": average_participation,
                "voting_trends": voting_trends,
                "analysis_period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error analyzing voting patterns: {e}")
            raise
        finally:
            db.close()
    
    async def predict_proposal_outcome(self, proposal_id: str) -> Dict[str, Any]:
        """Predict the outcome of a governance proposal."""
        try:
            db = SessionLocal()
            
            proposal = db.query(ProtocolUpgrade).filter(
                ProtocolUpgrade.proposal_id == proposal_id
            ).first()
            
            if not proposal:
                raise ValueError(f"Proposal {proposal_id} not found")
            
            # Get historical voting patterns
            voting_patterns = await self.analyze_voting_patterns(proposal.protocol_id)
            
            # Get current proposal metrics
            extra_metadata = proposal.extra_metadata or {}
            current_votes = 0
            if "votes" in extra_metadata:
                current_votes = extra_metadata["votes"]
            elif "for_votes" in extra_metadata and "against_votes" in extra_metadata:
                current_votes = extra_metadata["for_votes"] + extra_metadata["against_votes"]
            
            # Simple prediction based on historical success rate and current participation
            historical_success_rate = voting_patterns["success_rate"]
            participation_ratio = current_votes / voting_patterns["average_participation"] if voting_patterns["average_participation"] > 0 else 1.0
            
            # Adjust prediction based on participation
            if participation_ratio > 1.2:
                success_probability = min(historical_success_rate * 1.1, 1.0)
            elif participation_ratio < 0.8:
                success_probability = max(historical_success_rate * 0.9, 0.0)
            else:
                success_probability = historical_success_rate
            
            return {
                "proposal_id": proposal_id,
                "predicted_outcome": "pass" if success_probability > 0.5 else "fail",
                "success_probability": success_probability,
                "confidence_level": "medium",
                "factors": {
                    "historical_success_rate": historical_success_rate,
                    "current_participation": current_votes,
                    "average_participation": voting_patterns["average_participation"],
                    "participation_ratio": participation_ratio
                }
            }
            
        except Exception as e:
            logger.error(f"Error predicting proposal outcome: {e}")
            raise
        finally:
            db.close()
    
    async def get_active_proposals(self) -> List[Dict]:
        """Get all active governance proposals."""
        db = SessionLocal()
        try:
            active_proposals = db.query(ProtocolUpgrade).filter(
                ProtocolUpgrade.upgrade_type == "governance_proposal",
                ProtocolUpgrade.status.in_(["active", "pending"])
            ).all()
            
            return [
                {
                    "id": proposal.id,
                    "proposal_id": proposal.proposal_id,
                    "protocol_name": proposal.protocol.name,
                    "title": proposal.title,
                    "status": proposal.status,
                    "start_time": proposal.start_time.isoformat() if proposal.start_time else None,
                    "end_time": proposal.end_time.isoformat() if proposal.end_time else None,
                    "extra_metadata": proposal.extra_metadata
                }
                for proposal in active_proposals
            ]
            
        except Exception as e:
            logger.error(f"Error getting active proposals: {e}")
            return []
        finally:
            db.close()
    
    async def start_monitoring(self):
        """Start monitoring governance platforms."""
        self.is_running = True
        logger.info("Starting governance monitoring...")
        
        while self.is_running:
            try:
                # Monitor Snapshot spaces
                snapshot_spaces = ["uniswap", "aave", "compound"]
                for space in snapshot_spaces:
                    proposals = await self.track_snapshot_proposals(space)
                    if proposals:
                        logger.info(f"Found {len(proposals)} new Snapshot proposals for {space}")
                
                # Monitor Tally governance contracts
                tally_contracts = [
                    "0x408ED6354d4973f66138C91495F2f2FCbd8724C3",  # Uniswap
                    "0xEC568fffba86c094cf06b22134B23074DFE2252c"   # Aave
                ]
                for contract in tally_contracts:
                    proposals = await self.track_tally_proposals(contract)
                    if proposals:
                        logger.info(f"Found {len(proposals)} new Tally proposals for {contract}")
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in governance monitoring: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def stop_monitoring(self):
        """Stop governance monitoring."""
        self.is_running = False
        if self.session:
            await self.session.close()
        logger.info("Stopped governance monitoring") 