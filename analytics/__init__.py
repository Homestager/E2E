"""
Marketing Analytics Report Generator

Generates PNG reports for Telegram bot with:
- Graph 1: Cross-analytics (Сквозная аналитика) - all campaigns overview
- Graph 2: Campaign analytics - detailed analysis within single campaign
"""

from .models import (
    Campaign,
    Source,
    SocialNetwork,
    DailyMetrics,
    AnalyticsPeriod,
    KPISettings,
    Alert,
    AlertType,
)
from .alerts import AlertEngine, AnomalyDetector
from .graph1_cross_analytics import CrossAnalyticsReport
from .graph2_campaign_analytics import CampaignAnalyticsReport
from .data_generator import SampleDataGenerator

__version__ = "1.0.0"
__all__ = [
    "Campaign",
    "Source",
    "SocialNetwork",
    "DailyMetrics",
    "AnalyticsPeriod",
    "KPISettings",
    "Alert",
    "AlertType",
    "AlertEngine",
    "AnomalyDetector",
    "CrossAnalyticsReport",
    "CampaignAnalyticsReport",
    "SampleDataGenerator",
]
