#!/usr/bin/env python3

import asyncio
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.main import app
from app.database.database import init_db
from app.core.blockchain import BlockchainMonitor
from app.core.risk_models import RiskAssessmentEngine
from app.core.volatility import VolatilityPredictor
from app.core.liquidity import LiquidityPredictor
from app.core.sentiment import SentimentAnalyzer
from app.core.governance import GovernanceTracker
from app.ui.dashboard import app as dashboard_app
from loguru import logger


async def initialize_system():
    logger.info("🚀 Initializing Protocol Upgrade Monitor...")
    
    try:
        logger.info("📊 Initializing database...")
        init_db()
        logger.info("✅ Database initialized successfully")
        
        logger.info("🔗 Initializing blockchain monitor...")
        blockchain_monitor = BlockchainMonitor()
        await blockchain_monitor.initialize()
        logger.info("✅ Blockchain monitor initialized")
        
        logger.info("⚠️  Initializing risk assessment engine...")
        risk_engine = RiskAssessmentEngine()
        await risk_engine.train_risk_model()
        logger.info("✅ Risk engine initialized and trained")
        
        logger.info("📈 Initializing prediction models...")
        volatility_predictor = VolatilityPredictor()
        liquidity_predictor = LiquidityPredictor()
        sentiment_analyzer = SentimentAnalyzer()
        governance_tracker = GovernanceTracker()
        
        await governance_tracker.initialize()
        logger.info("✅ All components initialized successfully")
        
        return {
            "blockchain_monitor": blockchain_monitor,
            "risk_engine": risk_engine,
            "volatility_predictor": volatility_predictor,
            "liquidity_predictor": liquidity_predictor,
            "sentiment_analyzer": sentiment_analyzer,
            "governance_tracker": governance_tracker
        }
        
    except Exception as e:
        logger.error(f"❌ Error initializing system: {e}")
        raise


def print_startup_info():
    print("\n" + "="*60)
    print("🔍 PROTOCOL UPGRADE MONITOR (PUM)")
    print("="*60)
    print("📊 High-performance protocol upgrade monitoring system")
    print("🎯 Real-time risk assessment and market intelligence")
    print("="*60)
    print("\n🌐 Services:")
    print("   • FastAPI Backend: http://localhost:8000")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Dashboard: http://localhost:8050")
    print("   • WebSocket: ws://localhost:8000/ws")
    print("\n📁 Project Structure:")
    print("   • Core Logic: app/core/")
    print("   • API Endpoints: app/api/")
    print("   • Database Models: app/database/")
    print("   • Dashboard UI: app/ui/")
    print("   • Tests: tests/")
    print("   • Documentation: docs/")
    print("\n🔧 Configuration:")
    print("   • Environment: Copy env_example.txt to .env")
    print("   • API Keys: Configure in .env file")
    print("   • Database: SQLite (dev) / PostgreSQL (prod)")
    print("="*60 + "\n")


async def start_background_tasks(components):
    logger.info("🔄 Starting background tasks...")
    
    blockchain_task = asyncio.create_task(
        components["blockchain_monitor"].start_monitoring()
    )
    
    governance_task = asyncio.create_task(
        components["governance_tracker"].start_monitoring()
    )
    
    logger.info("✅ Background tasks started")
    
    return [blockchain_task, governance_task]


def main():
    print_startup_info()
    
    try:
        components = asyncio.run(initialize_system())
        
        background_tasks = asyncio.run(start_background_tasks(components))
        
        logger.info("🎉 Protocol Upgrade Monitor is ready!")
        logger.info("📊 Access the dashboard at: http://localhost:8050")
        logger.info("🔗 API documentation at: http://localhost:8000/docs")
        
        try:
            asyncio.run(asyncio.gather(*background_tasks))
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down Protocol Upgrade Monitor...")
            
            for task in background_tasks:
                task.cancel()
            
            asyncio.run(components["blockchain_monitor"].stop_monitoring())
            asyncio.run(components["governance_tracker"].stop_monitoring())
            
            logger.info("✅ Shutdown complete")
            
    except Exception as e:
        logger.error(f"❌ Failed to start system: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 