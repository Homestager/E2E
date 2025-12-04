"""
Система обнаружения аномалий и генерации алертов
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
from ..models.data_models import Campaign, Source, DailyMetrics, AnalyticsPeriod


@dataclass
class Alert:
    """Алерт об аномалии"""
    emoji: str
    message: str
    severity: str  # 'critical', 'warning', 'info'
    timestamp: datetime
    metric: str  # 'romi', 'cpl', 'cr_cs', etc.
    entity_type: str  # 'campaign', 'source', 'social'
    entity_id: Optional[int] = None


class AnomalyDetector:
    """Детектор аномалий"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
    
    def calculate_moving_average(self, values: List[float], window: int = 7) -> List[float]:
        """Рассчитать скользящее среднее"""
        if len(values) < window:
            return values
        
        ma = []
        for i in range(len(values)):
            if i < window - 1:
                ma.append(sum(values[:i+1]) / (i+1))
            else:
                ma.append(sum(values[i-window+1:i+1]) / window)
        return ma
    
    def calculate_z_score(self, value: float, values: List[float]) -> float:
        """Рассчитать Z-score"""
        if len(values) < 2:
            return 0.0
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        if stdev == 0:
            return 0.0
        return (value - mean) / stdev
    
    def detect_romi_drop(self, metrics: List[DailyMetrics], threshold: float = 0.7) -> Optional[Alert]:
        """Обнаружить резкое падение ROMI"""
        if len(metrics) < 7:
            return None
        
        recent_romi = [m.romi for m in metrics[-7:] if m.spend > 0]
        if len(recent_romi) < 2:
            return None
        
        ma7 = statistics.mean(recent_romi[:-1]) if len(recent_romi) > 1 else recent_romi[0]
        current = recent_romi[-1]
        
        if ma7 > 0 and current < ma7 * threshold:
            drop_percent = ((ma7 - current) / ma7) * 100
            return Alert(
                emoji="🔥",
                message=f"ROMI упал на {drop_percent:.0f}% за последние дни",
                severity="critical",
                timestamp=datetime.now(),
                metric="romi",
                entity_type="general"
            )
        return None
    
    def detect_romi_spike(self, metrics: List[DailyMetrics], threshold: float = 1.5) -> Optional[Alert]:
        """Обнаружить резкий рост ROMI"""
        if len(metrics) < 7:
            return None
        
        recent_romi = [m.romi for m in metrics[-7:] if m.spend > 0]
        if len(recent_romi) < 2:
            return None
        
        ma7 = statistics.mean(recent_romi[:-1]) if len(recent_romi) > 1 else recent_romi[0]
        current = recent_romi[-1]
        
        if ma7 > 0 and current > ma7 * threshold:
            growth_percent = ((current - ma7) / ma7) * 100
            return Alert(
                emoji="🚀",
                message=f"ROMI вырос на {growth_percent:.0f}% - отличный результат!",
                severity="info",
                timestamp=datetime.now(),
                metric="romi",
                entity_type="general"
            )
        return None
    
    def detect_source_died(self, source: Source) -> Optional[Alert]:
        """Обнаружить, что источник перестал приносить трафик"""
        if len(source.daily_metrics) < 3:
            return None
        
        recent_leads = sum(m.leads for m in source.daily_metrics[-3:])
        if recent_leads == 0:
            return Alert(
                emoji="🚫",
                message=f"Источник {source.name} перестал приносить трафик (0 лидов за 3 дня)",
                severity="critical",
                timestamp=datetime.now(),
                metric="leads",
                entity_type="source",
                entity_id=source.rid
            )
        return None
    
    def detect_cpl_growth(self, metrics: List[DailyMetrics], threshold: float = 1.4) -> Optional[Alert]:
        """Обнаружить рост CPL"""
        if len(metrics) < 7:
            return None
        
        recent_cpl = [m.cpl for m in metrics[-7:] if m.leads > 0]
        if len(recent_cpl) < 2:
            return None
        
        ma7 = statistics.mean(recent_cpl[:-1]) if len(recent_cpl) > 1 else recent_cpl[0]
        current = recent_cpl[-1]
        
        if ma7 > 0 and current > ma7 * threshold:
            growth_percent = ((current - ma7) / ma7) * 100
            return Alert(
                emoji="⚠️",
                message=f"CPL вырос на {growth_percent:.0f}% за неделю",
                severity="warning",
                timestamp=datetime.now(),
                metric="cpl",
                entity_type="general"
            )
        return None
    
    def detect_cr_drop(self, metrics: List[DailyMetrics], threshold: float = 0.5) -> Optional[Alert]:
        """Обнаружить падение конверсии"""
        if len(metrics) < 7:
            return None
        
        recent_cr = [m.cr_c_s for m in metrics[-7:] if m.clicks > 0]
        if len(recent_cr) < 2:
            return None
        
        ma7 = statistics.mean(recent_cr[:-1]) if len(recent_cr) > 1 else recent_cr[0]
        current = recent_cr[-1]
        
        if ma7 > 0 and current < ma7 * threshold:
            drop_percent = ((ma7 - current) / ma7) * 100
            return Alert(
                emoji="📉",
                message=f"CR(C→S) упала на {drop_percent:.0f}%",
                severity="warning",
                timestamp=datetime.now(),
                metric="cr_cs",
                entity_type="general"
            )
        return None
    
    def detect_budget_stale(self, metrics: List[DailyMetrics], days: int = 6) -> Optional[Alert]:
        """Обнаружить, что бюджет не обновлялся"""
        if len(metrics) < days:
            return None
        
        recent_spend = sum(m.spend for m in metrics[-days:])
        if recent_spend == 0:
            return Alert(
                emoji="💤",
                message=f"Бюджет не обновлялся {days} дней",
                severity="warning",
                timestamp=datetime.now(),
                metric="spend",
                entity_type="general"
            )
        return None
    
    def detect_romi_below_kpi(self, campaign: Campaign) -> Optional[Alert]:
        """Обнаружить ROMI ниже KPI"""
        if campaign.kpi_romi_negative is None:
            return None
        
        if campaign.avg_romi < campaign.kpi_romi_negative:
            return Alert(
                emoji="⚠️",
                message=f"ROMI кампании {campaign.name} ниже KPI ({campaign.avg_romi:.0f}% < {campaign.kpi_romi_negative:.0f}%)",
                severity="critical",
                timestamp=datetime.now(),
                metric="romi",
                entity_type="campaign",
                entity_id=campaign.campaign_id
            )
        return None
    
    def detect_no_sales_after_launch(self, source: Source, days_threshold: int = 3) -> Optional[Alert]:
        """Обнаружить отсутствие продаж после запуска источника"""
        if source.start_date is None or len(source.daily_metrics) < days_threshold:
            return None
        
        days_since_launch = (datetime.now() - source.start_date).days
        if days_since_launch >= days_threshold and source.total_sales == 0:
            return Alert(
                emoji="🤔",
                message=f"Источник {source.name} запущен {days_since_launch} дней назад, но продаж нет",
                severity="warning",
                timestamp=datetime.now(),
                metric="sales",
                entity_type="source",
                entity_id=source.rid
            )
        return None
    
    def detect_spike_correlation(self, source: Source, all_metrics: List[DailyMetrics]) -> Optional[Alert]:
        """Обнаружить корреляцию пика продаж с запуском источника"""
        if source.start_date is None or len(all_metrics) < 3:
            return None
        
        # Найти метрики в день запуска и следующие дни
        launch_date = source.start_date.date()
        metrics_after_launch = [m for m in all_metrics if m.date.date() >= launch_date][:3]
        
        if len(metrics_after_launch) < 2:
            return None
        
        # Средние продажи до запуска
        metrics_before = [m for m in all_metrics if m.date.date() < launch_date]
        if len(metrics_before) < 3:
            return None
        
        avg_before = statistics.mean([m.sales for m in metrics_before[-7:]])
        sales_after = sum(m.sales for m in metrics_after_launch)
        
        if sales_after > avg_before * 1.5:
            return Alert(
                emoji="🎯",
                message=f"Резкий пик продаж связан со стартом {source.name}",
                severity="info",
                timestamp=datetime.now(),
                metric="sales",
                entity_type="source",
                entity_id=source.rid
            )
        return None
    
    def analyze_campaign(self, campaign: Campaign) -> List[Alert]:
        """Проанализировать кампанию и вернуть все алерты"""
        alerts = []
        
        # Собрать все метрики кампании
        all_metrics = []
        for source in campaign.sources:
            all_metrics.extend(source.daily_metrics)
        
        if all_metrics:
            all_metrics.sort(key=lambda m: m.date)
            
            # Проверить различные аномалии
            alert = self.detect_romi_drop(all_metrics)
            if alert:
                alerts.append(alert)
            
            alert = self.detect_cpl_growth(all_metrics)
            if alert:
                alerts.append(alert)
            
            alert = self.detect_cr_drop(all_metrics)
            if alert:
                alerts.append(alert)
            
            alert = self.detect_budget_stale(all_metrics)
            if alert:
                alerts.append(alert)
        
        # Проверить ROMI относительно KPI
        alert = self.detect_romi_below_kpi(campaign)
        if alert:
            alerts.append(alert)
        
        # Проверить каждый источник
        for source in campaign.sources:
            alert = self.detect_source_died(source)
            if alert:
                alerts.append(alert)
            
            alert = self.detect_no_sales_after_launch(source)
            if alert:
                alerts.append(alert)
            
            alert = self.detect_spike_correlation(source, all_metrics)
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def analyze_period(self, period: AnalyticsPeriod) -> List[Alert]:
        """Проанализировать весь период"""
        alerts = []
        
        for campaign in period.campaigns:
            alerts.extend(self.analyze_campaign(campaign))
        
        # Проверить, есть ли кампании без KPI
        campaigns_without_kpi = [c for c in period.campaigns 
                                if c.kpi_romi_positive is None or c.kpi_cpl_positive is None]
        
        if campaigns_without_kpi:
            alerts.append(Alert(
                emoji="🎯",
                message=f"Не заданы KPI для {len(campaigns_without_kpi)} кампаний",
                severity="info",
                timestamp=datetime.now(),
                metric="kpi",
                entity_type="campaign"
            ))
        
        return alerts
