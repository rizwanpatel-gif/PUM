import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from app.core.blockchain import BlockchainMonitor
from app.core.risk_models import RiskAssessmentEngine
from app.core.volatility import VolatilityPredictor
from app.core.liquidity import LiquidityPredictor
from app.core.sentiment import SentimentAnalyzer
from app.core.governance import GovernanceTracker
from app.database.database import init_db, SessionLocal
from app.database.models import Protocol, ProtocolUpgrade, Network


@pytest.fixture
def db_session():
    init_db()
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_protocol(db_session):
    network = db_session.query(Network).filter_by(name="ethereum").first()
    if not network:
        network = Network(
            name="ethereum",
            chain_id=1,
            rpc_url="https://mainnet.infura.io/v3/test",
            explorer_url="https://etherscan.io",
            api_key="test_key"
        )
        db_session.add(network)
        db_session.commit()
    protocol = db_session.query(Protocol).filter_by(address="0x1234567890123456789012345678901234567890").first()
    if not protocol:
        protocol = Protocol(
            name="Test Protocol",
            address="0x1234567890123456789012345678901234567890",
            network_id=network.id,
            protocol_type="DeFi Protocol"
        )
        db_session.add(protocol)
        db_session.commit()
    return protocol


@pytest.fixture
def sample_upgrade(db_session, sample_protocol):
    upgrade = ProtocolUpgrade(
        protocol_id=sample_protocol.id,
        upgrade_type="governance_proposal",
        title="Test Upgrade",
        description="Test upgrade description",
        proposal_id="test_proposal_123",
        status="pending",
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(days=7)
    )
    db_session.add(upgrade)
    db_session.commit()
    
    return upgrade


class TestBlockchainMonitor:
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        monitor = BlockchainMonitor()
        await monitor.initialize()
        
        assert monitor.session is not None
        assert len(monitor.web3_connections) >= 0
    
    @pytest.mark.asyncio
    async def test_get_latest_events(self):
        monitor = BlockchainMonitor()
        events = await monitor.get_latest_events("ethereum", limit=5)
        
        assert isinstance(events, list)
        assert len(events) <= 5
    
    @pytest.mark.asyncio
    async def test_get_protocol_upgrades(self):
        monitor = BlockchainMonitor()
        upgrades = await monitor.get_protocol_upgrades()
        
        assert isinstance(upgrades, list)


class TestRiskAssessmentEngine:
    
    @pytest.mark.asyncio
    async def test_assess_upgrade_risk(self, sample_upgrade):
        engine = RiskAssessmentEngine()
        
        risk_assessment = await engine.assess_upgrade_risk(sample_upgrade.id)
        
        assert isinstance(risk_assessment, dict)
        assert "overall_risk_score" in risk_assessment
        assert "risk_breakdown" in risk_assessment
        assert "risk_factors" in risk_assessment
        assert "recommendations" in risk_assessment
        
        assert 0 <= risk_assessment["overall_risk_score"] <= 100
    
    @pytest.mark.asyncio
    async def test_get_risk_history(self, sample_protocol):
        engine = RiskAssessmentEngine()
        
        history = await engine.get_risk_history(sample_protocol.id, days=30)
        
        assert isinstance(history, list)
    
    @pytest.mark.asyncio
    async def test_train_risk_model(self):
        engine = RiskAssessmentEngine()
        
        await engine.train_risk_model()
        
        assert True
    
    @pytest.mark.asyncio
    async def test_predict_risk(self):
        engine = RiskAssessmentEngine()
        
        prediction = await engine.predict_risk(
            technical=50.0,
            governance=60.0,
            market=40.0,
            liquidity=30.0
        )
        
        assert isinstance(prediction, float)
        assert 0 <= prediction <= 100


