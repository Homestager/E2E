"""
Модели данных для аналитической системы
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class SocialNetwork(str, Enum):
    """Социальные сети"""
    INSTAGRAM = "Instagram"
    TELEGRAM = "Telegram"
    YOUTUBE = "YouTube"
    VK = "VK"
    FACEBOOK = "Facebook"
    TIKTOK = "TikTok"


@dataclass
class DailyMetrics:
    """Метрики за день"""
    date: datetime
    clicks: int = 0
    leads: int = 0
    sales: int = 0
    revenue: float = 0.0
    spend: float = 0.0
    refunds: int = 0
    
    @property
    def romi(self) -> float:
        """Return on Marketing Investment"""
        if self.spend == 0:
            return 0.0
        return ((self.revenue - self.spend) / self.spend) * 100
    
    @property
    def cpl(self) -> float:
        """Cost Per Lead"""
        if self.leads == 0:
            return 0.0
        return self.spend / self.leads
    
    @property
    def cac(self) -> float:
        """Customer Acquisition Cost"""
        if self.sales == 0:
            return 0.0
        return self.spend / self.sales
    
    @property
    def cpa(self) -> float:
        """Cost Per Action (Click)"""
        if self.clicks == 0:
            return 0.0
        return self.spend / self.clicks
    
    @property
    def cr_c_l(self) -> float:
        """Conversion Rate: Clicks to Leads"""
        if self.clicks == 0:
            return 0.0
        return (self.leads / self.clicks) * 100
    
    @property
    def cr_l_s(self) -> float:
        """Conversion Rate: Leads to Sales"""
        if self.leads == 0:
            return 0.0
        return (self.sales / self.leads) * 100
    
    @property
    def cr_c_s(self) -> float:
        """Conversion Rate: Clicks to Sales"""
        if self.clicks == 0:
            return 0.0
        return (self.sales / self.clicks) * 100


@dataclass
class Source:
    """Источник трафика (RID)"""
    rid: int
    name: str
    social_network: SocialNetwork
    campaign_id: int
    start_date: Optional[datetime] = None
    daily_metrics: List[DailyMetrics] = field(default_factory=list)
    
    @property
    def total_revenue(self) -> float:
        return sum(m.revenue for m in self.daily_metrics)
    
    @property
    def total_spend(self) -> float:
        return sum(m.spend for m in self.daily_metrics)
    
    @property
    def total_leads(self) -> int:
        return sum(m.leads for m in self.daily_metrics)
    
    @property
    def total_sales(self) -> int:
        return sum(m.sales for m in self.daily_metrics)
    
    @property
    def total_clicks(self) -> int:
        return sum(m.clicks for m in self.daily_metrics)
    
    @property
    def avg_romi(self) -> float:
        if self.total_spend == 0:
            return 0.0
        return ((self.total_revenue - self.total_spend) / self.total_spend) * 100
    
    @property
    def avg_cpl(self) -> float:
        if self.total_leads == 0:
            return 0.0
        return self.total_spend / self.total_leads
    
    @property
    def avg_cac(self) -> float:
        if self.total_sales == 0:
            return 0.0
        return self.total_spend / self.total_sales
    
    @property
    def avg_cpa(self) -> float:
        if self.total_clicks == 0:
            return 0.0
        return self.total_spend / self.total_clicks
    
    @property
    def avg_ltv(self) -> float:
        """Average Lifetime Value"""
        if self.total_sales == 0:
            return 0.0
        return self.total_revenue / self.total_sales


@dataclass
class Campaign:
    """Рекламная кампания"""
    campaign_id: int
    name: str
    created_date: datetime
    sources: List[Source] = field(default_factory=list)
    kpi_romi_positive: Optional[float] = 1200.0  # по умолчанию 1200%
    kpi_romi_negative: Optional[float] = 700.0   # по умолчанию 700%
    kpi_cpl_positive: Optional[float] = None
    kpi_cpl_negative: Optional[float] = None
    
    @property
    def total_revenue(self) -> float:
        return sum(s.total_revenue for s in self.sources)
    
    @property
    def total_spend(self) -> float:
        return sum(s.total_spend for s in self.sources)
    
    @property
    def total_leads(self) -> int:
        return sum(s.total_leads for s in self.sources)
    
    @property
    def total_sales(self) -> int:
        return sum(s.total_sales for s in self.sources)
    
    @property
    def total_clicks(self) -> int:
        return sum(s.total_clicks for s in self.sources)
    
    @property
    def avg_romi(self) -> float:
        if self.total_spend == 0:
            return 0.0
        return ((self.total_revenue - self.total_spend) / self.total_spend) * 100
    
    @property
    def avg_cpl(self) -> float:
        if self.total_leads == 0:
            return 0.0
        return self.total_spend / self.total_leads
    
    @property
    def avg_ltv(self) -> float:
        if self.total_sales == 0:
            return 0.0
        return self.total_revenue / self.total_sales
    
    @property
    def cr_c_l(self) -> float:
        if self.total_clicks == 0:
            return 0.0
        return (self.total_leads / self.total_clicks) * 100
    
    @property
    def cr_l_s(self) -> float:
        if self.total_leads == 0:
            return 0.0
        return (self.total_sales / self.total_leads) * 100
    
    @property
    def cr_c_s(self) -> float:
        if self.total_clicks == 0:
            return 0.0
        return (self.total_sales / self.total_clicks) * 100
    
    def get_sources_by_social(self, social: SocialNetwork) -> List[Source]:
        """Получить источники по социальной сети"""
        return [s for s in self.sources if s.social_network == social]
    
    def get_top_sources(self, n: int = 3, by: str = "romi") -> List[Source]:
        """Получить топ-N источников"""
        if by == "romi":
            return sorted(self.sources, key=lambda s: s.avg_romi, reverse=True)[:n]
        elif by == "revenue":
            return sorted(self.sources, key=lambda s: s.total_revenue, reverse=True)[:n]
        return self.sources[:n]
    
    def get_worst_sources(self, n: int = 3, by: str = "romi") -> List[Source]:
        """Получить худшие источники"""
        if by == "romi":
            return sorted(self.sources, key=lambda s: s.avg_romi)[:n]
        elif by == "revenue":
            return sorted(self.sources, key=lambda s: s.total_revenue)[:n]
        return self.sources[:n]


@dataclass
class AnalyticsPeriod:
    """Период аналитики"""
    start_date: datetime
    end_date: datetime
    campaigns: List[Campaign] = field(default_factory=list)
    
    @property
    def total_revenue(self) -> float:
        return sum(c.total_revenue for c in self.campaigns)
    
    @property
    def total_spend(self) -> float:
        return sum(c.total_spend for c in self.campaigns)
    
    @property
    def total_leads(self) -> int:
        return sum(c.total_leads for c in self.campaigns)
    
    @property
    def total_sales(self) -> int:
        return sum(c.total_sales for c in self.campaigns)
    
    @property
    def total_clicks(self) -> int:
        return sum(c.total_clicks for c in self.campaigns)
    
    @property
    def avg_romi(self) -> float:
        if self.total_spend == 0:
            return 0.0
        return ((self.total_revenue - self.total_spend) / self.total_spend) * 100
    
    @property
    def avg_cpl(self) -> float:
        if self.total_leads == 0:
            return 0.0
        return self.total_spend / self.total_leads
    
    def get_revenue_by_social(self) -> Dict[SocialNetwork, float]:
        """Получить выручку по соцсетям"""
        result = {}
        for campaign in self.campaigns:
            for source in campaign.sources:
                if source.social_network not in result:
                    result[source.social_network] = 0.0
                result[source.social_network] += source.total_revenue
        return result
    
    def get_spend_by_social(self) -> Dict[SocialNetwork, float]:
        """Получить расходы по соцсетям"""
        result = {}
        for campaign in self.campaigns:
            for source in campaign.sources:
                if source.social_network not in result:
                    result[source.social_network] = 0.0
                result[source.social_network] += source.total_spend
        return result
