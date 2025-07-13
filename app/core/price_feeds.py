"""
Real-time price feed service for cryptocurrency tokens.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger

# Token addresses for major protocols
TOKEN_ADDRESSES = {
    "aave": "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9",  # AAVE token
    "compound": "0xc00e94cb662c3520282e6f5717214004a7f26888",  # COMP token
    "uniswap": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",  # UNI token
    "curve": "0xd533a949740bb3306d119cc777fa900ba034cd52",  # CRV token
    "balancer": "0xba100000625a3754423978a60c9317c58a424e3d",  # BAL token
    "rari": "0xfca59cd816ab1ead66534d82bc21e7515ce441cf",  # RARI token
}

# CoinGecko API endpoints
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
PRICE_ENDPOINT = "/simple/price"
MARKET_DATA_ENDPOINT = "/coins/markets"


class PriceFeedService:
    """Service for fetching real-time cryptocurrency prices."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_duration = 30  # Cache prices for 30 seconds
        
    async def initialize(self):
        """Initialize the HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        logger.info("Price feed service initialized")
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_token_prices(self, token_ids: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get current prices for specified tokens."""
        if not token_ids:
            token_ids = list(TOKEN_ADDRESSES.keys())
        
        try:
            # Check cache first
            current_time = datetime.utcnow()
            cached_prices = {}
            tokens_to_fetch = []
            
            for token_id in token_ids:
                if (token_id in self.cache and 
                    current_time - self.cache[token_id]["timestamp"] < timedelta(seconds=self.cache_duration)):
                    cached_prices[token_id] = self.cache[token_id]
                else:
                    tokens_to_fetch.append(token_id)
            
            # Fetch new prices if needed
            if tokens_to_fetch:
                new_prices = await self._fetch_prices_from_api(tokens_to_fetch)
                for token_id, price_data in new_prices.items():
                    self.cache[token_id] = {
                        "price": price_data["price"],
                        "change_24h": price_data.get("change_24h", 0),
                        "volume_24h": price_data.get("volume_24h", 0),
                        "market_cap": price_data.get("market_cap", 0),
                        "timestamp": current_time
                    }
            
            # Combine cached and new prices
            result = {**cached_prices}
            for token_id in tokens_to_fetch:
                if token_id in self.cache:
                    result[token_id] = self.cache[token_id]
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching token prices: {e}")
            return {}
    
    async def _fetch_prices_from_api(self, token_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch prices from CoinGecko API."""
        if not self.session:
            await self.initialize()
        
        try:
            # Use simple price endpoint for basic price data
            params = {
                "ids": ",".join(token_ids),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true",
                "include_market_cap": "true"
            }
            
            url = f"{COINGECKO_BASE_URL}{PRICE_ENDPOINT}"
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    result = {}
                    for token_id in token_ids:
                        if token_id in data:
                            token_data = data[token_id]
                            result[token_id] = {
                                "price": token_data.get("usd", 0),
                                "change_24h": token_data.get("usd_24h_change", 0),
                                "volume_24h": token_data.get("usd_24h_vol", 0),
                                "market_cap": token_data.get("usd_market_cap", 0)
                            }
                    
                    return result
                else:
                    logger.warning(f"CoinGecko API returned status {response.status}")
                    return {}
                    
        except asyncio.TimeoutError:
            logger.warning("Timeout fetching prices from CoinGecko")
            return {}
        except Exception as e:
            logger.error(f"Error fetching from CoinGecko API: {e}")
            return {}
    
    async def get_protocol_prices(self) -> Dict[str, Dict[str, Any]]:
        """Get prices for all monitored protocols."""
        return await self.get_token_prices()
    
    async def get_price_history(self, token_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get historical price data for a token."""
        if not self.session:
            await self.initialize()
        
        try:
            url = f"{COINGECKO_BASE_URL}/coins/{token_id}/market_chart"
            params = {
                "vs_currency": "usd",
                "days": days
            }
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    history = []
                    for price_point in data.get("prices", []):
                        timestamp, price = price_point
                        history.append({
                            "timestamp": datetime.fromtimestamp(timestamp / 1000),
                            "price": price
                        })
                    
                    return history
                else:
                    logger.warning(f"CoinGecko API returned status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching price history for {token_id}: {e}")
            return []
    
    def get_price_change_color(self, change_24h: float) -> str:
        """Get color for price change display."""
        if change_24h > 0:
            return "#00FFB3"  # Green for positive
        elif change_24h < 0:
            return "#FF4C4C"  # Red for negative
        else:
            return "#9CA3AF"  # Gray for no change
    
    def format_price(self, price: float) -> str:
        """Format price for display."""
        if price >= 1:
            return f"${price:.2f}"
        elif price >= 0.01:
            return f"${price:.4f}"
        else:
            return f"${price:.6f}"


# Global instance
price_feed_service = PriceFeedService() 