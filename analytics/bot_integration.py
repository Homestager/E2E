"""
Bot Integration Module

Provides high-level API for Telegram bot integration.
Handles PNG generation and text formatting for bot messages.
"""

import os
from datetime import date, timedelta
from typing import List, Optional, Tuple, Dict, Any
from io import BytesIO

from .models import (
    Campaign,
    Source,
    AnalyticsPeriod,
    SocialNetwork,
    Alert,
    KPISettings,
)
from .alerts import AlertEngine
from .graph1_cross_analytics import CrossAnalyticsReport
from .graph2_campaign_analytics import CampaignAnalyticsReport


class MarketingAnalyticsBot:
    """
    High-level interface for Telegram bot integration.
    
    Usage:
        bot = MarketingAnalyticsBot(period)
        
        # Get Graph 1 (Cross Analytics)
        png_bytes = bot.generate_graph1()
        
        # Get Graph 2 (Campaign Analytics)
        png_bytes = bot.generate_graph2(campaign_id)
        
        # Get campaign list for buttons
        campaigns = bot.get_campaign_list()
        
        # Get campaign card text
        card_text = bot.get_campaign_card(campaign_id)
    """
    
    def __init__(self, period: AnalyticsPeriod, output_dir: str = "./output"):
        """
        Initialize bot integration.
        
        Args:
            period: AnalyticsPeriod with all campaigns and data
            output_dir: Directory to save generated PNG files
        """
        self.period = period
        self.output_dir = output_dir
        self.alert_engine = AlertEngine()
        
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Index campaigns by ID
        self._campaigns_by_id: Dict[str, Campaign] = {
            c.id: c for c in period.campaigns
        }
        
        # Index sources by RID
        self._sources_by_rid: Dict[str, Tuple[Source, Campaign]] = {}
        for campaign in period.campaigns:
            for source in campaign.sources:
                self._sources_by_rid[source.rid] = (source, campaign)
    
    def generate_graph1(self, save_file: bool = True) -> bytes:
        """
        Generate Graph 1 - Cross Analytics report.
        
        Args:
            save_file: Whether to also save to file
            
        Returns:
            PNG image as bytes
        """
        report = CrossAnalyticsReport(self.period)
        
        output_path = None
        if save_file:
            output_path = os.path.join(self.output_dir, "graph1_cross_analytics.png")
        
        png_bytes = report.generate(output_path)
        
        return png_bytes
    
    def generate_graph2(self, campaign_id: str, save_file: bool = True) -> Optional[bytes]:
        """
        Generate Graph 2 - Campaign Analytics report.
        
        Args:
            campaign_id: Campaign ID to generate report for
            save_file: Whether to also save to file
            
        Returns:
            PNG image as bytes, or None if campaign not found
        """
        campaign = self._campaigns_by_id.get(campaign_id)
        if campaign is None:
            return None
        
        report = CampaignAnalyticsReport(campaign, self.period)
        
        output_path = None
        if save_file:
            output_path = os.path.join(
                self.output_dir, 
                f"graph2_campaign_{campaign_id}.png"
            )
        
        png_bytes = report.generate(output_path)
        
        return png_bytes
    
    def get_campaign_list(self) -> List[Dict[str, Any]]:
        """
        Get list of campaigns for button generation.
        
        Returns:
            List of dicts with campaign info:
            [
                {
                    "id": "1234",
                    "name": "BLACKFRIDAY_2025",
                    "leads": 123,
                    "sales": 45,
                    "revenue": 1230000,
                    "romi": 450,
                    "cpl": 240,
                    "cr_cs": 1.25,
                    "created_at": "2025-11-29",
                    "summary": "🎯 BLACKFRIDAY_2025\nID: 1234..."
                },
                ...
            ]
        """
        result = []
        
        for campaign in sorted(self.period.campaigns, key=lambda c: c.overall_romi, reverse=True):
            report = CrossAnalyticsReport(self.period)
            
            result.append({
                "id": campaign.id,
                "name": campaign.name,
                "leads": campaign.total_leads,
                "sales": campaign.total_sales,
                "revenue": campaign.total_revenue,
                "romi": campaign.overall_romi,
                "cpl": campaign.overall_cpl,
                "cr_cs": campaign.overall_cr_cs,
                "created_at": campaign.created_at.isoformat(),
                "summary": report.generate_summary_card(campaign)
            })
        
        return result
    
    def get_campaign_card(self, campaign_id: str) -> Optional[str]:
        """
        Get detailed campaign card text.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Formatted text card, or None if not found
        """
        campaign = self._campaigns_by_id.get(campaign_id)
        if campaign is None:
            return None
        
        report = CrossAnalyticsReport(self.period)
        return report.generate_campaign_card(campaign)
    
    def get_source_card(self, rid: str) -> Optional[str]:
        """
        Get detailed source card text.
        
        Args:
            rid: Source RID
            
        Returns:
            Formatted text card, or None if not found
        """
        source_info = self._sources_by_rid.get(rid)
        if source_info is None:
            return None
        
        source, campaign = source_info
        report = CampaignAnalyticsReport(campaign, self.period)
        return report.generate_source_card(source)
    
    def get_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get current alerts.
        
        Args:
            limit: Maximum number of alerts
            
        Returns:
            List of alert dicts
        """
        alerts = self.alert_engine.get_all_alerts(self.period)[:limit]
        
        return [
            {
                "type": alert.type.value,
                "severity": alert.severity,
                "emoji": alert.emoji,
                "message": alert.message,
                "message_ru": alert.message_ru,
                "source_id": alert.source_id,
                "campaign_id": alert.campaign_id,
                "value": alert.value,
                "threshold": alert.threshold,
                "change_percent": alert.change_percent,
            }
            for alert in alerts
        ]
    
    def get_alerts_text(self) -> str:
        """Get formatted alerts text for bot message."""
        return self.alert_engine.format_alerts_text(
            self.alert_engine.get_all_alerts(self.period)
        )
    
    def get_comparison_text(self, period_type: str = "week") -> str:
        """
        Get period comparison text.
        
        Args:
            period_type: "week" or "month"
        """
        comparisons = self.alert_engine.compare_periods(self.period, period_type)
        period_name = "неделя" if period_type == "week" else "месяц"
        return self.alert_engine.format_comparison_text(comparisons, period_name)
    
    def get_expert_comments(self, campaign_id: Optional[str] = None) -> List[str]:
        """
        Get expert comments about peaks and anomalies.
        
        Args:
            campaign_id: Optional specific campaign
        """
        campaign = self._campaigns_by_id.get(campaign_id) if campaign_id else None
        return self.alert_engine.get_expert_comments(self.period, campaign)
    
    def set_campaign_kpi(
        self,
        campaign_id: str,
        romi_positive: Optional[float] = None,
        romi_negative: Optional[float] = None,
        cpl_positive: Optional[float] = None,
        cpl_negative: Optional[float] = None
    ) -> bool:
        """
        Set KPI for a campaign.
        
        Returns:
            True if successful
        """
        campaign = self._campaigns_by_id.get(campaign_id)
        if campaign is None:
            return False
        
        if romi_positive is not None:
            campaign.kpi.romi_positive = romi_positive
        if romi_negative is not None:
            campaign.kpi.romi_negative = romi_negative
        if cpl_positive is not None:
            campaign.kpi.cpl_positive = cpl_positive
        if cpl_negative is not None:
            campaign.kpi.cpl_negative = cpl_negative
        
        return True
    
    def set_source_kpi(
        self,
        rid: str,
        romi_positive: Optional[float] = None,
        romi_negative: Optional[float] = None
    ) -> bool:
        """
        Set KPI for a source.
        
        Returns:
            True if successful
        """
        source_info = self._sources_by_rid.get(rid)
        if source_info is None:
            return False
        
        source, _ = source_info
        
        if romi_positive is not None:
            source.kpi.romi_positive = romi_positive
        if romi_negative is not None:
            source.kpi.romi_negative = romi_negative
        
        return True
    
    def get_cross_analytics_summary(self) -> str:
        """
        Get text summary for cross analytics button.
        """
        from .chart_utils import format_currency, format_percent, format_number
        
        total_revenue = self.period.get_total_revenue()
        total_spend = self.period.get_total_spend()
        total_leads = self.period.get_total_leads()
        total_sales = self.period.get_total_sales()
        overall_romi = self.period.get_overall_romi()
        overall_cpl = self.period.get_overall_cpl()
        overall_ltv = self.period.get_overall_ltv()
        
        return f"""📊 СКВОЗНАЯ АНАЛИТИКА

📅 Период: {self.period.start_date.strftime('%d.%m.%Y')} - {self.period.end_date.strftime('%d.%m.%Y')}
📈 Кампаний: {len(self.period.campaigns)}

💰 Итоги:
• Выручка: {format_currency(total_revenue)}
• Расходы: {format_currency(total_spend)}
• ROMI: {format_percent(overall_romi)}
• CPL: {format_currency(overall_cpl)}
• LTV: {format_currency(overall_ltv)}

📊 Воронка:
• Лиды: {format_number(total_leads)}
• Продажи: {format_number(total_sales)}
• CR(C→S): {format_percent(self.period.get_total_sales() / self.period.get_total_clicks() * 100 if self.period.get_total_clicks() > 0 else 0)}

{self.get_alerts_text()}

{self.get_comparison_text('week')}

📁 Полный отчет: /analytics_graph1
"""
