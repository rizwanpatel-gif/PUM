"""
Volatility prediction using GARCH models.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from arch import arch_model
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from loguru import logger

from app.database.models import MarketData, VolatilityPrediction, ProtocolUpgrade
from app.database.database import SessionLocal


class VolatilityPredictor:
    """Volatility prediction using GARCH and time series models."""
    
    def __init__(self):
        self.models = {}
        self.historical_volatility = {}
        
    async def predict_volatility(
        self, token_address: str, upgrade_id: int, 
        horizon_days: int = 30
    ) -> Dict[str, Any]:
        """Predict volatility for a token around an upgrade event."""
        db = SessionLocal()
        try:
            # Get historical price data
            price_data = await self._get_price_data(db, token_address, days=90)
            
            if len(price_data) < 30:
                raise ValueError("Insufficient price data for volatility prediction")
            
            # Calculate returns
            returns = self._calculate_returns(price_data)

            # Rescale returns to avoid DataScaleWarning
            returns = returns * 1e4

            # Fit GARCH model
            garch_model = self._fit_garch_model(returns)
            
            # Make volatility forecast
            forecast = garch_model.forecast(horizon=horizon_days)
            volatility_forecast = np.sqrt(forecast.variance.values[-1, :])
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                volatility_forecast, returns
            )
            
            # Store prediction
            prediction = VolatilityPrediction(
                upgrade_id=upgrade_id,
                token_address=token_address,
                token_symbol=price_data[0].token_symbol if price_data else "UNKNOWN",
                prediction_horizon=horizon_days,
                predicted_volatility=float(volatility_forecast[-1]),
                confidence_interval_lower=float(confidence_intervals[0]),
                confidence_interval_upper=float(confidence_intervals[1]),
                model_used="GARCH(1,1)",
                model_parameters={
                    "omega": float(garch_model.params.iloc[0]),
                    "alpha": float(garch_model.params.iloc[1]),
                    "beta": float(garch_model.params.iloc[2])
                }
            )
            
            db.add(prediction)
            db.commit()
            
            return {
                "token_address": token_address,
                "upgrade_id": upgrade_id,
                "predicted_volatility": float(volatility_forecast[-1]),
                "volatility_forecast": volatility_forecast.tolist(),
                "confidence_intervals": {
                    "lower": float(confidence_intervals[0]),
                    "upper": float(confidence_intervals[1])
                },
                "model_parameters": prediction.model_parameters,
                "prediction_horizon": horizon_days,
                "prediction_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting volatility: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _get_price_data(
        self, db, token_address: str, days: int = 90
    ) -> List[MarketData]:
        """Get historical price data for a token."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return db.query(MarketData).filter(
            MarketData.token_address == token_address,
            MarketData.timestamp >= cutoff_date
        ).order_by(MarketData.timestamp.asc()).all()
    
    def _calculate_returns(self, price_data: List[MarketData]) -> np.ndarray:
        """Calculate log returns from price data."""
        prices = [data.price for data in price_data]
        log_prices = np.log(prices)
        returns = np.diff(log_prices)
        return returns
    
    def _fit_garch_model(self, returns: np.ndarray):
        """Fit GARCH(1,1) model to returns."""
        try:
            # Fit GARCH(1,1) model
            model = arch_model(returns, vol='GARCH', p=1, q=1)
            fitted_model = model.fit(disp='off')
            
            return fitted_model
            
        except Exception as e:
            logger.error(f"Error fitting GARCH model: {e}")
            # Fallback to simpler model
            return self._fit_simple_volatility_model(returns)
    
    def _fit_simple_volatility_model(self, returns: np.ndarray):
        """Fit a simple volatility model as fallback."""
        # Simple rolling volatility model
        class SimpleVolatilityModel:
            def __init__(self, returns):
                self.returns = returns
                self.volatility = np.std(returns)
            
            def forecast(self, horizon):
                class Forecast:
                    def __init__(self, volatility, horizon):
                        self.variance = pd.DataFrame(
                            np.full((1, horizon), volatility**2)
                        )
                return Forecast(self.volatility, horizon)
        
        return SimpleVolatilityModel(returns)
    
    def _calculate_confidence_intervals(
        self, volatility_forecast: np.ndarray, returns: np.ndarray
    ) -> Tuple[float, float]:
        """Calculate confidence intervals for volatility forecast."""
        # Use historical volatility distribution
        historical_vol = np.std(returns)
        std_error = historical_vol / np.sqrt(len(returns))
        
        # 95% confidence interval
        lower_bound = max(0, volatility_forecast[-1] - 1.96 * std_error)
        upper_bound = volatility_forecast[-1] + 1.96 * std_error
        
        return lower_bound, upper_bound
    
    async def predict_egarch_volatility(
        self, token_address: str, upgrade_id: int, 
        horizon_days: int = 30
    ) -> Dict[str, Any]:
        """Predict volatility using EGARCH model (captures asymmetric effects)."""
        db = SessionLocal()
        try:
            # Get price data
            price_data = await self._get_price_data(db, token_address, days=90)
            returns = self._calculate_returns(price_data)

            # Rescale returns to avoid DataScaleWarning
            returns = returns * 1e4

            # Fit EGARCH model
            model = arch_model(returns, vol='EGARCH', p=1, q=1, o=1)
            fitted_model = model.fit(disp='off')
            
            # Make forecast
            forecast = fitted_model.forecast(horizon=horizon_days)
            volatility_forecast = np.sqrt(forecast.variance.values[-1, :])
            
            # Store prediction
            prediction = VolatilityPrediction(
                upgrade_id=upgrade_id,
                token_address=token_address,
                token_symbol=price_data[0].token_symbol if price_data else "UNKNOWN",
                prediction_horizon=horizon_days,
                predicted_volatility=float(volatility_forecast[-1]),
                confidence_interval_lower=float(volatility_forecast[-1] * 0.8),
                confidence_interval_upper=float(volatility_forecast[-1] * 1.2),
                model_used="EGARCH(1,1,1)",
                model_parameters={
                    "omega": float(fitted_model.params.iloc[0]),
                    "alpha": float(fitted_model.params.iloc[1]),
                    "gamma": float(fitted_model.params.iloc[2]),
                    "beta": float(fitted_model.params.iloc[3])
                }
            )
            
            db.add(prediction)
            db.commit()
            
            return {
                "token_address": token_address,
                "upgrade_id": upgrade_id,
                "predicted_volatility": float(volatility_forecast[-1]),
                "model_used": "EGARCH(1,1,1)",
                "model_parameters": prediction.model_parameters,
                "prediction_horizon": horizon_days
            }
            
        except Exception as e:
            logger.error(f"Error predicting EGARCH volatility: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def analyze_volatility_regime(
        self, token_address: str, upgrade_id: int
    ) -> Dict[str, Any]:
        """Analyze volatility regime changes around upgrades."""
        db = SessionLocal()
        try:
            # Get upgrade details
            upgrade = db.query(ProtocolUpgrade).filter(
                ProtocolUpgrade.id == upgrade_id
            ).first()
            
            if not upgrade:
                raise ValueError(f"Upgrade {upgrade_id} not found")
            
            # Get price data around upgrade
            upgrade_time = upgrade.execution_time or upgrade.created_at
            pre_upgrade_data = await self._get_price_data(
                db, token_address, days=30, end_date=upgrade_time
            )
            post_upgrade_data = await self._get_price_data(
                db, token_address, days=30, start_date=upgrade_time
            )
            
            # Calculate volatility in each period
            pre_volatility = self._calculate_period_volatility(pre_upgrade_data)
            post_volatility = self._calculate_period_volatility(post_upgrade_data)
            
            # Determine regime change
            volatility_change = (post_volatility - pre_volatility) / pre_volatility
            regime_change = self._classify_regime_change(volatility_change)
            
            return {
                "token_address": token_address,
                "upgrade_id": upgrade_id,
                "pre_upgrade_volatility": pre_volatility,
                "post_upgrade_volatility": post_volatility,
                "volatility_change_percent": volatility_change * 100,
                "regime_change": regime_change,
                "analysis_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volatility regime: {e}")
            raise
        finally:
            db.close()
    
    async def _get_price_data(
        self, db, token_address: str, days: int = 90, 
        start_date: datetime = None, end_date: datetime = None
    ) -> List[MarketData]:
        """Get price data with optional date range."""
        query = db.query(MarketData).filter(
            MarketData.token_address == token_address
        )
        
        if start_date:
            query = query.filter(MarketData.timestamp >= start_date)
        if end_date:
            query = query.filter(MarketData.timestamp <= end_date)
        if not start_date and not end_date:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(MarketData.timestamp >= cutoff_date)
        
        return query.order_by(MarketData.timestamp.asc()).all()
    
    def _calculate_period_volatility(self, price_data: List[MarketData]) -> float:
        """Calculate volatility for a specific period."""
        if len(price_data) < 2:
            return 0.0
        
        prices = [data.price for data in price_data]
        returns = np.diff(np.log(prices))
        return np.std(returns) * np.sqrt(365)  # Annualized volatility
    
    def _classify_regime_change(self, volatility_change: float) -> str:
        """Classify volatility regime change."""
        if volatility_change > 0.5:
            return "high_volatility_regime"
        elif volatility_change > 0.1:
            return "moderate_volatility_increase"
        elif volatility_change < -0.5:
            return "low_volatility_regime"
        elif volatility_change < -0.1:
            return "moderate_volatility_decrease"
        else:
            return "stable_volatility"
    
    async def get_volatility_history(
        self, token_address: str, days: int = 30
    ) -> List[Dict]:
        """Get historical volatility predictions for a token."""
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            predictions = db.query(VolatilityPrediction).filter(
                VolatilityPrediction.token_address == token_address,
                VolatilityPrediction.prediction_time >= cutoff_date
            ).order_by(VolatilityPrediction.prediction_time.desc()).all()
            
            return [
                {
                    "id": pred.id,
                    "upgrade_id": pred.upgrade_id,
                    "predicted_volatility": pred.predicted_volatility,
                    "model_used": pred.model_used,
                    "prediction_horizon": pred.prediction_horizon,
                    "prediction_time": pred.prediction_time.isoformat()
                }
                for pred in predictions
            ]
        finally:
            db.close()
    
    async def evaluate_model_performance(
        self, token_address: str, days: int = 30
    ) -> Dict[str, Any]:
        """Evaluate volatility model performance."""
        db = SessionLocal()
        try:
            # Get predictions and actual volatility
            predictions = await self.get_volatility_history(token_address, days)
            
            if len(predictions) < 10:
                return {"error": "Insufficient data for evaluation"}
            
            # Calculate performance metrics
            actual_volatilities = []
            predicted_volatilities = []
            
            for pred in predictions:
                # Get actual volatility for the prediction period
                actual_vol = await self._get_actual_volatility(
                    db, token_address, pred["prediction_time"], 
                    pred["prediction_horizon"]
                )
                if actual_vol is not None:
                    actual_volatilities.append(actual_vol)
                    predicted_volatilities.append(pred["predicted_volatility"])
            
            if len(actual_volatilities) < 5:
                return {"error": "Insufficient actual data for evaluation"}
            
            # Calculate metrics
            mse = mean_squared_error(actual_volatilities, predicted_volatilities)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(np.array(actual_volatilities) - np.array(predicted_volatilities)))
            
            return {
                "token_address": token_address,
                "evaluation_period_days": days,
                "num_predictions": len(predictions),
                "mean_squared_error": mse,
                "root_mean_squared_error": rmse,
                "mean_absolute_error": mae,
                "mean_actual_volatility": np.mean(actual_volatilities),
                "mean_predicted_volatility": np.mean(predicted_volatilities)
            }
            
        except Exception as e:
            logger.error(f"Error evaluating model performance: {e}")
            return {"error": str(e)}
        finally:
            db.close()
    
    async def _get_actual_volatility(
        self, db, token_address: str, prediction_time: str, 
        horizon_days: int
    ) -> Optional[float]:
        """Get actual volatility for a prediction period."""
        try:
            pred_time = datetime.fromisoformat(prediction_time)
            start_date = pred_time
            end_date = pred_time + timedelta(days=horizon_days)
            
            price_data = await self._get_price_data(
                db, token_address, start_date=start_date, end_date=end_date
            )
            
            if len(price_data) < 2:
                return None
            
            return self._calculate_period_volatility(price_data)
            
        except Exception as e:
            logger.error(f"Error getting actual volatility: {e}")
            return None 