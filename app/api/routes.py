from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger
import time
import tweepy
import os

from app.database.database import get_db
from app.database.models import Protocol, ProtocolUpgrade, RiskAssessment, VolatilityPrediction
from app.core.risk_models import RiskAssessmentEngine
from app.core.volatility import VolatilityPredictor
from app.core.blockchain import BlockchainMonitor
from app.core.price_feeds import price_feed_service
from textblob import TextBlob

router = APIRouter()


risk_engine = RiskAssessmentEngine()
volatility_predictor = VolatilityPredictor()
blockchain_monitor = BlockchainMonitor()
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "YOUR_BEARER_TOKEN")


@router.get("/dashboard/summary")
async def get_dashboard_summary():
    try:
      
        recent_upgrades = await blockchain_monitor.get_protocol_upgrades(limit=5)
        
      
        high_risk_upgrades = []
        for upgrade in recent_upgrades:
            try:
                risk = await risk_engine.assess_upgrade_risk(upgrade["id"])
                if risk["overall_risk_score"] > 70:
                    high_risk_upgrades.append(risk)
            except Exception as e:
                logger.warning(f"Error assessing risk for upgrade {upgrade['id']}: {e}")
        
        return {
            "recent_upgrades": recent_upgrades,
            "high_risk_upgrades": high_risk_upgrades,
            "total_protocols": len(recent_upgrades),
            "active_upgrades": len([u for u in recent_upgrades if u["status"] == "active"]),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/upgrades/active")
async def get_active_upgrades():
    try:
        upgrades = await blockchain_monitor.get_protocol_upgrades()
        active_upgrades = [u for u in upgrades if u["status"] in ["active", "pending"]]
        return {"active_upgrades": active_upgrades}
    except Exception as e:
        logger.error(f"Error getting active upgrades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/upgrades/{upgrade_id}/details")
async def get_upgrade_details(upgrade_id: int):
    try:
        db = next(get_db())
        upgrade = db.query(ProtocolUpgrade).filter(
            ProtocolUpgrade.id == upgrade_id
        ).first()
        
        if not upgrade:
            raise HTTPException(status_code=404, detail="Upgrade not found")
        
        risk_assessment = None
        try:
            risk_assessment = await risk_engine.assess_upgrade_risk(upgrade_id)
        except Exception as e:
            logger.warning(f"Error getting risk assessment: {e}")
        
        volatility_predictions = []
        try:
            predictions = await volatility_predictor.get_volatility_history(
                upgrade.protocol.address, days=7
            )
            volatility_predictions = predictions
        except Exception as e:
            logger.warning(f"Error getting volatility predictions: {e}")
        
        return {
            "upgrade": {
                "id": upgrade.id,
                "protocol_name": upgrade.protocol.name,
                "upgrade_type": upgrade.upgrade_type,
                "title": upgrade.title,
                "description": upgrade.description,
                "status": upgrade.status,
                "start_time": upgrade.start_time.isoformat() if upgrade.start_time else None,
                "end_time": upgrade.end_time.isoformat() if upgrade.end_time else None,
                "execution_time": upgrade.execution_time.isoformat() if upgrade.execution_time else None,
                "created_at": upgrade.created_at.isoformat()
            },
            "risk_assessment": risk_assessment,
            "volatility_predictions": volatility_predictions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting upgrade details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upgrades/{upgrade_id}/assess")
async def assess_upgrade(upgrade_id: int):
    try:
        risk_assessment = await risk_engine.assess_upgrade_risk(upgrade_id)
        
        db = next(get_db())
        upgrade = db.query(ProtocolUpgrade).filter(
            ProtocolUpgrade.id == upgrade_id
        ).first()
        
        volatility_prediction = None
        if upgrade:
            try:
                volatility_prediction = await volatility_predictor.predict_volatility(
                    upgrade.protocol.address, upgrade_id
                )
            except Exception as e:
                logger.warning(f"Error predicting volatility: {e}")
        
        return {
            "upgrade_id": upgrade_id,
            "risk_assessment": risk_assessment,
            "volatility_prediction": volatility_prediction,
            "assessment_time": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error assessing upgrade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/protocols/{protocol_id}/overview")
async def get_protocol_overview(protocol_id: int):
    try:
        db = next(get_db())
        protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
        
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")
        
        recent_upgrades = db.query(ProtocolUpgrade).filter(
            ProtocolUpgrade.protocol_id == protocol_id
        ).order_by(ProtocolUpgrade.created_at.desc()).limit(10).all()
        
        risk_history = await risk_engine.get_risk_history(protocol_id, days=30)
        
        volatility_history = await volatility_predictor.get_volatility_history(
            protocol.address, days=30
        )
        
        return {
            "protocol": {
                "id": protocol.id,
                "name": protocol.name,
                "address": protocol.address,
                "network": protocol.network.name,
                "protocol_type": protocol.protocol_type,
                "description": protocol.description
            },
            "recent_upgrades": [
                {
                    "id": upgrade.id,
                    "upgrade_type": upgrade.upgrade_type,
                    "title": upgrade.title,
                    "status": upgrade.status,
                    "created_at": upgrade.created_at.isoformat()
                }
                for upgrade in recent_upgrades
            ],
            "risk_history": risk_history,
            "volatility_history": volatility_history,
            "total_upgrades": len(recent_upgrades),
            "active_upgrades": len([u for u in recent_upgrades if u.status in ["active", "pending"]])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting protocol overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/risk-distribution")
async def get_risk_distribution():
    try:
        db = next(get_db())
        
        recent_assessments = db.query(RiskAssessment).filter(
            RiskAssessment.assessment_time >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        if not recent_assessments:
            return {"risk_distribution": [], "total_assessments": 0}
        
        risk_ranges = {
            "low": (0, 30),
            "medium": (30, 70),
            "high": (70, 100)
        }
        
        distribution = {}
        for risk_range, (min_val, max_val) in risk_ranges.items():
            count = len([a for a in recent_assessments 
                        if min_val <= a.overall_risk_score < max_val])
            distribution[risk_range] = count
        
        return {
            "risk_distribution": distribution,
            "total_assessments": len(recent_assessments),
            "average_risk": sum(a.overall_risk_score for a in recent_assessments) / len(recent_assessments)
        }
    except Exception as e:
        logger.error(f"Error getting risk distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/volatility-trends")
async def get_volatility_trends(token_address: str = None, limit: int = 200):
    try:
        limit = min(max(limit, 1), 1000)
        if token_address:
            history = await volatility_predictor.get_volatility_history(token_address, days=30)
            return {
                "token_address": token_address,
                "volatility_trends": history
            }
        else:
            db = next(get_db())
            recent_predictions = db.query(VolatilityPrediction).filter(
                VolatilityPrediction.prediction_time >= datetime.utcnow() - timedelta(days=7)
            ).order_by(VolatilityPrediction.prediction_time.desc()).limit(limit).all()
            
            return {
                "overall_trends": [
                    {
                        "token_address": pred.token_address,
                        "token_symbol": pred.token_symbol,
                        "predicted_volatility": pred.predicted_volatility,
                        "prediction_time": pred.prediction_time.isoformat()
                    }
                    for pred in recent_predictions
                ]
            }
    except Exception as e:
        logger.error(f"Error getting volatility trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/high-risk")
async def get_high_risk_alerts(threshold: int = 70):
    try:
        db = next(get_db())
        
        high_risk_assessments = db.query(RiskAssessment).filter(
            RiskAssessment.overall_risk_score >= threshold,
            RiskAssessment.assessment_time >= datetime.utcnow() - timedelta(days=7)
        ).order_by(RiskAssessment.overall_risk_score.desc()).all()
        
        alerts = []
        for assessment in high_risk_assessments:
            upgrade = db.query(ProtocolUpgrade).filter(
                ProtocolUpgrade.id == assessment.upgrade_id
            ).first()
            
            if upgrade:
                alerts.append({
                    "id": assessment.id,
                    "upgrade_id": upgrade.id,
                    "protocol_name": upgrade.protocol.name,
                    "upgrade_title": upgrade.title,
                    "risk_score": assessment.overall_risk_score,
                    "risk_factors": assessment.risk_factors,
                    "recommendations": assessment.recommendations,
                    "assessment_time": assessment.assessment_time.isoformat()
                })
        
        return {
            "high_risk_alerts": alerts,
            "total_alerts": len(alerts),
            "threshold": threshold
        }
    except Exception as e:
        logger.error(f"Error getting high-risk alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_upgrades(
    query: str = Query(..., description="Search query"),
    protocol_name: Optional[str] = None,
    upgrade_type: Optional[str] = None,
    status: Optional[str] = None
):
    try:
        db = next(get_db())
        
        search_query = db.query(ProtocolUpgrade).join(Protocol)
        
        if query:
            search_query = search_query.filter(
                (ProtocolUpgrade.title.contains(query)) |
                (ProtocolUpgrade.description.contains(query)) |
                (Protocol.name.contains(query))
            )
        
        if protocol_name:
            search_query = search_query.filter(Protocol.name.contains(protocol_name))
        
        if upgrade_type:
            search_query = search_query.filter(ProtocolUpgrade.upgrade_type == upgrade_type)
        
        if status:
            search_query = search_query.filter(ProtocolUpgrade.status == status)
        
        upgrades = search_query.order_by(ProtocolUpgrade.created_at.desc()).limit(20).all()
        
        return {
            "search_results": [
                {
                    "id": upgrade.id,
                    "protocol_name": upgrade.protocol.name,
                    "upgrade_type": upgrade.upgrade_type,
                    "title": upgrade.title,
                    "status": upgrade.status,
                    "created_at": upgrade.created_at.isoformat()
                }
                for upgrade in upgrades
            ],
            "total_results": len(upgrades),
            "query": query
        }
    except Exception as e:
        logger.error(f"Error searching upgrades: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 


@router.get("/dashboard/bulk-data")
async def get_dashboard_bulk_data():
    try:
        db = next(get_db())
        t0 = time.time()
        print("[TIMER] Start bulk-data endpoint")
        recent_upgrades = db.query(ProtocolUpgrade).join(Protocol).order_by(
            ProtocolUpgrade.created_at.desc()
        ).limit(10).all()
        print(f"[TIMER] After recent_upgrades query: {time.time() - t0:.2f}s")

        upgrade_ids = [upgrade.id for upgrade in recent_upgrades]
        t1 = time.time()
        risk_assessments = db.query(RiskAssessment).filter(
            RiskAssessment.upgrade_id.in_(upgrade_ids)
        ).all()
        print(f"[TIMER] After risk_assessments query: {time.time() - t1:.2f}s (total: {time.time() - t0:.2f}s)")

        t2 = time.time()
        volatility_predictions = db.query(VolatilityPrediction).filter(
            VolatilityPrediction.upgrade_id.in_(upgrade_ids)
        ).all()
        print(f"[TIMER] After volatility_predictions query: {time.time() - t2:.2f}s (total: {time.time() - t0:.2f}s)")

        t3 = time.time()
        risk_lookup = {ra.upgrade_id: ra for ra in risk_assessments}
        vol_lookup = {vp.upgrade_id: vp for vp in volatility_predictions}
        print(f"[TIMER] After creating lookups: {time.time() - t3:.2f}s (total: {time.time() - t0:.2f}s)")

        t4 = time.time()
        processed_upgrades = []
        risk_scores = []
        for upgrade in recent_upgrades:
            risk_data = risk_lookup.get(upgrade.id)
            vol_data = vol_lookup.get(upgrade.id)
            upgrade_data = {
                "id": upgrade.id,
                "protocol_name": upgrade.protocol.name,
                "title": upgrade.title,
                "description": upgrade.description,
                "status": upgrade.status,
                "upgrade_type": upgrade.upgrade_type,
                "created_at": upgrade.created_at.isoformat(),
                "risk_assessment": {
                    "overall_risk_score": risk_data.overall_risk_score if risk_data else 50,
                    "technical_risk": risk_data.technical_risk if risk_data else 50,
                    "governance_risk": risk_data.governance_risk if risk_data else 50,
                    "market_risk": risk_data.market_risk if risk_data else 50,
                    "liquidity_risk": risk_data.liquidity_risk if risk_data else 50
                } if risk_data else None,
                "volatility_prediction": {
                    "predicted_volatility": vol_data.predicted_volatility if vol_data else 0,
                    "confidence_interval_lower": vol_data.confidence_interval_lower if vol_data else 0,
                    "confidence_interval_upper": vol_data.confidence_interval_upper if vol_data else 0
                } if vol_data else None
            }
            processed_upgrades.append(upgrade_data)
            if risk_data:
                risk_scores.append(risk_data.overall_risk_score)
        print(f"[TIMER] After processing upgrades: {time.time() - t4:.2f}s (total: {time.time() - t0:.2f}s)")

        t5 = time.time()
        risk_distribution = {
            "low": len([r for r in risk_scores if r < 30]),
            "medium": len([r for r in risk_scores if 30 <= r < 70]),
            "high": len([r for r in risk_scores if r >= 70])
        }
        print(f"[TIMER] After risk_distribution: {time.time() - t5:.2f}s (total: {time.time() - t0:.2f}s)")

        t6 = time.time()
        recommendations = []
        for upgrade in processed_upgrades[:3]:
            risk_score = upgrade["risk_assessment"]["overall_risk_score"] if upgrade["risk_assessment"] else 50
            if risk_score < 30:
                recommendation = "Low risk - Consider accumulating"
            elif risk_score < 70:
                recommendation = "Medium risk - Monitor closely"
            else:
                recommendation = "High risk - Exercise caution"
            recommendations.append({
                "protocol": upgrade["protocol_name"],
                "recommendation": recommendation,
                "risk_level": "Low" if risk_score < 30 else "Medium" if risk_score < 70 else "High"
            })
        print(f"[TIMER] After recommendations: {time.time() - t6:.2f}s (total: {time.time() - t0:.2f}s)")

        print(f"[TIMER] END bulk-data endpoint: {time.time() - t0:.2f}s")
        return {
            "recent_upgrades": processed_upgrades,
            "risk_scores": risk_scores,
            "risk_distribution": risk_distribution,
            "trading_recommendations": recommendations,
            "total_protocols": len(processed_upgrades),
            "active_upgrades": len([u for u in processed_upgrades if u["status"] == "active"]),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting bulk dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close() 


@router.get("/prices/protocols")
async def get_protocol_prices():
    try:
        prices = await price_feed_service.get_protocol_prices()
        return {
            "prices": prices,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting protocol prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prices/{token_id}")
async def get_token_price(token_id: str):
    try:
        prices = await price_feed_service.get_token_prices([token_id])
        if token_id in prices:
            return {
                "token_id": token_id,
                "price_data": prices[token_id],
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Token {token_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting token price: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prices/{token_id}/history")
async def get_token_price_history(token_id: str, days: int = 7):
    try:
        history = await price_feed_service.get_price_history(token_id, days)
        return {
            "token_id": token_id,
            "history": history,
            "days": days,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting price history: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 


@router.post("/sentiment/analyze")
async def analyze_sentiment(request: Request):
    data = await request.json()
    text = data.get("text", "")
    if not text:
        return {"error": "No text provided"}
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    return {
        "text": text,
        "polarity": polarity,
        "subjectivity": subjectivity,
        "sentiment": (
            "positive" if polarity > 0.1 else
            "negative" if polarity < -0.1 else
            "neutral"
        )
    } 


@router.get("/sentiment/twitter")
async def twitter_sentiment(query: str, count: int = 10):
    if TWITTER_BEARER_TOKEN == "YOUR_BEARER_TOKEN":
        return {"error": "Please set your Twitter Bearer Token in the environment variable TWITTER_BEARER_TOKEN."}
    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
    tweets = client.search_recent_tweets(query=query, max_results=count)
    results = []
    if tweets.data:
        for tweet in tweets.data:
            blob = TextBlob(tweet.text)
            results.append({
                "text": tweet.text,
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity,
                "sentiment": (
                    "positive" if blob.sentiment.polarity > 0.1 else
                    "negative" if blob.sentiment.polarity < -0.1 else
                    "neutral"
                )
            })
    return {"results": results} 