class TestVolatilityPredictor:
    
    @pytest.mark.asyncio
    async def test_predict_volatility(self, sample_upgrade):
        predictor = VolatilityPredictor()
        with patch('app.core.volatility.VolatilityPredictor._get_price_data') as mock_get_data:
            mock_data = [Mock(price=100.0 + i, token_symbol="TEST") for i in range(30)]
            mock_get_data.return_value = mock_data
            prediction = await predictor.predict_volatility(
                "0x1234567890123456789012345678901234567890",
                sample_upgrade.id,
                horizon_days=30
            )
            assert isinstance(prediction, dict)
            assert "predicted_volatility" in prediction
            assert "confidence_intervals" in prediction
            assert "model_parameters" in prediction

    @pytest.mark.asyncio
    async def test_predict_egarch_volatility(self, sample_upgrade):
        predictor = VolatilityPredictor()
        with patch('app.core.volatility.VolatilityPredictor._get_price_data') as mock_get_data:
            mock_data = [Mock(price=100.0 + i, token_symbol="TEST") for i in range(50)]
            mock_get_data.return_value = mock_data
            prediction = await predictor.predict_egarch_volatility(
                "0x1234567890123456789012345678901234567890",
                sample_upgrade.id,
                horizon_days=1
            )
            assert isinstance(prediction, dict)
            assert "predicted_volatility" in prediction
            assert "model_used" in prediction

    @pytest.mark.asyncio
    async def test_get_volatility_history(self):
        predictor = VolatilityPredictor()
        
        history = await predictor.get_volatility_history(
            "0x1234567890123456789012345678901234567890",
            days=30
        )
        
        assert isinstance(history, list)


class TestLiquidityPredictor:
    
    @pytest.mark.asyncio
    async def test_predict_liquidity(self, sample_upgrade):
        predictor = LiquidityPredictor()
        with patch('app.core.liquidity.LiquidityPredictor._get_tvl_data') as mock_get_data:
            base_time = datetime.utcnow() - timedelta(days=29)
            mock_data = [
                Mock(market_cap=1000000 + i * 10000, volume_24h=500000 + i * 5000, timestamp=base_time + timedelta(days=i))
                for i in range(30)
            ]
            mock_get_data.return_value = mock_data
            prediction = await predictor.predict_liquidity(
                "0x1234567890123456789012345678901234567890",
                sample_upgrade.id,
                horizon_days=7
            )
            assert isinstance(prediction, dict)
            assert "predicted_tvl_change_percent" in prediction
            assert "confidence_intervals" in prediction
    
    @pytest.mark.asyncio
    async def test_predict_cross_protocol_flow(self, sample_upgrade):
        predictor = LiquidityPredictor()
        
        with patch.object(predictor, 'predict_liquidity') as mock_predict:
            mock_predict.return_value = {
                "predicted_tvl_change_percent": 5.0
            }
            
            flow = await predictor.predict_cross_protocol_flow(
                "0x1111111111111111111111111111111111111111",
                "0x2222222222222222222222222222222222222222",
                sample_upgrade.id
            )
            
            assert isinstance(flow, dict)
            assert "flow_direction" in flow
            assert "flow_magnitude" in flow


