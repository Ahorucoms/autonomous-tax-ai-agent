"""
Feedback Service for Malta Tax AI
Captures user feedback, analyzes satisfaction, and provides insights for continuous improvement
"""

import os
import json
import logging
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import statistics
from collections import defaultdict, Counter

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import required packages
import openai

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')


class FeedbackType(Enum):
    """Types of feedback"""
    RATING = "rating"
    THUMBS = "thumbs"
    DETAILED = "detailed"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    GENERAL = "general"


class FeedbackCategory(Enum):
    """Categories of feedback"""
    ACCURACY = "accuracy"
    HELPFULNESS = "helpfulness"
    SPEED = "speed"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    USABILITY = "usability"
    TECHNICAL = "technical"
    CONTENT = "content"


class SentimentScore(Enum):
    """Sentiment analysis scores"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


@dataclass
class UserFeedback:
    """User feedback data structure"""
    id: str
    user_id: str
    session_id: str
    query: str
    response: str
    feedback_type: FeedbackType
    rating: Optional[int] = None  # 1-5 scale
    thumbs: Optional[bool] = None  # True for up, False for down
    category: Optional[FeedbackCategory] = None
    comment: Optional[str] = None
    sentiment: Optional[SentimentScore] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    processed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FeedbackAnalytics:
    """Feedback analytics summary"""
    total_feedback: int
    average_rating: float
    thumbs_up_percentage: float
    sentiment_distribution: Dict[str, int]
    category_breakdown: Dict[str, int]
    trend_data: Dict[str, List[float]]
    top_issues: List[str]
    improvement_suggestions: List[str]
    time_period: str
    generated_at: datetime


@dataclass
class QualityMetrics:
    """Response quality metrics"""
    accuracy_score: float
    helpfulness_score: float
    clarity_score: float
    completeness_score: float
    overall_score: float
    confidence_level: str
    response_time_ms: float
    user_satisfaction: float
    improvement_areas: List[str]


class FeedbackService:
    """Service for capturing and analyzing user feedback"""
    
    def __init__(self, db_path: str = "/tmp/feedback.sqlite"):
        """Initialize feedback service"""
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database for feedback storage"""
        with sqlite3.connect(self.db_path) as conn:
            # Feedback table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    rating INTEGER,
                    thumbs BOOLEAN,
                    category TEXT,
                    comment TEXT,
                    sentiment TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP
                )
            """)
            
            # Quality metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id TEXT PRIMARY KEY,
                    feedback_id TEXT,
                    accuracy_score REAL,
                    helpfulness_score REAL,
                    clarity_score REAL,
                    completeness_score REAL,
                    overall_score REAL,
                    confidence_level TEXT,
                    response_time_ms REAL,
                    user_satisfaction REAL,
                    improvement_areas TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (feedback_id) REFERENCES feedback (id)
                )
            """)
            
            # Analytics cache table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics_cache (
                    id TEXT PRIMARY KEY,
                    time_period TEXT NOT NULL,
                    analytics_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback(category)")
    
    async def capture_feedback(self, feedback: UserFeedback) -> bool:
        """
        Capture user feedback
        
        Args:
            feedback: User feedback data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate feedback ID if not provided
            if not feedback.id:
                feedback.id = hashlib.sha256(
                    f"{feedback.user_id}_{feedback.session_id}_{feedback.created_at}".encode()
                ).hexdigest()[:16]
            
            # Analyze sentiment if comment provided
            if feedback.comment and not feedback.sentiment:
                feedback.sentiment = await self._analyze_sentiment(feedback.comment)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO feedback 
                    (id, user_id, session_id, query, response, feedback_type, rating, 
                     thumbs, category, comment, sentiment, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    feedback.id,
                    feedback.user_id,
                    feedback.session_id,
                    feedback.query,
                    feedback.response,
                    feedback.feedback_type.value,
                    feedback.rating,
                    feedback.thumbs,
                    feedback.category.value if feedback.category else None,
                    feedback.comment,
                    feedback.sentiment.value if feedback.sentiment else None,
                    json.dumps(feedback.metadata),
                    feedback.created_at.isoformat()
                ))
            
            self.logger.info(f"Captured feedback: {feedback.id}")
            
            # Trigger quality analysis
            await self._analyze_quality_metrics(feedback)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to capture feedback: {e}")
            return False
    
    async def _analyze_sentiment(self, comment: str) -> SentimentScore:
        """Analyze sentiment of feedback comment"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Analyze the sentiment of the following feedback comment. Respond with only one word: very_positive, positive, neutral, negative, or very_negative."},
                    {"role": "user", "content": comment}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            sentiment_text = response.choices[0].message.content.strip().lower()
            
            # Map to enum
            sentiment_map = {
                'very_positive': SentimentScore.VERY_POSITIVE,
                'positive': SentimentScore.POSITIVE,
                'neutral': SentimentScore.NEUTRAL,
                'negative': SentimentScore.NEGATIVE,
                'very_negative': SentimentScore.VERY_NEGATIVE
            }
            
            return sentiment_map.get(sentiment_text, SentimentScore.NEUTRAL)
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return SentimentScore.NEUTRAL
    
    async def _analyze_quality_metrics(self, feedback: UserFeedback):
        """Analyze quality metrics from feedback"""
        try:
            # Calculate quality scores based on feedback
            accuracy_score = self._calculate_accuracy_score(feedback)
            helpfulness_score = self._calculate_helpfulness_score(feedback)
            clarity_score = self._calculate_clarity_score(feedback)
            completeness_score = self._calculate_completeness_score(feedback)
            
            # Calculate overall score
            overall_score = statistics.mean([
                accuracy_score, helpfulness_score, clarity_score, completeness_score
            ])
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(overall_score)
            
            # Calculate user satisfaction
            user_satisfaction = self._calculate_user_satisfaction(feedback)
            
            # Identify improvement areas
            improvement_areas = self._identify_improvement_areas(feedback, {
                'accuracy': accuracy_score,
                'helpfulness': helpfulness_score,
                'clarity': clarity_score,
                'completeness': completeness_score
            })
            
            # Create quality metrics
            metrics = QualityMetrics(
                accuracy_score=accuracy_score,
                helpfulness_score=helpfulness_score,
                clarity_score=clarity_score,
                completeness_score=completeness_score,
                overall_score=overall_score,
                confidence_level=confidence_level,
                response_time_ms=feedback.metadata.get('response_time_ms', 0),
                user_satisfaction=user_satisfaction,
                improvement_areas=improvement_areas
            )
            
            # Store quality metrics
            metrics_id = hashlib.sha256(f"{feedback.id}_metrics".encode()).hexdigest()[:16]
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO quality_metrics 
                    (id, feedback_id, accuracy_score, helpfulness_score, clarity_score, 
                     completeness_score, overall_score, confidence_level, response_time_ms, 
                     user_satisfaction, improvement_areas)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics_id,
                    feedback.id,
                    metrics.accuracy_score,
                    metrics.helpfulness_score,
                    metrics.clarity_score,
                    metrics.completeness_score,
                    metrics.overall_score,
                    metrics.confidence_level,
                    metrics.response_time_ms,
                    metrics.user_satisfaction,
                    json.dumps(metrics.improvement_areas)
                ))
            
            self.logger.info(f"Analyzed quality metrics for feedback: {feedback.id}")
            
        except Exception as e:
            self.logger.error(f"Quality metrics analysis failed: {e}")
    
    def _calculate_accuracy_score(self, feedback: UserFeedback) -> float:
        """Calculate accuracy score from feedback"""
        if feedback.category == FeedbackCategory.ACCURACY:
            if feedback.rating:
                return feedback.rating / 5.0
            elif feedback.thumbs is not None:
                return 1.0 if feedback.thumbs else 0.2
        
        # Default scoring based on overall feedback
        if feedback.rating:
            return feedback.rating / 5.0
        elif feedback.thumbs is not None:
            return 0.8 if feedback.thumbs else 0.3
        
        return 0.7  # Neutral default
    
    def _calculate_helpfulness_score(self, feedback: UserFeedback) -> float:
        """Calculate helpfulness score from feedback"""
        if feedback.category == FeedbackCategory.HELPFULNESS:
            if feedback.rating:
                return feedback.rating / 5.0
            elif feedback.thumbs is not None:
                return 1.0 if feedback.thumbs else 0.2
        
        # Sentiment-based scoring
        sentiment_scores = {
            SentimentScore.VERY_POSITIVE: 1.0,
            SentimentScore.POSITIVE: 0.8,
            SentimentScore.NEUTRAL: 0.6,
            SentimentScore.NEGATIVE: 0.3,
            SentimentScore.VERY_NEGATIVE: 0.1
        }
        
        if feedback.sentiment:
            return sentiment_scores.get(feedback.sentiment, 0.6)
        
        return 0.6  # Neutral default
    
    def _calculate_clarity_score(self, feedback: UserFeedback) -> float:
        """Calculate clarity score from feedback"""
        if feedback.category == FeedbackCategory.CLARITY:
            if feedback.rating:
                return feedback.rating / 5.0
            elif feedback.thumbs is not None:
                return 1.0 if feedback.thumbs else 0.2
        
        # Response length and complexity analysis
        response_length = len(feedback.response.split())
        if response_length < 20:
            return 0.4  # Too short
        elif response_length > 200:
            return 0.6  # Might be too long
        else:
            return 0.8  # Good length
    
    def _calculate_completeness_score(self, feedback: UserFeedback) -> float:
        """Calculate completeness score from feedback"""
        if feedback.category == FeedbackCategory.COMPLETENESS:
            if feedback.rating:
                return feedback.rating / 5.0
            elif feedback.thumbs is not None:
                return 1.0 if feedback.thumbs else 0.2
        
        # Check if response addresses the query
        query_words = set(feedback.query.lower().split())
        response_words = set(feedback.response.lower().split())
        
        # Simple overlap analysis
        overlap = len(query_words.intersection(response_words))
        overlap_ratio = overlap / len(query_words) if query_words else 0
        
        return min(0.9, 0.5 + overlap_ratio)
    
    def _determine_confidence_level(self, overall_score: float) -> str:
        """Determine confidence level from overall score"""
        if overall_score >= 0.9:
            return "very_high"
        elif overall_score >= 0.7:
            return "high"
        elif overall_score >= 0.5:
            return "medium"
        elif overall_score >= 0.3:
            return "low"
        else:
            return "very_low"
    
    def _calculate_user_satisfaction(self, feedback: UserFeedback) -> float:
        """Calculate user satisfaction score"""
        if feedback.rating:
            return feedback.rating / 5.0
        elif feedback.thumbs is not None:
            return 1.0 if feedback.thumbs else 0.0
        
        # Sentiment-based satisfaction
        sentiment_satisfaction = {
            SentimentScore.VERY_POSITIVE: 1.0,
            SentimentScore.POSITIVE: 0.8,
            SentimentScore.NEUTRAL: 0.5,
            SentimentScore.NEGATIVE: 0.2,
            SentimentScore.VERY_NEGATIVE: 0.0
        }
        
        if feedback.sentiment:
            return sentiment_satisfaction.get(feedback.sentiment, 0.5)
        
        return 0.5  # Neutral default
    
    def _identify_improvement_areas(self, feedback: UserFeedback, scores: Dict[str, float]) -> List[str]:
        """Identify areas for improvement based on scores"""
        improvement_areas = []
        
        # Check low scores
        for area, score in scores.items():
            if score < 0.6:
                improvement_areas.append(area)
        
        # Check specific feedback categories
        if feedback.category:
            category_name = feedback.category.value
            if category_name not in improvement_areas and scores.get(category_name, 1.0) < 0.7:
                improvement_areas.append(category_name)
        
        # Check negative sentiment
        if feedback.sentiment in [SentimentScore.NEGATIVE, SentimentScore.VERY_NEGATIVE]:
            improvement_areas.append("user_experience")
        
        return improvement_areas
    
    async def get_feedback_analytics(self, time_period: str = "7d") -> FeedbackAnalytics:
        """
        Get feedback analytics for specified time period
        
        Args:
            time_period: Time period (1d, 7d, 30d, 90d)
            
        Returns:
            Feedback analytics summary
        """
        try:
            # Check cache first
            cached_analytics = self._get_cached_analytics(time_period)
            if cached_analytics:
                return cached_analytics
            
            # Calculate time range
            end_date = datetime.utcnow()
            days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
            days = days_map.get(time_period, 7)
            start_date = end_date - timedelta(days=days)
            
            # Query feedback data
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get feedback in time range
                cursor = conn.execute("""
                    SELECT * FROM feedback 
                    WHERE created_at >= ? AND created_at <= ?
                    ORDER BY created_at DESC
                """, (start_date.isoformat(), end_date.isoformat()))
                
                feedback_data = cursor.fetchall()
            
            # Calculate analytics
            total_feedback = len(feedback_data)
            
            if total_feedback == 0:
                return FeedbackAnalytics(
                    total_feedback=0,
                    average_rating=0.0,
                    thumbs_up_percentage=0.0,
                    sentiment_distribution={},
                    category_breakdown={},
                    trend_data={},
                    top_issues=[],
                    improvement_suggestions=[],
                    time_period=time_period,
                    generated_at=datetime.utcnow()
                )
            
            # Calculate metrics
            ratings = [row['rating'] for row in feedback_data if row['rating']]
            average_rating = statistics.mean(ratings) if ratings else 0.0
            
            thumbs_data = [row['thumbs'] for row in feedback_data if row['thumbs'] is not None]
            thumbs_up_count = sum(1 for thumb in thumbs_data if thumb)
            thumbs_up_percentage = (thumbs_up_count / len(thumbs_data) * 100) if thumbs_data else 0.0
            
            # Sentiment distribution
            sentiment_counts = Counter(row['sentiment'] for row in feedback_data if row['sentiment'])
            sentiment_distribution = dict(sentiment_counts)
            
            # Category breakdown
            category_counts = Counter(row['category'] for row in feedback_data if row['category'])
            category_breakdown = dict(category_counts)
            
            # Trend data (daily averages)
            trend_data = self._calculate_trend_data(feedback_data, days)
            
            # Top issues and suggestions
            top_issues = self._identify_top_issues(feedback_data)
            improvement_suggestions = await self._generate_improvement_suggestions(feedback_data)
            
            # Create analytics object
            analytics = FeedbackAnalytics(
                total_feedback=total_feedback,
                average_rating=average_rating,
                thumbs_up_percentage=thumbs_up_percentage,
                sentiment_distribution=sentiment_distribution,
                category_breakdown=category_breakdown,
                trend_data=trend_data,
                top_issues=top_issues,
                improvement_suggestions=improvement_suggestions,
                time_period=time_period,
                generated_at=datetime.utcnow()
            )
            
            # Cache analytics
            self._cache_analytics(time_period, analytics)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get feedback analytics: {e}")
            return FeedbackAnalytics(
                total_feedback=0,
                average_rating=0.0,
                thumbs_up_percentage=0.0,
                sentiment_distribution={},
                category_breakdown={},
                trend_data={},
                top_issues=[],
                improvement_suggestions=[],
                time_period=time_period,
                generated_at=datetime.utcnow()
            )
    
    def _get_cached_analytics(self, time_period: str) -> Optional[FeedbackAnalytics]:
        """Get cached analytics if available and not expired"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT analytics_data FROM analytics_cache 
                    WHERE time_period = ? AND expires_at > ?
                    ORDER BY created_at DESC LIMIT 1
                """, (time_period, datetime.utcnow().isoformat()))
                
                row = cursor.fetchone()
                if row:
                    analytics_data = json.loads(row['analytics_data'])
                    return FeedbackAnalytics(**analytics_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get cached analytics: {e}")
            return None
    
    def _cache_analytics(self, time_period: str, analytics: FeedbackAnalytics):
        """Cache analytics data"""
        try:
            # Set expiration (1 hour for short periods, 6 hours for longer)
            hours = 1 if time_period in ["1d", "7d"] else 6
            expires_at = datetime.utcnow() + timedelta(hours=hours)
            
            cache_id = hashlib.sha256(f"{time_period}_{analytics.generated_at}".encode()).hexdigest()[:16]
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO analytics_cache 
                    (id, time_period, analytics_data, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    cache_id,
                    time_period,
                    json.dumps(asdict(analytics), default=str),
                    expires_at.isoformat()
                ))
            
        except Exception as e:
            self.logger.error(f"Failed to cache analytics: {e}")
    
    def _calculate_trend_data(self, feedback_data: List, days: int) -> Dict[str, List[float]]:
        """Calculate trend data for analytics"""
        try:
            # Group feedback by day
            daily_data = defaultdict(list)
            
            for row in feedback_data:
                date_str = row['created_at'][:10]  # YYYY-MM-DD
                daily_data[date_str].append(row)
            
            # Calculate daily metrics
            trend_data = {
                'ratings': [],
                'satisfaction': [],
                'volume': []
            }
            
            # Generate data for each day
            end_date = datetime.utcnow().date()
            for i in range(days):
                date = end_date - timedelta(days=i)
                date_str = date.isoformat()
                
                day_feedback = daily_data.get(date_str, [])
                
                # Daily average rating
                day_ratings = [row['rating'] for row in day_feedback if row['rating']]
                avg_rating = statistics.mean(day_ratings) if day_ratings else 0.0
                trend_data['ratings'].append(avg_rating)
                
                # Daily satisfaction (thumbs up percentage)
                day_thumbs = [row['thumbs'] for row in day_feedback if row['thumbs'] is not None]
                satisfaction = (sum(day_thumbs) / len(day_thumbs) * 100) if day_thumbs else 0.0
                trend_data['satisfaction'].append(satisfaction)
                
                # Daily volume
                trend_data['volume'].append(len(day_feedback))
            
            # Reverse to get chronological order
            for key in trend_data:
                trend_data[key].reverse()
            
            return trend_data
            
        except Exception as e:
            self.logger.error(f"Failed to calculate trend data: {e}")
            return {}
    
    def _identify_top_issues(self, feedback_data: List) -> List[str]:
        """Identify top issues from feedback"""
        try:
            issues = []
            
            # Collect negative feedback
            negative_feedback = [
                row for row in feedback_data 
                if (row['rating'] and row['rating'] <= 2) or 
                   (row['thumbs'] is not None and not row['thumbs']) or
                   (row['sentiment'] in ['negative', 'very_negative'])
            ]
            
            # Analyze categories of negative feedback
            category_issues = Counter(row['category'] for row in negative_feedback if row['category'])
            
            # Add top category issues
            for category, count in category_issues.most_common(3):
                issues.append(f"Issues with {category.replace('_', ' ')}")
            
            # Analyze comments for common themes
            comments = [row['comment'] for row in negative_feedback if row['comment']]
            if comments:
                # Simple keyword analysis
                common_words = Counter()
                for comment in comments:
                    words = comment.lower().split()
                    # Filter out common words
                    filtered_words = [w for w in words if len(w) > 3 and w not in ['that', 'this', 'with', 'from', 'they', 'were', 'been', 'have']]
                    common_words.update(filtered_words)
                
                # Add top issues from comments
                for word, count in common_words.most_common(2):
                    if count >= 2:  # Mentioned at least twice
                        issues.append(f"Concerns about {word}")
            
            return issues[:5]  # Return top 5 issues
            
        except Exception as e:
            self.logger.error(f"Failed to identify top issues: {e}")
            return []
    
    async def _generate_improvement_suggestions(self, feedback_data: List) -> List[str]:
        """Generate improvement suggestions using AI"""
        try:
            # Collect negative feedback comments
            negative_comments = [
                row['comment'] for row in feedback_data 
                if row['comment'] and (
                    (row['rating'] and row['rating'] <= 3) or 
                    (row['thumbs'] is not None and not row['thumbs']) or
                    (row['sentiment'] in ['negative', 'very_negative'])
                )
            ]
            
            if not negative_comments:
                return ["Continue current excellent performance", "Monitor user satisfaction trends"]
            
            # Analyze with AI
            comments_text = "\n".join(negative_comments[:10])  # Limit to 10 comments
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing user feedback for a Malta tax AI system. Based on the negative feedback comments, provide 3-5 specific, actionable improvement suggestions. Focus on practical improvements that can be implemented."},
                    {"role": "user", "content": f"Analyze these negative feedback comments and suggest improvements:\n\n{comments_text}"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            suggestions_text = response.choices[0].message.content
            
            # Parse suggestions (assume they're in a list format)
            suggestions = []
            for line in suggestions_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                    # Clean up the suggestion
                    suggestion = line.lstrip('-•0123456789. ').strip()
                    if suggestion:
                        suggestions.append(suggestion)
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to generate improvement suggestions: {e}")
            return ["Review recent feedback for improvement opportunities", "Focus on user experience enhancements"]
    
    def get_feedback_by_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get feedback for specific user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM feedback 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Failed to get user feedback: {e}")
            return []
    
    def get_quality_metrics_summary(self, time_period: str = "7d") -> Dict[str, Any]:
        """Get quality metrics summary"""
        try:
            # Calculate time range
            end_date = datetime.utcnow()
            days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
            days = days_map.get(time_period, 7)
            start_date = end_date - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT qm.* FROM quality_metrics qm
                    JOIN feedback f ON qm.feedback_id = f.id
                    WHERE f.created_at >= ? AND f.created_at <= ?
                """, (start_date.isoformat(), end_date.isoformat()))
                
                metrics_data = cursor.fetchall()
            
            if not metrics_data:
                return {}
            
            # Calculate averages
            accuracy_scores = [row['accuracy_score'] for row in metrics_data if row['accuracy_score']]
            helpfulness_scores = [row['helpfulness_score'] for row in metrics_data if row['helpfulness_score']]
            clarity_scores = [row['clarity_score'] for row in metrics_data if row['clarity_score']]
            completeness_scores = [row['completeness_score'] for row in metrics_data if row['completeness_score']]
            overall_scores = [row['overall_score'] for row in metrics_data if row['overall_score']]
            response_times = [row['response_time_ms'] for row in metrics_data if row['response_time_ms']]
            satisfaction_scores = [row['user_satisfaction'] for row in metrics_data if row['user_satisfaction']]
            
            return {
                'average_accuracy': statistics.mean(accuracy_scores) if accuracy_scores else 0.0,
                'average_helpfulness': statistics.mean(helpfulness_scores) if helpfulness_scores else 0.0,
                'average_clarity': statistics.mean(clarity_scores) if clarity_scores else 0.0,
                'average_completeness': statistics.mean(completeness_scores) if completeness_scores else 0.0,
                'average_overall': statistics.mean(overall_scores) if overall_scores else 0.0,
                'average_response_time': statistics.mean(response_times) if response_times else 0.0,
                'average_satisfaction': statistics.mean(satisfaction_scores) if satisfaction_scores else 0.0,
                'total_metrics': len(metrics_data),
                'time_period': time_period
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get quality metrics summary: {e}")
            return {}


# Global instance
feedback_service = FeedbackService()


# Helper functions for easy access
async def capture_user_feedback(user_id: str, session_id: str, query: str, response: str,
                              feedback_type: str = "rating", rating: int = None,
                              thumbs: bool = None, category: str = None,
                              comment: str = None, metadata: Dict[str, Any] = None) -> bool:
    """
    Simple function to capture user feedback
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        query: Original user query
        response: AI response
        feedback_type: Type of feedback (rating, thumbs, detailed, etc.)
        rating: Rating score (1-5)
        thumbs: Thumbs up/down (True/False)
        category: Feedback category
        comment: User comment
        metadata: Additional metadata
        
    Returns:
        True if successful, False otherwise
    """
    feedback = UserFeedback(
        id="",  # Will be generated
        user_id=user_id,
        session_id=session_id,
        query=query,
        response=response,
        feedback_type=FeedbackType(feedback_type),
        rating=rating,
        thumbs=thumbs,
        category=FeedbackCategory(category) if category else None,
        comment=comment,
        metadata=metadata or {}
    )
    
    return await feedback_service.capture_feedback(feedback)


async def get_feedback_analytics_summary(time_period: str = "7d") -> Dict[str, Any]:
    """
    Get feedback analytics summary
    
    Args:
        time_period: Time period for analytics (1d, 7d, 30d, 90d)
        
    Returns:
        Analytics summary dictionary
    """
    analytics = await feedback_service.get_feedback_analytics(time_period)
    return asdict(analytics)

