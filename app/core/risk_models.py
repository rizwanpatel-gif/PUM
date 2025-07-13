"""
Risk assessment models for protocol upgrades.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from loguru import logger

from app.database.models import (
    Protocol, ProtocolUpgrade, RiskAssessment, MarketData, 
    SentimentData, BlockchainEvent
)
from app.database.database import SessionLocal
from app.config import RISK_CATEGORIES


class RiskAssessmentEngine:
    """Multi-factor risk assessment engine for protocol upgrades."""
    
    def __init__(self):
        self.risk_weights = {
            "technical": 0.25,
            "governance": 0.25,
            "market": 0.25,
            "liquidity": 0.25
        }
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        
    async def assess_upgrade_risk(self, upgrade_id: int) -> Dict[str, Any]:
        """Assess risk for a specific protocol upgrade."""
        db = SessionLocal()
        try:
            upgrade = db.query(ProtocolUpgrade).filter(
                ProtocolUpgrade.id == upgrade_id
            ).first()
            
            if not upgrade:
                raise ValueError(f"Upgrade {upgrade_id} not found")
            
            # Calculate individual risk components
            technical_risk = await self._calculate_technical_risk(db, upgrade)
            governance_risk = await self._calculate_governance_risk(db, upgrade)
            market_risk = await self._calculate_market_risk(db, upgrade)
            liquidity_risk = await self._calculate_liquidity_risk(db, upgrade)
            
            # Calculate overall risk score
            overall_risk = self._calculate_overall_risk(
                technical_risk, governance_risk, market_risk, liquidity_risk
            )
            
            # Generate risk factors and recommendations
            risk_factors = self._identify_risk_factors(
                technical_risk, governance_risk, market_risk, liquidity_risk
            )
            recommendations = self._generate_recommendations(risk_factors)
            
            # Create risk assessment record
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
            
            return {
                "upgrade_id": upgrade.id,
                "protocol_name": upgrade.protocol.name,
                "overall_risk_score": overall_risk,
                "risk_breakdown": {
                    "technical": technical_risk,
                    "governance": governance_risk,
                    "market": market_risk,
                    "liquidity": liquidity_risk
                },
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "assessment_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing upgrade risk: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _calculate_technical_risk(self, db, upgrade: ProtocolUpgrade) -> float:
        """Calculate technical risk based on smart contract complexity and security."""
        try:
            # Get recent blockchain events for the protocol
            recent_events = db.query(BlockchainEvent).join(Protocol, BlockchainEvent.to_address == Protocol.address).filter(
                Protocol.id == upgrade.protocol_id,
                BlockchainEvent.timestamp >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            # Calculate complexity metrics
            complexity_score = min(recent_events / 100, 1.0)  # Normalize to 0-1
            
            # Check for recent security events
            security_events = db.query(BlockchainEvent).join(Protocol, BlockchainEvent.to_address == Protocol.address).filter(
                Protocol.id == upgrade.protocol_id,
                BlockchainEvent.event_type.in_(["Emergency_Pause", "Security_Patch"]),
                BlockchainEvent.timestamp >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            security_score = min(security_events * 0.2, 1.0)
            
            # Calculate technical risk (0-100 scale)
            technical_risk = (complexity_score * 0.6 + security_score * 0.4) * 100
            
            return min(technical_risk, 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating technical risk: {e}")
            return 50.0  # Default moderate risk
    
    async def _calculate_governance_risk(self, db, upgrade: ProtocolUpgrade) -> float:
        """Calculate governance risk based on voting patterns and proposal history."""
        try:
            # Get governance history for the protocol
            governance_proposals = db.query(ProtocolUpgrade).filter(
                ProtocolUpgrade.protocol_id == upgrade.protocol_id,
                ProtocolUpgrade.upgrade_type == "governance_proposal",
                ProtocolUpgrade.created_at >= datetime.utcnow() - timedelta(days=90)
            ).all()
            
            if not governance_proposals:
                return 75.0  # High risk if no governance history
            
            # Calculate success rate
            successful_proposals = sum(1 for p in governance_proposals if p.status == "passed")
            success_rate = successful_proposals / len(governance_proposals)
            
            # Calculate proposal frequency
            proposal_frequency = len(governance_proposals) / 3  # per month
            
            # Calculate governance risk
            governance_risk = (
                (1 - success_rate) * 0.5 +  # Lower success rate = higher risk
                min(proposal_frequency / 5, 1.0) * 0.3 +  # High frequency = higher risk
                (0.2 if upgrade.status == "pending" else 0.0)  # Pending proposals = higher risk
            ) * 100
            
            return min(governance_risk, 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating governance risk: {e}")
            return 50.0
    
    async def _calculate_market_risk(self, db, upgrade: ProtocolUpgrade) -> float:
        """Calculate market risk based on price volatility and market conditions."""
        try:
            # Get market data for the protocol token
            market_data = db.query(MarketData).filter(
                MarketData.token_address == upgrade.protocol.address,
                MarketData.timestamp >= datetime.utcnow() - timedelta(days=30)
            ).order_by(MarketData.timestamp.desc()).limit(30).all()
            
            if not market_data:
                return 60.0  # Moderate risk if no market data
            
            # Calculate price volatility
            prices = [data.price for data in market_data]
            if len(prices) > 1:
                returns = np.diff(np.log(prices))
                volatility = np.std(returns) * np.sqrt(365)  # Annualized volatility
                volatility_score = min(volatility * 100, 1.0)
            else:
                volatility_score = 0.5
            
            # Calculate price trend
            if len(prices) > 7:
                recent_avg = np.mean(prices[:7])
                older_avg = np.mean(prices[-7:])
                trend_score = 1.0 if recent_avg < older_avg else 0.0
            else:
                trend_score = 0.5
            
            # Calculate market risk
            market_risk = (volatility_score * 0.7 + trend_score * 0.3) * 100
            
            return min(market_risk, 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating market risk: {e}")
            return 50.0
    
    async def _calculate_liquidity_risk(self, db, upgrade: ProtocolUpgrade) -> float:
        """Calculate liquidity risk based on TVL and trading volume."""
        try:
            # Get recent market data
            market_data = db.query(MarketData).filter(
                MarketData.token_address == upgrade.protocol.address,
                MarketData.timestamp >= datetime.utcnow() - timedelta(days=7)
            ).order_by(MarketData.timestamp.desc()).limit(7).all()
            
            if not market_data:
                return 70.0  # High risk if no liquidity data
            
            # Calculate volume volatility
            volumes = [data.volume_24h for data in market_data if data.volume_24h]
            if len(volumes) > 1:
                volume_cv = np.std(volumes) / np.mean(volumes)  # Coefficient of variation
                volume_risk = min(volume_cv, 1.0)
            else:
                volume_risk = 0.5
            
            # Calculate average volume
            avg_volume = np.mean(volumes) if volumes else 0
            volume_score = 1.0 if avg_volume < 1000000 else 0.0  # Low volume = high risk
            
            # Calculate liquidity risk
            liquidity_risk = (volume_risk * 0.6 + volume_score * 0.4) * 100
            
            return min(liquidity_risk, 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating liquidity risk: {e}")
            return 50.0
    
    def _calculate_overall_risk(
        self, technical: float, governance: float, 
        market: float, liquidity: float
    ) -> float:
        """Calculate overall risk score using weighted average."""
        overall_risk = (
            technical * self.risk_weights["technical"] +
            governance * self.risk_weights["governance"] +
            market * self.risk_weights["market"] +
            liquidity * self.risk_weights["liquidity"]
        )
        
        return min(overall_risk, 100.0)
    
    def _identify_risk_factors(
        self, technical: float, governance: float, 
        market: float, liquidity: float
    ) -> Dict[str, Any]:
        """Identify specific risk factors contributing to the risk score."""
        risk_factors = {}
        
        if technical > 70:
            risk_factors["technical"] = {
                "level": "high",
                "description": "High smart contract complexity or recent security events",
                "score": technical
            }
        elif technical > 40:
            risk_factors["technical"] = {
                "level": "medium",
                "description": "Moderate technical complexity",
                "score": technical
            }
        
        if governance > 70:
            risk_factors["governance"] = {
                "level": "high",
                "description": "Low governance participation or proposal success rate",
                "score": governance
            }
        elif governance > 40:
            risk_factors["governance"] = {
                "level": "medium",
                "description": "Moderate governance risk",
                "score": governance
            }
        
        if market > 70:
            risk_factors["market"] = {
                "level": "high",
                "description": "High price volatility or negative price trend",
                "score": market
            }
        elif market > 40:
            risk_factors["market"] = {
                "level": "medium",
                "description": "Moderate market volatility",
                "score": market
            }
        
        if liquidity > 70:
            risk_factors["liquidity"] = {
                "level": "high",
                "description": "Low trading volume or high volume volatility",
                "score": liquidity
            }
        elif liquidity > 40:
            risk_factors["liquidity"] = {
                "level": "medium",
                "description": "Moderate liquidity risk",
                "score": liquidity
            }
        
        return risk_factors
    
    def _generate_recommendations(self, risk_factors: Dict[str, Any]) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        if "technical" in risk_factors:
            if risk_factors["technical"]["level"] == "high":
                recommendations.append("Conduct thorough smart contract audit before upgrade")
                recommendations.append("Implement emergency pause functionality")
            else:
                recommendations.append("Monitor smart contract events closely")
        
        if "governance" in risk_factors:
            if risk_factors["governance"]["level"] == "high":
                recommendations.append("Increase governance participation incentives")
                recommendations.append("Extend proposal voting period")
            else:
                recommendations.append("Monitor governance proposal outcomes")
        
        if "market" in risk_factors:
            if risk_factors["market"]["level"] == "high":
                recommendations.append("Consider hedging strategies for price volatility")
                recommendations.append("Monitor market sentiment closely")
            else:
                recommendations.append("Track price movements during upgrade")
        
        if "liquidity" in risk_factors:
            if risk_factors["liquidity"]["level"] == "high":
                recommendations.append("Ensure sufficient liquidity before upgrade")
                recommendations.append("Monitor trading volume patterns")
            else:
                recommendations.append("Watch for unusual trading activity")
        
        if not recommendations:
            recommendations.append("Continue monitoring all risk factors")
        
        return recommendations
    
    async def get_risk_history(self, protocol_id: int, days: int = 30) -> List[Dict]:
        """Get risk assessment history for a protocol."""
        db = SessionLocal()
        try:
            assessments = db.query(RiskAssessment).filter(
                RiskAssessment.protocol_id == protocol_id,
                RiskAssessment.assessment_time >= datetime.utcnow() - timedelta(days=days)
            ).order_by(RiskAssessment.assessment_time.desc()).all()
            
            return [
                {
                    "id": assessment.id,
                    "upgrade_id": assessment.upgrade_id,
                    "overall_risk": assessment.overall_risk_score,
                    "technical_risk": assessment.technical_risk,
                    "governance_risk": assessment.governance_risk,
                    "market_risk": assessment.market_risk,
                    "liquidity_risk": assessment.liquidity_risk,
                    "assessment_time": assessment.assessment_time.isoformat()
                }
                for assessment in assessments
            ]
        finally:
            db.close()
    
    async def train_risk_model(self):
        """Train the machine learning risk model."""
        db = SessionLocal()
        try:
            # Get historical risk assessments
            assessments = db.query(RiskAssessment).all()
            
            if len(assessments) < 50:
                logger.warning("Insufficient data to train risk model")
                return
            
            # Prepare features
            features = []
            targets = []
            
            for assessment in assessments:
                feature_vector = [
                    assessment.technical_risk,
                    assessment.governance_risk,
                    assessment.market_risk,
                    assessment.liquidity_risk
                ]
                features.append(feature_vector)
                targets.append(assessment.overall_risk_score)
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train model
            self.model.fit(features_scaled, targets)
            self.is_trained = True
            
            logger.info("Risk model trained successfully")
            
        except Exception as e:
            logger.error(f"Error training risk model: {e}")
        finally:
            db.close()
    
    async def predict_risk(self, technical: float, governance: float, 
                          market: float, liquidity: float) -> float:
        """Predict risk score using trained model."""
        if not self.is_trained:
            return self._calculate_overall_risk(technical, governance, market, liquidity)
        
        try:
            features = np.array([[technical, governance, market, liquidity]])
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled)[0]
            return min(max(prediction, 0), 100)
        except Exception as e:
            logger.error(f"Error predicting risk: {e}")
            return self._calculate_overall_risk(technical, governance, market, liquidity) 