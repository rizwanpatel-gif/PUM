from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .database import Base


class Network(Base):
    __tablename__ = "networks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    chain_id = Column(Integer, unique=True)
    rpc_url = Column(String)
    explorer_url = Column(String)
    api_key = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    protocols = relationship("Protocol", back_populates="network")
    events = relationship("BlockchainEvent", back_populates="network")


class Protocol(Base):
    __tablename__ = "protocols"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String, unique=True, index=True)
    network_id = Column(Integer, ForeignKey("networks.id"))
    protocol_type = Column(String)
    description = Column(Text)
    website = Column(String)
    github = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    network = relationship("Network", back_populates="protocols")
    upgrades = relationship("ProtocolUpgrade", back_populates="protocol")
    risk_assessments = relationship("RiskAssessment", back_populates="protocol")


class ProtocolUpgrade(Base):
    __tablename__ = "protocol_upgrades"
    
    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), index=True)
    upgrade_type = Column(String)
    title = Column(String)
    description = Column(Text)
    proposal_id = Column(String, index=True)
    status = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    execution_time = Column(DateTime)
    block_number = Column(Integer)
    transaction_hash = Column(String)
    extra_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    protocol = relationship("Protocol", back_populates="upgrades")
    risk_assessments = relationship("RiskAssessment", back_populates="upgrade")
    volatility_predictions = relationship("VolatilityPrediction", back_populates="upgrade")
    liquidity_predictions = relationship("LiquidityPrediction", back_populates="upgrade")


class BlockchainEvent(Base):
    __tablename__ = "blockchain_events"
    
    id = Column(Integer, primary_key=True, index=True)
    network_id = Column(Integer, ForeignKey("networks.id"))
    block_number = Column(Integer, index=True)
    transaction_hash = Column(String, index=True)
    from_address = Column(String, index=True)
    to_address = Column(String, index=True)
    event_type = Column(String)
    event_data = Column(JSON)
    gas_used = Column(Integer)
    gas_price = Column(Integer)
    timestamp = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    network = relationship("Network", back_populates="events")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"))
    upgrade_id = Column(Integer, ForeignKey("protocol_upgrades.id"), index=True)
    overall_risk_score = Column(Float)
    technical_risk = Column(Float)
    governance_risk = Column(Float)
    market_risk = Column(Float)
    liquidity_risk = Column(Float)
    risk_factors = Column(JSON)
    recommendations = Column(JSON)
    assessment_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    protocol = relationship("Protocol", back_populates="risk_assessments")
    upgrade = relationship("ProtocolUpgrade", back_populates="risk_assessments")


class VolatilityPrediction(Base):
    __tablename__ = "volatility_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    upgrade_id = Column(Integer, ForeignKey("protocol_upgrades.id"), index=True)
    token_address = Column(String, index=True)
    token_symbol = Column(String)
    prediction_horizon = Column(Integer)
    predicted_volatility = Column(Float)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    model_used = Column(String)
    model_parameters = Column(JSON)
    prediction_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    upgrade = relationship("ProtocolUpgrade", back_populates="volatility_predictions")


class LiquidityPrediction(Base):
    __tablename__ = "liquidity_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    upgrade_id = Column(Integer, ForeignKey("protocol_upgrades.id"))
    protocol_address = Column(String, index=True)
    prediction_horizon = Column(Integer)
    predicted_tvl_change = Column(Float)
    predicted_volume_change = Column(Float)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    model_used = Column(String)
    model_parameters = Column(JSON)
    prediction_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    upgrade = relationship("ProtocolUpgrade", back_populates="liquidity_predictions")


class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    token_address = Column(String, index=True)
    token_symbol = Column(String)
    price = Column(Float)
    volume_24h = Column(Float)
    market_cap = Column(Float)
    price_change_24h = Column(Float)
    price_change_7d = Column(Float)
    data_source = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class SentimentData(Base):
    __tablename__ = "sentiment_data"
    
    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"))
    source = Column(String)
    sentiment_score = Column(Float)
    sentiment_label = Column(String)
    text_content = Column(Text)
    user_count = Column(Integer)
    engagement_metrics = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExecutionGuidance(Base):
    __tablename__ = "execution_guidance"
    
    id = Column(Integer, primary_key=True, index=True)
    upgrade_id = Column(Integer, ForeignKey("protocol_upgrades.id"))
    action_type = Column(String)
    token_address = Column(String, index=True)
    token_symbol = Column(String)
    recommended_quantity = Column(Float)
    entry_price_range = Column(JSON)
    exit_price_range = Column(JSON)
    timing_recommendation = Column(String)
    confidence_level = Column(Float)
    risk_reward_ratio = Column(Float)
    reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String)
    component = Column(String)
    message = Column(Text)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow) 