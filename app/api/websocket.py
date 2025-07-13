"""
WebSocket manager for real-time updates.
"""

import json
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger


class WebSocketManager:
    """Manage WebSocket connections and real-time updates."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[WebSocket, List[str]] = {}
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.subscriptions[websocket] = []
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message(websocket, {
            "type": "connection",
            "message": "Connected to Protocol Upgrade Monitor",
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            await self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected WebSocket clients."""
        if not self.active_connections:
            return
        
        disconnected = set()
        for websocket in self.active_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected websockets
        for websocket in disconnected:
            await self.disconnect(websocket)
    
    async def broadcast_to_subscribers(self, message: dict, subscription_type: str):
        """Broadcast a message to subscribers of a specific type."""
        if not self.active_connections:
            return
        
        disconnected = set()
        for websocket in self.active_connections:
            if (websocket in self.subscriptions and 
                subscription_type in self.subscriptions[websocket]):
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to subscribers: {e}")
                    disconnected.add(websocket)
        
        # Remove disconnected websockets
        for websocket in disconnected:
            await self.disconnect(websocket)
    
    async def handle_message(self, websocket: WebSocket, data: str):
        """Handle incoming WebSocket messages."""
        try:
            message = json.loads(data)
            message_type = message.get("type")
            
            if message_type == "subscribe":
                await self._handle_subscribe(websocket, message)
            elif message_type == "unsubscribe":
                await self._handle_unsubscribe(websocket, message)
            elif message_type == "ping":
                await self._handle_ping(websocket)
            else:
                await self.send_personal_message(websocket, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
                
        except json.JSONDecodeError:
            await self.send_personal_message(websocket, {
                "type": "error",
                "message": "Invalid JSON format"
            })
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send_personal_message(websocket, {
                "type": "error",
                "message": "Internal server error"
            })
    
    async def _handle_subscribe(self, websocket: WebSocket, message: dict):
        """Handle subscription requests."""
        subscription_type = message.get("subscription_type")
        
        if not subscription_type:
            await self.send_personal_message(websocket, {
                "type": "error",
                "message": "Missing subscription_type"
            })
            return
        
        if websocket not in self.subscriptions:
            self.subscriptions[websocket] = []
        
        if subscription_type not in self.subscriptions[websocket]:
            self.subscriptions[websocket].append(subscription_type)
        
        await self.send_personal_message(websocket, {
            "type": "subscription_confirmed",
            "subscription_type": subscription_type,
            "message": f"Subscribed to {subscription_type} updates"
        })
        
        logger.info(f"Client subscribed to {subscription_type}")
    
    async def _handle_unsubscribe(self, websocket: WebSocket, message: dict):
        """Handle unsubscription requests."""
        subscription_type = message.get("subscription_type")
        
        if not subscription_type:
            await self.send_personal_message(websocket, {
                "type": "error",
                "message": "Missing subscription_type"
            })
            return
        
        if (websocket in self.subscriptions and 
            subscription_type in self.subscriptions[websocket]):
            self.subscriptions[websocket].remove(subscription_type)
        
        await self.send_personal_message(websocket, {
            "type": "unsubscription_confirmed",
            "subscription_type": subscription_type,
            "message": f"Unsubscribed from {subscription_type} updates"
        })
        
        logger.info(f"Client unsubscribed from {subscription_type}")
    
    async def _handle_ping(self, websocket: WebSocket):
        """Handle ping messages."""
        await self.send_personal_message(websocket, {
            "type": "pong",
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def send_upgrade_notification(self, upgrade_data: dict):
        """Send upgrade notification to subscribers."""
        message = {
            "type": "upgrade_notification",
            "data": upgrade_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast_to_subscribers(message, "upgrades")
    
    async def send_risk_alert(self, risk_data: dict):
        """Send risk alert to subscribers."""
        message = {
            "type": "risk_alert",
            "data": risk_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast_to_subscribers(message, "risk_alerts")
    
    async def send_volatility_update(self, volatility_data: dict):
        """Send volatility update to subscribers."""
        message = {
            "type": "volatility_update",
            "data": volatility_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast_to_subscribers(message, "volatility")
    
    async def send_network_event(self, event_data: dict):
        """Send network event to subscribers."""
        message = {
            "type": "network_event",
            "data": event_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast_to_subscribers(message, "network_events")
    
    async def send_system_status(self, status_data: dict):
        """Send system status update to subscribers."""
        message = {
            "type": "system_status",
            "data": status_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast_to_subscribers(message, "system_status")
    
    def get_connection_stats(self) -> dict:
        """Get WebSocket connection statistics."""
        total_connections = len(self.active_connections)
        subscription_counts = {}
        
        for subscriptions in self.subscriptions.values():
            for subscription_type in subscriptions:
                subscription_counts[subscription_type] = subscription_counts.get(subscription_type, 0) + 1
        
        return {
            "total_connections": total_connections,
            "subscription_counts": subscription_counts,
            "active_subscriptions": list(set().union(*self.subscriptions.values()))
        } 