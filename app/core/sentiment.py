"""
Sentiment analysis for social media and news.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from textblob import TextBlob
import re
from loguru import logger

from app.database.models import SentimentData, Protocol
from app.database.database import SessionLocal


class SentimentAnalyzer:
    """Sentiment analysis for protocol-related social media content."""
    
    def __init__(self):
        self.sentiment_cache = {}
        
    async def analyze_sentiment(
        self, protocol_id: int, text_content: str, 
        source: str = "twitter"
    ) -> Dict[str, Any]:
        """Analyze sentiment of text content."""
        try:
            # Clean text
            cleaned_text = self._clean_text(text_content)
            
            # Analyze sentiment using TextBlob
            blob = TextBlob(cleaned_text)
            sentiment_score = blob.sentiment.polarity
            
            # Classify sentiment
            sentiment_label = self._classify_sentiment(sentiment_score)
            
            # Calculate engagement metrics (placeholder)
            engagement_metrics = self._calculate_engagement_metrics(text_content)
            
            # Store sentiment data
            db = SessionLocal()
            try:
                sentiment_data = SentimentData(
                    protocol_id=protocol_id,
                    source=source,
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_label,
                    text_content=cleaned_text,
                    user_count=1,  # Placeholder
                    engagement_metrics=engagement_metrics
                )
                
                db.add(sentiment_data)
                db.commit()
                
                return {
                    "protocol_id": protocol_id,
                    "source": source,
                    "sentiment_score": sentiment_score,
                    "sentiment_label": sentiment_label,
                    "engagement_metrics": engagement_metrics,
                    "analysis_time": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error storing sentiment data: {e}")
                db.rollback()
                raise
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text."""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.lower().strip()
    
    def _classify_sentiment(self, sentiment_score: float) -> str:
        """Classify sentiment based on score."""
        if sentiment_score > 0.1:
            return "positive"
        elif sentiment_score < -0.1:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_engagement_metrics(self, text: str) -> Dict[str, Any]:
        """Calculate engagement metrics from text."""
        # Placeholder implementation
        return {
            "likes": 0,
            "retweets": 0,
            "replies": 0,
            "word_count": len(text.split()),
            "hashtag_count": len(re.findall(r'#\w+', text)),
            "mention_count": len(re.findall(r'@\w+', text))
        }
    
    async def get_protocol_sentiment(
        self, protocol_id: int, days: int = 7
    ) -> Dict[str, Any]:
        """Get aggregated sentiment for a protocol."""
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            sentiment_data = db.query(SentimentData).filter(
                SentimentData.protocol_id == protocol_id,
                SentimentData.timestamp >= cutoff_date
            ).all()
            
            if not sentiment_data:
                return {
                    "protocol_id": protocol_id,
                    "total_posts": 0,
                    "average_sentiment": 0.0,
                    "sentiment_distribution": {},
                    "trend": "neutral"
                }
            
            # Calculate metrics
            total_posts = len(sentiment_data)
            average_sentiment = np.mean([s.sentiment_score for s in sentiment_data])
            
            # Sentiment distribution
            sentiment_counts = {}
            for data in sentiment_data:
                label = data.sentiment_label
                sentiment_counts[label] = sentiment_counts.get(label, 0) + 1
            
            # Determine trend
            recent_sentiment = np.mean([s.sentiment_score for s in sentiment_data[-10:]])
            trend = "improving" if recent_sentiment > average_sentiment else "declining"
            
            return {
                "protocol_id": protocol_id,
                "total_posts": total_posts,
                "average_sentiment": float(average_sentiment),
                "sentiment_distribution": sentiment_counts,
                "trend": trend,
                "analysis_period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting protocol sentiment: {e}")
            raise
        finally:
            db.close()
    
    async def analyze_sentiment_trends(
        self, protocol_id: int, days: int = 30
    ) -> Dict[str, Any]:
        """Analyze sentiment trends over time."""
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            sentiment_data = db.query(SentimentData).filter(
                SentimentData.protocol_id == protocol_id,
                SentimentData.timestamp >= cutoff_date
            ).order_by(SentimentData.timestamp.asc()).all()
            
            if not sentiment_data:
                return {"error": "No sentiment data available"}
            
            # Group by day
            daily_sentiment = {}
            for data in sentiment_data:
                date_key = data.timestamp.date()
                if date_key not in daily_sentiment:
                    daily_sentiment[date_key] = []
                daily_sentiment[date_key].append(data.sentiment_score)
            
            # Calculate daily averages
            dates = []
            avg_sentiments = []
            for date, scores in sorted(daily_sentiment.items()):
                dates.append(date.isoformat())
                avg_sentiments.append(np.mean(scores))
            
            # Calculate trend
            if len(avg_sentiments) > 1:
                trend_slope = np.polyfit(range(len(avg_sentiments)), avg_sentiments, 1)[0]
                trend_direction = "positive" if trend_slope > 0 else "negative"
            else:
                trend_direction = "stable"
            
            return {
                "protocol_id": protocol_id,
                "dates": dates,
                "sentiment_scores": [float(s) for s in avg_sentiments],
                "trend_direction": trend_direction,
                "volatility": float(np.std(avg_sentiments)) if len(avg_sentiments) > 1 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment trends: {e}")
            raise
        finally:
            db.close()
    
    async def get_sentiment_correlation(
        self, protocol_id: int, days: int = 30
    ) -> Dict[str, Any]:
        """Get correlation between sentiment and market movements."""
        # This would require market data integration
        # For now, return placeholder data
        return {
            "protocol_id": protocol_id,
            "correlation": 0.0,
            "significance": "low",
            "analysis_period_days": days
        }
    
    async def get_sentiment_alerts(
        self, threshold: float = 0.5, days: int = 1
    ) -> List[Dict]:
        """Get sentiment alerts for significant changes."""
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get recent sentiment data
            recent_sentiment = db.query(SentimentData).filter(
                SentimentData.timestamp >= cutoff_date
            ).all()
            
            alerts = []
            for data in recent_sentiment:
                if abs(data.sentiment_score) > threshold:
                    protocol = db.query(Protocol).filter(
                        Protocol.id == data.protocol_id
                    ).first()
                    
                    alerts.append({
                        "protocol_name": protocol.name if protocol else "Unknown",
                        "sentiment_score": data.sentiment_score,
                        "sentiment_label": data.sentiment_label,
                        "source": data.source,
                        "timestamp": data.timestamp.isoformat(),
                        "text_preview": data.text_content[:100] + "..." if len(data.text_content) > 100 else data.text_content
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting sentiment alerts: {e}")
            return []
        finally:
            db.close() 