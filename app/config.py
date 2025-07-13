import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    
    database_url: str = Field(default="sqlite:///./pum.db")
    
    etherscan_api_key: Optional[str] = Field(default=None)
    polygonscan_api_key: Optional[str] = Field(default=None)
    arbiscan_api_key: Optional[str] = Field(default=None)
    
    twitter_api_key: Optional[str] = Field(default=None)
    twitter_api_secret: Optional[str] = Field(default=None)
    twitter_access_token: Optional[str] = Field(default=None)
    twitter_access_token_secret: Optional[str] = Field(default=None)
    
    coingecko_api_key: Optional[str] = Field(default=None)
    coinmarketcap_api_key: Optional[str] = Field(default=None)
    
    defi_llama_api_key: Optional[str] = Field(default=None)
    defi_pulse_api_key: Optional[str] = Field(default=None)
    
    snapshot_api_key: Optional[str] = Field(default=None)
    tally_api_key: Optional[str] = Field(default=None)
    
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    dashboard_port: int = Field(default=8050)
    
    model_update_interval: int = Field(default=3600)
    risk_threshold: int = Field(default=75)
    volatility_window: int = Field(default=30)
    liquidity_window: int = Field(default=7)
    
    cache_ttl: int = Field(default=300)
    redis_url: Optional[str] = Field(default=None)
    
    secret_key: str = Field(default="your_secret_key_here_change_in_production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    ethereum_rpc_url: str = Field(default="https://mainnet.infura.io/v3/your_project_id")
    polygon_rpc_url: str = Field(default="https://polygon-rpc.com")
    arbitrum_rpc_url: str = Field(default="https://arb1.arbitrum.io/rpc")


settings = Settings()


NETWORKS = {
    "ethereum": {
        "name": "Ethereum",
        "chain_id": 1,
        "rpc_url": settings.ethereum_rpc_url,
        "explorer": "https://etherscan.io",
        "api_key": settings.etherscan_api_key,
        "api_base": "https://api.etherscan.io/api"
    },
    "polygon": {
        "name": "Polygon",
        "chain_id": 137,
        "rpc_url": settings.polygon_rpc_url,
        "explorer": "https://polygonscan.com",
        "api_key": settings.polygonscan_api_key,
        "api_base": "https://api.polygonscan.com/api"
    },
    "arbitrum": {
        "name": "Arbitrum",
        "chain_id": 42161,
        "rpc_url": settings.arbitrum_rpc_url,
        "explorer": "https://arbiscan.io",
        "api_key": settings.arbiscan_api_key,
        "api_base": "https://api.arbiscan.io/api"
    }
}

PROTOCOL_ADDRESSES = {
    "uniswap_v3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
    "aave_v3": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "compound_v3": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
    "curve_finance": "0xD533a949740bb3306d119CC777fa900bA034cd52",
    "balancer": "0xba100000625a3754423978a60c9317c58a424e3D"
}

UPGRADE_TYPES = [
    "governance_proposal",
    "implementation_upgrade",
    "parameter_change",
    "emergency_pause",
    "fee_adjustment",
    "security_patch"
]

RISK_CATEGORIES = {
    "technical": "Smart contract complexity and security",
    "governance": "Voter participation and proposal history",
    "market": "Correlation with broader market movements",
    "liquidity": "TVL concentration and DEX volume"
}

if __name__ == "__main__":
    print("ETHERSCAN_API_KEY:", settings.etherscan_api_key) 