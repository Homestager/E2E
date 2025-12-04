"""
Data models for Marketing Analytics

Contains all data structures for campaigns, sources, metrics, and alerts.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict
from enum import Enum


class AlertType(Enum):
    """Types of alerts for anomaly detection"""
    CPL_SPIKE = "cpl_spike"
    ROMI_DROP = "romi_drop"
    ROMI_BELOW_KPI = "romi_below_kpi"
    ROMI_ABOVE_KPI = "romi_above_kpi"
    BUDGET_STALE = "budget_stale"
    SOURCE_NO_TRAFFIC = "source_no_traffic"
    KPI_NOT_SET = "kpi_not_set"
    REVENUE_SPIKE = "revenue_spike"
    REVENUE_DROP = "revenue_drop"
    CR_DROP = "cr_drop"
    CR_SPIKE = "cr_spike"
    SOURCE_OVERHEATED = "source_overheated"
    SOURCE_INEFFECTIVE = "source_ineffective"
    CAMPAIGN_LAUNCHED = "campaign_launched"
    NO_SALES_AFTER_LAUNCH = "no_sales_after_launch"
    LEADS_DROP = "leads_drop"
    FUNNEL_ISSUE = "funnel_issue"


class SocialNetwork(Enum):
    """Supported social networks"""
    INSTAGRAM = "Instagram"
    TELEGRAM = "Telegram"
    YOUTUBE = "YouTube"
    VK = "VK"
    FACEBOOK = "Facebook"
    TIKTOK = "TikTok"
    TWITTER = "Twitter"
    OTHER = "Other"


@dataclass
class KPISettings:
    """KPI settings for campaign or source"""
    romi_positive: float = 1200.0  # Target ROMI (positive threshold)
    romi_negative: float = 700.0   # Minimum acceptable ROMI
    cpl_positive: Optional[float] = None  # Target CPL
    cpl_negative: Optional[float] = None  # Maximum acceptable CPL
    cac_positive: Optional[float] = None  # Target CAC
    cac_negative: Optional[float] = None  # Maximum acceptable CAC


@dataclass
class DailyMetrics:
    """Daily metrics for a source/campaign"""
    date: date
    clicks: int = 0
    leads: int = 0
    sales: int = 0
    revenue: float = 0.0
    spend: float = 0.0
    refunds: int = 0
    refund_amount: float = 0.0
    
    @property
    def cpl(self) -> float:
        """Cost per lead"""
        return self.spend / self.leads if self.leads > 0 else 0.0
    
    @property
    def cac(self) -> float:
        """Cost per acquisition (customer)"""
        return self.spend / self.sales if self.sales > 0 else 0.0
    
    @property
    def cpa(self) -> float:
        """Cost per action (click)"""
        return self.spend / self.clicks if self.clicks > 0 else 0.0
    
    @property
    def romi(self) -> float:
        """Return on marketing investment (%)"""
        if self.spend <= 0:
            return 0.0
        return ((self.revenue - self.spend) / self.spend) * 100
    
    @property
    def cr_cl(self) -> float:
        """Conversion rate: Click to Lead (%)"""
        return (self.leads / self.clicks * 100) if self.clicks > 0 else 0.0
    
    @property
    def cr_ls(self) -> float:
        """Conversion rate: Lead to Sale (%)"""
        return (self.sales / self.leads * 100) if self.leads > 0 else 0.0
    
    @property
    def cr_cs(self) -> float:
        """Conversion rate: Click to Sale (%)"""
        return (self.sales / self.clicks * 100) if self.clicks > 0 else 0.0
    
    @property
    def ltv(self) -> float:
        """Lifetime value (average revenue per customer)"""
        return self.revenue / self.sales if self.sales > 0 else 0.0


@dataclass
class Source:
    """
    Traffic source (RID) - e.g., specific influencer, ad placement, etc.
    """
    rid: str  # Unique identifier
    name: str
    campaign_id: str
    social_network: SocialNetwork
    created_at: date
    ad_start_date: Optional[date] = None  # When advertising started
    daily_metrics: List[DailyMetrics] = field(default_factory=list)
    kpi: KPISettings = field(default_factory=KPISettings)
    is_active: bool = True
    
    @property
    def total_clicks(self) -> int:
        return sum(m.clicks for m in self.daily_metrics)
    
    @property
    def total_leads(self) -> int:
        return sum(m.leads for m in self.daily_metrics)
    
    @property
    def total_sales(self) -> int:
        return sum(m.sales for m in self.daily_metrics)
    
    @property
    def total_revenue(self) -> float:
        return sum(m.revenue for m in self.daily_metrics)
    
    @property
    def total_spend(self) -> float:
        return sum(m.spend for m in self.daily_metrics)
    
    @property
    def overall_romi(self) -> float:
        if self.total_spend <= 0:
            return 0.0
        return ((self.total_revenue - self.total_spend) / self.total_spend) * 100
    
    @property
    def overall_cpl(self) -> float:
        return self.total_spend / self.total_leads if self.total_leads > 0 else 0.0
    
    @property
    def overall_cac(self) -> float:
        return self.total_spend / self.total_sales if self.total_sales > 0 else 0.0
    
    @property
    def overall_ltv(self) -> float:
        return self.total_revenue / self.total_sales if self.total_sales > 0 else 0.0
    
    @property
    def overall_cr_cl(self) -> float:
        return (self.total_leads / self.total_clicks * 100) if self.total_clicks > 0 else 0.0
    
    @property
    def overall_cr_ls(self) -> float:
        return (self.total_sales / self.total_leads * 100) if self.total_leads > 0 else 0.0
    
    @property
    def overall_cr_cs(self) -> float:
        return (self.total_sales / self.total_clicks * 100) if self.total_clicks > 0 else 0.0
    
    def get_first_click_date(self) -> Optional[date]:
        """Get date of first click (fallback for ad_start_date)"""
        for m in sorted(self.daily_metrics, key=lambda x: x.date):
            if m.clicks > 0:
                return m.date
        return None
    
    def get_effective_start_date(self) -> Optional[date]:
        """Get effective advertising start date"""
        return self.ad_start_date or self.get_first_click_date()


@dataclass
class Campaign:
    """
    Marketing campaign containing multiple sources
    """
    id: str
    name: str
    created_at: date
    sources: List[Source] = field(default_factory=list)
    kpi: KPISettings = field(default_factory=KPISettings)
    is_active: bool = True
    
    @property
    def total_clicks(self) -> int:
        return sum(s.total_clicks for s in self.sources)
    
    @property
    def total_leads(self) -> int:
        return sum(s.total_leads for s in self.sources)
    
    @property
    def total_sales(self) -> int:
        return sum(s.total_sales for s in self.sources)
    
    @property
    def total_revenue(self) -> float:
        return sum(s.total_revenue for s in self.sources)
    
    @property
    def total_spend(self) -> float:
        return sum(s.total_spend for s in self.sources)
    
    @property
    def overall_romi(self) -> float:
        if self.total_spend <= 0:
            return 0.0
        return ((self.total_revenue - self.total_spend) / self.total_spend) * 100
    
    @property
    def overall_cpl(self) -> float:
        return self.total_spend / self.total_leads if self.total_leads > 0 else 0.0
    
    @property
    def overall_cac(self) -> float:
        return self.total_spend / self.total_sales if self.total_sales > 0 else 0.0
    
    @property
    def overall_ltv(self) -> float:
        return self.total_revenue / self.total_sales if self.total_sales > 0 else 0.0
    
    @property
    def overall_cr_cl(self) -> float:
        return (self.total_leads / self.total_clicks * 100) if self.total_clicks > 0 else 0.0
    
    @property
    def overall_cr_ls(self) -> float:
        return (self.total_sales / self.total_leads * 100) if self.total_leads > 0 else 0.0
    
    @property
    def overall_cr_cs(self) -> float:
        return (self.total_sales / self.total_clicks * 100) if self.total_clicks > 0 else 0.0
    
    def get_sources_by_social_network(self, sn: SocialNetwork) -> List[Source]:
        """Get all sources from specific social network"""
        return [s for s in self.sources if s.social_network == sn]
    
    def get_daily_aggregated_metrics(self) -> Dict[date, DailyMetrics]:
        """Aggregate all sources metrics by day"""
        daily_data: Dict[date, DailyMetrics] = {}
        
        for source in self.sources:
            for m in source.daily_metrics:
                if m.date not in daily_data:
                    daily_data[m.date] = DailyMetrics(date=m.date)
                
                dm = daily_data[m.date]
                dm.clicks += m.clicks
                dm.leads += m.leads
                dm.sales += m.sales
                dm.revenue += m.revenue
                dm.spend += m.spend
                dm.refunds += m.refunds
                dm.refund_amount += m.refund_amount
        
        return daily_data
    
    def get_top_sources(self, n: int = 3, by: str = "romi") -> List[Source]:
        """Get top N sources by metric"""
        if by == "romi":
            return sorted(self.sources, key=lambda s: s.overall_romi, reverse=True)[:n]
        elif by == "revenue":
            return sorted(self.sources, key=lambda s: s.total_revenue, reverse=True)[:n]
        elif by == "cpl":
            return sorted(self.sources, key=lambda s: s.overall_cpl if s.overall_cpl > 0 else float('inf'))[:n]
        return self.sources[:n]
    
    def get_worst_sources(self, n: int = 3, by: str = "romi") -> List[Source]:
        """Get worst N sources by metric"""
        if by == "romi":
            return sorted(self.sources, key=lambda s: s.overall_romi)[:n]
        elif by == "revenue":
            return sorted(self.sources, key=lambda s: s.total_revenue)[:n]
        return self.sources[:n]


@dataclass
class Alert:
    """Alert/notification about anomaly or important event"""
    type: AlertType
    severity: str  # "info", "warning", "critical"
    message: str
    message_ru: str  # Russian message
    source_id: Optional[str] = None
    campaign_id: Optional[str] = None
    date: Optional[date] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    change_percent: Optional[float] = None
    
    @property
    def emoji(self) -> str:
        """Get emoji for alert type"""
        emoji_map = {
            AlertType.CPL_SPIKE: "🔥",
            AlertType.ROMI_DROP: "⚠️",
            AlertType.ROMI_BELOW_KPI: "⚠️",
            AlertType.ROMI_ABOVE_KPI: "🎯",
            AlertType.BUDGET_STALE: "💤",
            AlertType.SOURCE_NO_TRAFFIC: "🚫",
            AlertType.KPI_NOT_SET: "🎯",
            AlertType.REVENUE_SPIKE: "📈",
            AlertType.REVENUE_DROP: "📉",
            AlertType.CR_DROP: "📉",
            AlertType.CR_SPIKE: "📈",
            AlertType.SOURCE_OVERHEATED: "🔥",
            AlertType.SOURCE_INEFFECTIVE: "❌",
            AlertType.CAMPAIGN_LAUNCHED: "🚀",
            AlertType.NO_SALES_AFTER_LAUNCH: "⚠️",
            AlertType.LEADS_DROP: "📉",
            AlertType.FUNNEL_ISSUE: "🔧",
        }
        return emoji_map.get(self.type, "ℹ️")


@dataclass
class PeriodComparison:
    """Comparison between two periods"""
    metric_name: str
    current_value: float
    previous_value: float
    
    @property
    def change_percent(self) -> float:
        if self.previous_value == 0:
            return 0.0 if self.current_value == 0 else 100.0
        return ((self.current_value - self.previous_value) / self.previous_value) * 100
    
    @property
    def is_positive(self) -> bool:
        """Check if change is positive (depends on metric)"""
        # For CPL - decrease is positive
        if "cpl" in self.metric_name.lower() or "cac" in self.metric_name.lower():
            return self.change_percent < 0
        # For everything else - increase is positive
        return self.change_percent > 0
    
    @property
    def formatted(self) -> str:
        sign = "+" if self.change_percent >= 0 else ""
        warning = " ⚠️" if abs(self.change_percent) > 30 and not self.is_positive else ""
        return f"{sign}{self.change_percent:.1f}%{warning}"


@dataclass
class AnalyticsPeriod:
    """Period for analytics report"""
    start_date: date
    end_date: date
    campaigns: List[Campaign] = field(default_factory=list)
    
    @property
    def days(self) -> int:
        return (self.end_date - self.start_date).days + 1
    
    def get_all_sources(self) -> List[Source]:
        """Get all sources across all campaigns"""
        sources = []
        for campaign in self.campaigns:
            sources.extend(campaign.sources)
        return sources
    
    def get_total_revenue(self) -> float:
        return sum(c.total_revenue for c in self.campaigns)
    
    def get_total_spend(self) -> float:
        return sum(c.total_spend for c in self.campaigns)
    
    def get_total_leads(self) -> int:
        return sum(c.total_leads for c in self.campaigns)
    
    def get_total_sales(self) -> int:
        return sum(c.total_sales for c in self.campaigns)
    
    def get_total_clicks(self) -> int:
        return sum(c.total_clicks for c in self.campaigns)
    
    def get_overall_romi(self) -> float:
        total_spend = self.get_total_spend()
        if total_spend <= 0:
            return 0.0
        return ((self.get_total_revenue() - total_spend) / total_spend) * 100
    
    def get_overall_cpl(self) -> float:
        total_leads = self.get_total_leads()
        if total_leads <= 0:
            return 0.0
        return self.get_total_spend() / total_leads
    
    def get_overall_ltv(self) -> float:
        total_sales = self.get_total_sales()
        if total_sales <= 0:
            return 0.0
        return self.get_total_revenue() / total_sales
    
    def get_campaigns_by_romi(self, descending: bool = True) -> List[Campaign]:
        """Get campaigns sorted by ROMI"""
        return sorted(self.campaigns, key=lambda c: c.overall_romi, reverse=descending)
    
    def get_revenue_by_social_network(self) -> Dict[SocialNetwork, float]:
        """Get revenue breakdown by social network"""
        result: Dict[SocialNetwork, float] = {}
        for campaign in self.campaigns:
            for source in campaign.sources:
                sn = source.social_network
                if sn not in result:
                    result[sn] = 0.0
                result[sn] += source.total_revenue
        return result
    
    def get_spend_by_social_network(self) -> Dict[SocialNetwork, float]:
        """Get spend breakdown by social network"""
        result: Dict[SocialNetwork, float] = {}
        for campaign in self.campaigns:
            for source in campaign.sources:
                sn = source.social_network
                if sn not in result:
                    result[sn] = 0.0
                result[sn] += source.total_spend
        return result
