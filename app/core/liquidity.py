"""
Liquidity prediction using time series models.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error
from loguru import logger

from app.database.models import LiquidityPrediction, MarketData, ProtocolUpgrade
from app.database.database import SessionLocal


class LiquidityPredictor:
    """Liquidity prediction using time series models."""
    
    def __init__(self):
        self.models = {}
        self.historical_tvl = {}
        
    async def predict_liquidity(
        self, protocol_address: str, upgrade_id: int, 
        horizon_days: int = 7
    ) -> Dict[str, Any]:
        """Predict liquidity movement for a protocol around an upgrade."""
        db = SessionLocal()
        try:
            # Get historical TVL data
            tvl_data = await self._get_tvl_data(db, protocol_address, days=90)
            
            if len(tvl_data) < 30:
                raise ValueError("Insufficient TVL data for prediction")
            
            # Prepare time series data
            tvl_series = self._prepare_tvl_series(tvl_data)
            
            # Check stationarity
            if not self._is_stationary(tvl_series):
                tvl_series = self._make_stationary(tvl_series)
            
            # Fit ARIMA model
            arima_model = self._fit_arima_model(tvl_series)
            
            # Make prediction
            forecast = arima_model.forecast(steps=horizon_days)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                forecast, tvl_series, horizon_days
            )
            
            # Calculate percentage change
            current_tvl = tvl_series.iloc[-1]
            predicted_tvl = forecast.iloc[-1]
            tvl_change_percent = ((predicted_tvl - current_tvl) / current_tvl) * 100
            
            # Store prediction
            prediction = LiquidityPrediction(
                upgrade_id=upgrade_id,
                protocol_address=protocol_address,
                prediction_horizon=horizon_days,
                predicted_tvl_change=tvl_change_percent,
                predicted_volume_change=0.0,  # Placeholder
                confidence_interval_lower=float(confidence_intervals[0]),
                confidence_interval_upper=float(confidence_intervals[1]),
                model_used="ARIMA",
                model_parameters={
                    "order": str(arima_model.model.order),
                    "aic": float(arima_model.aic)
                }
            )
            
            db.add(prediction)
            db.commit()
            
            return {
                "protocol_address": protocol_address,
                "upgrade_id": upgrade_id,
                "predicted_tvl_change_percent": tvl_change_percent,
                "current_tvl": float(current_tvl),
                "predicted_tvl": float(predicted_tvl),
                "forecast_values": forecast.tolist(),
                "confidence_intervals": {
                    "lower": float(confidence_intervals[0]),
                    "upper": float(confidence_intervals[1])
                },
                "model_parameters": prediction.model_parameters,
                "prediction_horizon": horizon_days,
                "prediction_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting liquidity: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _get_tvl_data(
        self, db, protocol_address: str, days: int = 90
    ) -> List[MarketData]:
        """Get historical TVL data for a protocol."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # In a real implementation, you would fetch TVL data from DeFi APIs
        # For now, we'll use market data as a proxy
        return db.query(MarketData).filter(
            MarketData.token_address == protocol_address,
            MarketData.timestamp >= cutoff_date
        ).order_by(MarketData.timestamp.asc()).all()
    
    def _prepare_tvl_series(self, tvl_data: List[MarketData]) -> pd.Series:
        """Prepare TVL data as a time series."""
        # Use market cap as proxy for TVL
        data = []
        for record in tvl_data:
            data.append({
                'timestamp': record.timestamp,
                'tvl': record.market_cap or record.volume_24h or 1000000  # Fallback value
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        
        # Resample to daily data if needed
        if len(df) > 0:
            df = df.resample('D').mean().fillna(method='ffill')
        
        return df['tvl']
    
    def _is_stationary(self, series: pd.Series) -> bool:
        """Check if time series is stationary using Augmented Dickey-Fuller test."""
        try:
            result = adfuller(series.dropna())
            return result[1] < 0.05  # p-value < 0.05 indicates stationarity
        except Exception as e:
            logger.warning(f"Error in stationarity test: {e}")
            return False
    
    def _make_stationary(self, series: pd.Series) -> pd.Series:
        """Make time series stationary using differencing."""
        # First difference
        diff_series = series.diff().dropna()
        
        if self._is_stationary(diff_series):
            return diff_series
        else:
            # Second difference
            diff2_series = diff_series.diff().dropna()
            return diff2_series
    
    def _fit_arima_model(self, series: pd.Series):
        """Fit ARIMA model to the time series."""
        try:
            # Auto-fit ARIMA model
            model = ARIMA(series, order=(1, 1, 1))
            fitted_model = model.fit()
            
            return fitted_model
            
        except Exception as e:
            logger.error(f"Error fitting ARIMA model: {e}")
            # Fallback to simple model
            return self._fit_simple_model(series)
    
    def _fit_simple_model(self, series: pd.Series):
        """Fit a simple moving average model as fallback."""
        class SimpleModel:
            def __init__(self, series):
                self.series = series
                self.mean = series.mean()
                self.trend = np.polyfit(range(len(series)), series.values, 1)[0]
            
            def forecast(self, steps):
                last_value = self.series.iloc[-1]
                forecast_values = []
                for i in range(1, steps + 1):
                    forecast_values.append(last_value + (self.trend * i))
                return pd.Series(forecast_values)
        
        return SimpleModel(series)
    
    def _calculate_confidence_intervals(
        self, forecast: pd.Series, original_series: pd.Series, 
        horizon_days: int
    ) -> Tuple[float, float]:
        """Calculate confidence intervals for the forecast."""
        # Use historical volatility
        historical_vol = original_series.std()
        
        # 95% confidence interval
        lower_bound = forecast.iloc[-1] - 1.96 * historical_vol
        upper_bound = forecast.iloc[-1] + 1.96 * historical_vol
        
        return lower_bound, upper_bound
    
    async def predict_cross_protocol_flow(
        self, source_protocol: str, target_protocol: str, 
        upgrade_id: int
    ) -> Dict[str, Any]:
        """Predict cross-protocol liquidity flow."""
        try:
            # Get TVL predictions for both protocols
            source_prediction = await self.predict_liquidity(
                source_protocol, upgrade_id, horizon_days=7
            )
            target_prediction = await self.predict_liquidity(
                target_protocol, upgrade_id, horizon_days=7
            )
            
            # Calculate flow direction and magnitude
            flow_magnitude = target_prediction["predicted_tvl_change_percent"] - source_prediction["predicted_tvl_change_percent"]
            
            if flow_magnitude > 0:
                flow_direction = "inflow"
                flow_description = f"Liquidity flowing from {source_protocol} to {target_protocol}"
            else:
                flow_direction = "outflow"
                flow_description = f"Liquidity flowing from {target_protocol} to {source_protocol}"
            
            return {
                "source_protocol": source_protocol,
                "target_protocol": target_protocol,
                "upgrade_id": upgrade_id,
                "flow_direction": flow_direction,
                "flow_magnitude": abs(flow_magnitude),
                "flow_description": flow_description,
                "source_tvl_change": source_prediction["predicted_tvl_change_percent"],
                "target_tvl_change": target_prediction["predicted_tvl_change_percent"],
                "prediction_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting cross-protocol flow: {e}")
            raise
    
    async def analyze_liquidity_regime(
        self, protocol_address: str, upgrade_id: int
    ) -> Dict[str, Any]:
        """Analyze liquidity regime changes around upgrades."""
        db = SessionLocal()
        try:
            # Get upgrade details
            upgrade = db.query(ProtocolUpgrade).filter(
                ProtocolUpgrade.id == upgrade_id
            ).first()
            
            if not upgrade:
                raise ValueError(f"Upgrade {upgrade_id} not found")
            
            # Get TVL data around upgrade
            upgrade_time = upgrade.execution_time or upgrade.created_at
            pre_upgrade_data = await self._get_tvl_data(
                db, protocol_address, days=30, end_date=upgrade_time
            )
            post_upgrade_data = await self._get_tvl_data(
                db, protocol_address, days=30, start_date=upgrade_time
            )
            
            # Calculate liquidity metrics
            pre_tvl_series = self._prepare_tvl_series(pre_upgrade_data)
            post_tvl_series = self._prepare_tvl_series(post_upgrade_data)
            
            pre_avg_tvl = pre_tvl_series.mean() if len(pre_tvl_series) > 0 else 0
            post_avg_tvl = post_tvl_series.mean() if len(post_tvl_series) > 0 else 0
            
            pre_volatility = pre_tvl_series.std() if len(pre_tvl_series) > 0 else 0
            post_volatility = post_tvl_series.std() if len(post_tvl_series) > 0 else 0
            
            # Calculate regime change
            tvl_change = (post_avg_tvl - pre_avg_tvl) / pre_avg_tvl if pre_avg_tvl > 0 else 0
            volatility_change = (post_volatility - pre_volatility) / pre_volatility if pre_volatility > 0 else 0
            
            regime_classification = self._classify_liquidity_regime(
                tvl_change, volatility_change
            )
            
            return {
                "protocol_address": protocol_address,
                "upgrade_id": upgrade_id,
                "pre_upgrade_avg_tvl": float(pre_avg_tvl),
                "post_upgrade_avg_tvl": float(post_avg_tvl),
                "tvl_change_percent": tvl_change * 100,
                "pre_upgrade_volatility": float(pre_volatility),
                "post_upgrade_volatility": float(post_volatility),
                "volatility_change_percent": volatility_change * 100,
                "regime_classification": regime_classification,
                "analysis_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing liquidity regime: {e}")
            raise
        finally:
            db.close()
    
    async def _get_tvl_data(
        self, db, protocol_address: str, days: int = 90, 
        start_date: datetime = None, end_date: datetime = None
    ) -> List[MarketData]:
        """Get TVL data with optional date range."""
        query = db.query(MarketData).filter(
            MarketData.token_address == protocol_address
        )
        
        if start_date:
            query = query.filter(MarketData.timestamp >= start_date)
        if end_date:
            query = query.filter(MarketData.timestamp <= end_date)
        if not start_date and not end_date:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(MarketData.timestamp >= cutoff_date)
        
        return query.order_by(MarketData.timestamp.asc()).all()
    
    def _classify_liquidity_regime(
        self, tvl_change: float, volatility_change: float
    ) -> str:
        """Classify liquidity regime based on changes."""
        if tvl_change > 0.1 and volatility_change < 0.1:
            return "stable_growth"
        elif tvl_change > 0.1 and volatility_change > 0.1:
            return "volatile_growth"
        elif tvl_change < -0.1 and volatility_change < 0.1:
            return "stable_decline"
        elif tvl_change < -0.1 and volatility_change > 0.1:
            return "volatile_decline"
        elif abs(tvl_change) <= 0.1 and volatility_change > 0.1:
            return "high_volatility_stable"
        else:
            return "stable"
    
    async def get_liquidity_history(
        self, protocol_address: str, days: int = 30
    ) -> List[Dict]:
        """Get historical liquidity predictions for a protocol."""
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            predictions = db.query(LiquidityPrediction).filter(
                LiquidityPrediction.protocol_address == protocol_address,
                LiquidityPrediction.prediction_time >= cutoff_date
            ).order_by(LiquidityPrediction.prediction_time.desc()).all()
            
            return [
                {
                    "id": pred.id,
                    "upgrade_id": pred.upgrade_id,
                    "predicted_tvl_change": pred.predicted_tvl_change,
                    "model_used": pred.model_used,
                    "prediction_horizon": pred.prediction_horizon,
                    "prediction_time": pred.prediction_time.isoformat()
                }
                for pred in predictions
            ]
        finally:
            db.close()
    
    async def evaluate_model_performance(
        self, protocol_address: str, days: int = 30
    ) -> Dict[str, Any]:
        """Evaluate liquidity prediction model performance."""
        db = SessionLocal()
        try:
            # Get predictions and actual TVL changes
            predictions = await self.get_liquidity_history(protocol_address, days)
            
            if len(predictions) < 10:
                return {"error": "Insufficient data for evaluation"}
            
            # Calculate performance metrics
            actual_changes = []
            predicted_changes = []
            
            for pred in predictions:
                # Get actual TVL change for the prediction period
                actual_change = await self._get_actual_tvl_change(
                    db, protocol_address, pred["prediction_time"], 
                    pred["prediction_horizon"]
                )
                if actual_change is not None:
                    actual_changes.append(actual_change)
                    predicted_changes.append(pred["predicted_tvl_change"])
            
            if len(actual_changes) < 5:
                return {"error": "Insufficient actual data for evaluation"}
            
            # Calculate metrics
            mse = mean_squared_error(actual_changes, predicted_changes)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(np.array(actual_changes) - np.array(predicted_changes)))
            
            return {
                "protocol_address": protocol_address,
                "evaluation_period_days": days,
                "num_predictions": len(predictions),
                "mean_squared_error": mse,
                "root_mean_squared_error": rmse,
                "mean_absolute_error": mae,
                "mean_actual_change": np.mean(actual_changes),
                "mean_predicted_change": np.mean(predicted_changes)
            }
            
        except Exception as e:
            logger.error(f"Error evaluating model performance: {e}")
            return {"error": str(e)}
        finally:
            db.close()
    
    async def _get_actual_tvl_change(
        self, db, protocol_address: str, prediction_time: str, 
        horizon_days: int
    ) -> Optional[float]:
        """Get actual TVL change for a prediction period."""
        try:
            pred_time = datetime.fromisoformat(prediction_time)
            start_date = pred_time
            end_date = pred_time + timedelta(days=horizon_days)
            
            tvl_data = await self._get_tvl_data(
                db, protocol_address, start_date=start_date, end_date=end_date
            )
            
            if len(tvl_data) < 2:
                return None
            
            tvl_series = self._prepare_tvl_series(tvl_data)
            if len(tvl_series) < 2:
                return None
            
            start_tvl = tvl_series.iloc[0]
            end_tvl = tvl_series.iloc[-1]
            
            return ((end_tvl - start_tvl) / start_tvl) * 100
            
        except Exception as e:
            logger.error(f"Error getting actual TVL change: {e}")
            return None 