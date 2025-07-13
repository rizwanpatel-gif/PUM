import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger
from datetime import datetime, timedelta

from app.config import settings
from app.database.database import init_db
from app.core.blockchain import BlockchainMonitor
from app.core.risk_models import RiskAssessmentEngine
from app.core.volatility import VolatilityPredictor
from app.core.price_feeds import price_feed_service
from app.api.routes import router as api_router
from app.api.websocket import WebSocketManager


blockchain_monitor = BlockchainMonitor()
risk_engine = RiskAssessmentEngine()
volatility_predictor = VolatilityPredictor()
websocket_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Protocol Upgrade Monitor...")
    
    init_db()
    logger.info("Database initialized")
    
    await blockchain_monitor.initialize()
    logger.info("Blockchain monitor initialized")
    
    await price_feed_service.initialize()
    logger.info("Price feed service initialized")
    
    asyncio.create_task(blockchain_monitor.start_monitoring())
    logger.info("Blockchain monitoring started")
    
    await risk_engine.train_risk_model()
    logger.info("Risk model training completed")
    
    yield
    
    logger.info("Shutting down Protocol Upgrade Monitor...")
    await blockchain_monitor.stop_monitoring()
    await price_feed_service.close()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Protocol Upgrade Monitor",
    description="High-performance protocol upgrade monitoring system",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Protocol Upgrade Monitor API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "services": {
            "blockchain_monitor": "running",
            "risk_engine": "ready",
            "volatility_predictor": "ready"
        }
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket_manager.disconnect(websocket)


@app.get("/api/v1/networks")
async def get_networks():
    from app.config import NETWORKS
    return {
        "networks": [
            {
                "name": name,
                "chain_id": config["chain_id"],
                "explorer": config["explorer"]
            }
            for name, config in NETWORKS.items()
        ]
    }


@app.get("/api/v1/protocols")
async def get_protocols():
    from app.config import PROTOCOL_ADDRESSES
    return {
        "protocols": [
            {
                "name": name,
                "address": address
            }
            for name, address in PROTOCOL_ADDRESSES.items()
        ]
    }


@app.get("/api/v1/upgrades")
async def get_upgrades(protocol_name: str = None, limit: int = 20):
    try:
        upgrades = await blockchain_monitor.get_protocol_upgrades(protocol_name)
        return {"upgrades": upgrades[:limit]}
    except Exception as e:
        logger.error(f"Error getting upgrades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/upgrades/{upgrade_id}/risk")
async def get_upgrade_risk(upgrade_id: int):
    try:
        risk_assessment = await risk_engine.assess_upgrade_risk(upgrade_id)
        return risk_assessment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error assessing risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/upgrades/{upgrade_id}/volatility")
async def get_upgrade_volatility(
    upgrade_id: int, 
    token_address: str,
    horizon_days: int = 30
):
    try:
        volatility = await volatility_predictor.predict_volatility(
            token_address, upgrade_id, horizon_days
        )
        return volatility
    except Exception as e:
        logger.error(f"Error predicting volatility: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/events/{network_name}")
async def get_network_events(network_name: str, since_hours: int = 24):
    import time
    t0 = time.time()
    print(f"[TIMER] Start events endpoint for {network_name}")
    try:
        since_time = datetime.utcnow() - timedelta(hours=since_hours)
        events = await blockchain_monitor.get_latest_events(network_name, since_time=since_time)
        print(f"[TIMER] After get_latest_events for {network_name}: {time.time() - t0:.2f}s")
        return {"events": events}
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risk/history/{protocol_id}")
async def get_risk_history(protocol_id: int, days: int = 30):
    try:
        history = await risk_engine.get_risk_history(protocol_id, days)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting risk history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/volatility/history/{token_address}")
async def get_volatility_history(token_address: str, days: int = 30):
    try:
        history = await volatility_predictor.get_volatility_history(token_address, days)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting volatility history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/volatility/evaluate/{token_address}")
async def evaluate_volatility_model(token_address: str, days: int = 30):
    try:
        performance = await volatility_predictor.evaluate_model_performance(token_address, days)
        return performance
    except Exception as e:
        logger.error(f"Error evaluating model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 