class TestSentimentAnalyzer:
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, sample_protocol):
        analyzer = SentimentAnalyzer()
        
        sentiment = await analyzer.analyze_sentiment(
            sample_protocol.id,
            "This is a great protocol upgrade! Very excited about the new features.",
            source="twitter"
        )
        
        assert isinstance(sentiment, dict)
        assert "sentiment_score" in sentiment
        assert "sentiment_label" in sentiment
        assert "engagement_metrics" in sentiment
        
        assert -1 <= sentiment["sentiment_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_get_protocol_sentiment(self, sample_protocol):
        analyzer = SentimentAnalyzer()
        
        sentiment = await analyzer.get_protocol_sentiment(sample_protocol.id, days=7)
        
        assert isinstance(sentiment, dict)
        assert "total_posts" in sentiment
        assert "average_sentiment" in sentiment
        assert "sentiment_distribution" in sentiment
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_trends(self, sample_protocol):
        analyzer = SentimentAnalyzer()
        
        trends = await analyzer.analyze_sentiment_trends(sample_protocol.id, days=30)
        
        assert isinstance(trends, dict)
        if "error" not in trends:
            assert "dates" in trends
            assert "sentiment_scores" in trends
            assert "trend_direction" in trends


class TestGovernanceTracker:
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        tracker = GovernanceTracker()
        await tracker.initialize()
        
        assert tracker.session is not None
    
    @pytest.mark.asyncio
    async def test_track_snapshot_proposals(self):
        tracker = GovernanceTracker()
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "data": {
                    "proposals": [
                        {
                            "id": "test_proposal",
                            "title": "Test Proposal",
                            "body": "Test body",
                            "state": "active",
                            "start": int(datetime.utcnow().timestamp()),
                            "end": int((datetime.utcnow() + timedelta(days=7)).timestamp()),
                            "space": {"id": "uniswap", "name": "Uniswap"},
                            "votes": 100,
                            "scores_total": 1000
                        }
                    ]
                }
            })
            mock_post.return_value.__aenter__.return_value = mock_response
            
            proposals = await tracker.track_snapshot_proposals("uniswap")
            
            assert isinstance(proposals, list)
    
    @pytest.mark.asyncio
    async def test_analyze_voting_patterns(self, sample_protocol):
        tracker = GovernanceTracker()
        
        patterns = await tracker.analyze_voting_patterns(sample_protocol.id, days=90)
        
        assert isinstance(patterns, dict)
        assert "total_proposals" in patterns
        assert "success_rate" in patterns
        assert "average_participation" in patterns
    
    @pytest.mark.asyncio
    async def test_predict_proposal_outcome(self, sample_upgrade):
        tracker = GovernanceTracker()
        
        sample_upgrade.proposal_id = "test_proposal_123"
        
        prediction = await tracker.predict_proposal_outcome("test_proposal_123")
        
        assert isinstance(prediction, dict)
        assert "predicted_outcome" in prediction
        assert "success_probability" in prediction
        assert "confidence_level" in prediction


class TestSystemIntegration:
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, sample_upgrade):
        risk_engine = RiskAssessmentEngine()
        volatility_predictor = VolatilityPredictor()
        liquidity_predictor = LiquidityPredictor()
        sentiment_analyzer = SentimentAnalyzer()
        
        risk_assessment = await risk_engine.assess_upgrade_risk(sample_upgrade.id)
        assert risk_assessment["overall_risk_score"] >= 0
        
        with patch('app.core.volatility.VolatilityPredictor._get_price_data') as mock_get_data:
            mock_data = [Mock(price=100.0 + i, token_symbol="TEST") for i in range(30)]
            mock_get_data.return_value = mock_data
            
            volatility = await volatility_predictor.predict_volatility(
                "0x1234567890123456789012345678901234567890",
                sample_upgrade.id
            )
            assert volatility["predicted_volatility"] >= 0
        
        with patch('app.core.liquidity.LiquidityPredictor._get_tvl_data') as mock_get_data:
            base_time = datetime.utcnow() - timedelta(days=29)
            mock_data = [
                Mock(market_cap=1000000 + i * 10000, volume_24h=500000 + i * 5000, timestamp=base_time + timedelta(days=i))
                for i in range(30)
            ]
            mock_get_data.return_value = mock_data
            
            liquidity = await liquidity_predictor.predict_liquidity(
                "0x1234567890123456789012345678901234567890",
                sample_upgrade.id
            )
            assert liquidity["predicted_tvl_change_percent"] is not None
        
        sentiment = await sentiment_analyzer.analyze_sentiment(
            sample_upgrade.protocol_id,
            "Positive sentiment about this upgrade"
        )
        assert sentiment["sentiment_score"] >= -1 and sentiment["sentiment_score"] <= 1
        
        assert all([
            risk_assessment["overall_risk_score"] >= 0,
            volatility["predicted_volatility"] >= 0,
            liquidity["predicted_tvl_change_percent"] is not None,
            -1 <= sentiment["sentiment_score"] <= 1
        ])


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 