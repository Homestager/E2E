"""
Alert Engine and Anomaly Detection

Implements all anomaly detection rules for marketing analytics.
"""

from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import statistics

from .models import (
    Campaign,
    Source,
    DailyMetrics,
    AnalyticsPeriod,
    Alert,
    AlertType,
    PeriodComparison,
    SocialNetwork,
)


@dataclass
class MovingAverages:
    """7-day moving averages for metrics"""
    romi_ma7: float = 0.0
    cpl_ma7: float = 0.0
    cac_ma7: float = 0.0
    revenue_ma7: float = 0.0
    spend_ma7: float = 0.0
    leads_ma7: float = 0.0
    sales_ma7: float = 0.0
    clicks_ma7: float = 0.0
    cr_cl_ma7: float = 0.0
    cr_ls_ma7: float = 0.0
    cr_cs_ma7: float = 0.0


class AnomalyDetector:
    """
    Detects anomalies in marketing metrics based on predefined rules.
    """
    
    def __init__(
        self,
        romi_drop_threshold: float = 0.7,  # 30% drop
        romi_spike_threshold: float = 1.5,  # 50% increase
        cpl_spike_threshold: float = 1.4,   # 40% increase
        revenue_spike_threshold: float = 1.8,
        revenue_drop_threshold: float = 0.5,
        cr_drop_threshold: float = 0.5,
        cr_spike_threshold: float = 2.0,
        no_leads_days: int = 3,
        no_sales_days: int = 3,
        zscore_threshold: float = 2.5,
    ):
        self.romi_drop_threshold = romi_drop_threshold
        self.romi_spike_threshold = romi_spike_threshold
        self.cpl_spike_threshold = cpl_spike_threshold
        self.revenue_spike_threshold = revenue_spike_threshold
        self.revenue_drop_threshold = revenue_drop_threshold
        self.cr_drop_threshold = cr_drop_threshold
        self.cr_spike_threshold = cr_spike_threshold
        self.no_leads_days = no_leads_days
        self.no_sales_days = no_sales_days
        self.zscore_threshold = zscore_threshold
    
    def calculate_ma7(self, values: List[float]) -> float:
        """Calculate 7-day moving average"""
        if not values:
            return 0.0
        last_7 = values[-7:] if len(values) >= 7 else values
        return statistics.mean(last_7) if last_7 else 0.0
    
    def calculate_zscore(self, value: float, values: List[float]) -> float:
        """Calculate z-score for anomaly detection"""
        if len(values) < 2:
            return 0.0
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0.0
        if stdev == 0:
            return 0.0
        return (value - mean) / stdev
    
    def get_moving_averages(self, daily_metrics: List[DailyMetrics]) -> MovingAverages:
        """Calculate 7-day moving averages for all metrics"""
        if not daily_metrics:
            return MovingAverages()
        
        sorted_metrics = sorted(daily_metrics, key=lambda m: m.date)
        
        # Calculate individual metric lists
        revenues = [m.revenue for m in sorted_metrics]
        spends = [m.spend for m in sorted_metrics]
        leads = [float(m.leads) for m in sorted_metrics]
        sales = [float(m.sales) for m in sorted_metrics]
        clicks = [float(m.clicks) for m in sorted_metrics]
        
        # Calculate derived metrics
        romis = [m.romi for m in sorted_metrics]
        cpls = [m.cpl for m in sorted_metrics if m.leads > 0]
        cacs = [m.cac for m in sorted_metrics if m.sales > 0]
        cr_cls = [m.cr_cl for m in sorted_metrics if m.clicks > 0]
        cr_lss = [m.cr_ls for m in sorted_metrics if m.leads > 0]
        cr_css = [m.cr_cs for m in sorted_metrics if m.clicks > 0]
        
        return MovingAverages(
            romi_ma7=self.calculate_ma7(romis),
            cpl_ma7=self.calculate_ma7(cpls) if cpls else 0.0,
            cac_ma7=self.calculate_ma7(cacs) if cacs else 0.0,
            revenue_ma7=self.calculate_ma7(revenues),
            spend_ma7=self.calculate_ma7(spends),
            leads_ma7=self.calculate_ma7(leads),
            sales_ma7=self.calculate_ma7(sales),
            clicks_ma7=self.calculate_ma7(clicks),
            cr_cl_ma7=self.calculate_ma7(cr_cls) if cr_cls else 0.0,
            cr_ls_ma7=self.calculate_ma7(cr_lss) if cr_lss else 0.0,
            cr_cs_ma7=self.calculate_ma7(cr_css) if cr_css else 0.0,
        )
    
    def detect_source_anomalies(
        self,
        source: Source,
        campaign: Campaign,
        current_date: date
    ) -> List[Alert]:
        """Detect anomalies for a single source"""
        alerts = []
        
        if not source.daily_metrics:
            return alerts
        
        sorted_metrics = sorted(source.daily_metrics, key=lambda m: m.date)
        ma = self.get_moving_averages(sorted_metrics)
        
        # Get latest metrics
        latest = sorted_metrics[-1] if sorted_metrics else None
        if not latest:
            return alerts
        
        # 1. ROMI dropped sharply
        if ma.romi_ma7 > 0 and latest.romi < ma.romi_ma7 * self.romi_drop_threshold:
            alerts.append(Alert(
                type=AlertType.ROMI_DROP,
                severity="warning",
                message=f"ROMI dropped >30% for {source.name}",
                message_ru=f"ROMI упал более чем на 30% для {source.name}",
                source_id=source.rid,
                campaign_id=campaign.id,
                date=latest.date,
                value=latest.romi,
                threshold=ma.romi_ma7 * self.romi_drop_threshold,
                change_percent=((latest.romi - ma.romi_ma7) / ma.romi_ma7 * 100) if ma.romi_ma7 else 0,
            ))
        
        # 2. ROMI spiked (positive anomaly)
        if ma.romi_ma7 > 0 and latest.romi > ma.romi_ma7 * self.romi_spike_threshold:
            alerts.append(Alert(
                type=AlertType.REVENUE_SPIKE,
                severity="info",
                message=f"ROMI spiked >50% for {source.name}",
                message_ru=f"ROMI вырос более чем на 50% для {source.name}",
                source_id=source.rid,
                campaign_id=campaign.id,
                date=latest.date,
                value=latest.romi,
                change_percent=((latest.romi - ma.romi_ma7) / ma.romi_ma7 * 100) if ma.romi_ma7 else 0,
            ))
        
        # 3. CPL spiked
        if ma.cpl_ma7 > 0 and latest.cpl > ma.cpl_ma7 * self.cpl_spike_threshold:
            alerts.append(Alert(
                type=AlertType.CPL_SPIKE,
                severity="warning",
                message=f"CPL increased >40% for {source.name}",
                message_ru=f"CPL вырос на более чем 40% для {source.name}",
                source_id=source.rid,
                campaign_id=campaign.id,
                date=latest.date,
                value=latest.cpl,
                threshold=ma.cpl_ma7 * self.cpl_spike_threshold,
                change_percent=((latest.cpl - ma.cpl_ma7) / ma.cpl_ma7 * 100) if ma.cpl_ma7 else 0,
            ))
        
        # 4. ROMI went negative
        if latest.romi < 0:
            alerts.append(Alert(
                type=AlertType.ROMI_DROP,
                severity="critical",
                message=f"ROMI is negative for {source.name}",
                message_ru=f"ROMI отрицательный для {source.name}",
                source_id=source.rid,
                campaign_id=campaign.id,
                date=latest.date,
                value=latest.romi,
            ))
        
        # 5. No leads for N days
        recent_metrics = sorted_metrics[-self.no_leads_days:]
        if len(recent_metrics) >= self.no_leads_days:
            total_recent_leads = sum(m.leads for m in recent_metrics)
            if total_recent_leads == 0:
                alerts.append(Alert(
                    type=AlertType.SOURCE_NO_TRAFFIC,
                    severity="warning",
                    message=f"Source {source.name} has 0 leads for {self.no_leads_days} days",
                    message_ru=f"Источник {source.name} не приносит лидов уже {self.no_leads_days} дней",
                    source_id=source.rid,
                    campaign_id=campaign.id,
                    date=latest.date,
                ))
        
        # 6. Revenue spike
        if ma.revenue_ma7 > 0 and latest.revenue > ma.revenue_ma7 * self.revenue_spike_threshold:
            alerts.append(Alert(
                type=AlertType.REVENUE_SPIKE,
                severity="info",
                message=f"Revenue spiked for {source.name}",
                message_ru=f"Резкий рост выручки для {source.name}",
                source_id=source.rid,
                campaign_id=campaign.id,
                date=latest.date,
                value=latest.revenue,
                change_percent=((latest.revenue - ma.revenue_ma7) / ma.revenue_ma7 * 100) if ma.revenue_ma7 else 0,
            ))
        
        # 7. Source overheated (high spend, low ROMI)
        if ma.spend_ma7 > 0 and latest.spend > ma.spend_ma7 * 2:
            if latest.romi < ma.romi_ma7:
                alerts.append(Alert(
                    type=AlertType.SOURCE_OVERHEATED,
                    severity="warning",
                    message=f"Source {source.name} is overheated",
                    message_ru=f"Источник {source.name} перегрет: расходы выросли, ROMI упал",
                    source_id=source.rid,
                    campaign_id=campaign.id,
                    date=latest.date,
                ))
        
        # 8. CR dropped significantly
        if ma.cr_cs_ma7 > 0 and latest.cr_cs < ma.cr_cs_ma7 * self.cr_drop_threshold:
            alerts.append(Alert(
                type=AlertType.CR_DROP,
                severity="warning",
                message=f"CR(C→S) dropped >50% for {source.name}",
                message_ru=f"CR(C→S) упал более чем на 50% для {source.name}",
                source_id=source.rid,
                campaign_id=campaign.id,
                date=latest.date,
                value=latest.cr_cs,
                change_percent=((latest.cr_cs - ma.cr_cs_ma7) / ma.cr_cs_ma7 * 100) if ma.cr_cs_ma7 else 0,
            ))
        
        # 9. Check for funnel issues (high CPA, low CPL conversion)
        if latest.clicks > 50 and latest.leads == 0:
            alerts.append(Alert(
                type=AlertType.FUNNEL_ISSUE,
                severity="warning",
                message=f"High clicks but no leads for {source.name}",
                message_ru=f"Много кликов, но нет лидов для {source.name} - проблема воронки",
                source_id=source.rid,
                campaign_id=campaign.id,
                date=latest.date,
            ))
        
        # 10. Check for launch without sales
        start_date = source.get_effective_start_date()
        if start_date:
            days_since_start = (current_date - start_date).days
            if 2 <= days_since_start <= 5:  # Within 2-5 days of launch
                recent = [m for m in sorted_metrics if m.date >= start_date]
                if recent and sum(m.sales for m in recent) == 0 and sum(m.clicks for m in recent) > 20:
                    alerts.append(Alert(
                        type=AlertType.NO_SALES_AFTER_LAUNCH,
                        severity="warning",
                        message=f"No sales after launch for {source.name}",
                        message_ru=f"Источник {source.name} стартовал, но продаж нет",
                        source_id=source.rid,
                        campaign_id=campaign.id,
                        date=latest.date,
                    ))
        
        return alerts
    
    def detect_campaign_anomalies(
        self,
        campaign: Campaign,
        current_date: date
    ) -> List[Alert]:
        """Detect anomalies for a campaign"""
        alerts = []
        
        daily_agg = campaign.get_daily_aggregated_metrics()
        if not daily_agg:
            return alerts
        
        sorted_dates = sorted(daily_agg.keys())
        sorted_metrics = [daily_agg[d] for d in sorted_dates]
        ma = self.get_moving_averages(sorted_metrics)
        
        latest = sorted_metrics[-1] if sorted_metrics else None
        if not latest:
            return alerts
        
        # 1. ROMI below KPI
        if latest.romi < campaign.kpi.romi_negative:
            alerts.append(Alert(
                type=AlertType.ROMI_BELOW_KPI,
                severity="critical",
                message=f"ROMI below KPI for {campaign.name}",
                message_ru=f"ROMI ниже KPI для кампании {campaign.name}",
                campaign_id=campaign.id,
                date=latest.date,
                value=latest.romi,
                threshold=campaign.kpi.romi_negative,
            ))
        
        # 2. ROMI above positive KPI (good news)
        if latest.romi > campaign.kpi.romi_positive:
            alerts.append(Alert(
                type=AlertType.ROMI_ABOVE_KPI,
                severity="info",
                message=f"ROMI exceeded target for {campaign.name}",
                message_ru=f"ROMI превысил целевой показатель для {campaign.name}",
                campaign_id=campaign.id,
                date=latest.date,
                value=latest.romi,
                threshold=campaign.kpi.romi_positive,
            ))
        
        # 3. CPL exceeds KPI
        if campaign.kpi.cpl_negative and latest.cpl > campaign.kpi.cpl_negative:
            alerts.append(Alert(
                type=AlertType.CPL_SPIKE,
                severity="warning",
                message=f"CPL exceeds threshold for {campaign.name}",
                message_ru=f"CPL превышает допустимый порог для {campaign.name}",
                campaign_id=campaign.id,
                date=latest.date,
                value=latest.cpl,
                threshold=campaign.kpi.cpl_negative,
            ))
        
        # 4. No revenue for N days
        recent_metrics = sorted_metrics[-self.no_sales_days:]
        if len(recent_metrics) >= self.no_sales_days:
            total_recent_revenue = sum(m.revenue for m in recent_metrics)
            if total_recent_revenue == 0:
                alerts.append(Alert(
                    type=AlertType.REVENUE_DROP,
                    severity="critical",
                    message=f"No revenue for {self.no_sales_days} days in {campaign.name}",
                    message_ru=f"Нет выручки уже {self.no_sales_days} дней в кампании {campaign.name}",
                    campaign_id=campaign.id,
                    date=latest.date,
                ))
        
        # 5. Check if KPIs are set
        if campaign.kpi.romi_positive == 1200.0 and campaign.kpi.romi_negative == 700.0:
            alerts.append(Alert(
                type=AlertType.KPI_NOT_SET,
                severity="info",
                message=f"KPIs not set for {campaign.name}",
                message_ru=f"Не заданы KPI для кампании {campaign.name}",
                campaign_id=campaign.id,
            ))
        
        return alerts


class AlertEngine:
    """
    Main alert engine that generates all alerts and comparisons.
    """
    
    def __init__(self):
        self.detector = AnomalyDetector()
    
    def get_all_alerts(
        self,
        period: AnalyticsPeriod,
        current_date: Optional[date] = None
    ) -> List[Alert]:
        """Get all alerts for the analytics period"""
        if current_date is None:
            current_date = period.end_date
        
        all_alerts = []
        
        for campaign in period.campaigns:
            # Campaign-level alerts
            campaign_alerts = self.detector.detect_campaign_anomalies(
                campaign, current_date
            )
            all_alerts.extend(campaign_alerts)
            
            # Source-level alerts
            for source in campaign.sources:
                source_alerts = self.detector.detect_source_anomalies(
                    source, campaign, current_date
                )
                all_alerts.extend(source_alerts)
        
        # Sort by severity
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        all_alerts.sort(key=lambda a: severity_order.get(a.severity, 3))
        
        return all_alerts
    
    def compare_periods(
        self,
        period: AnalyticsPeriod,
        comparison_type: str = "week"  # "week" or "month"
    ) -> List[PeriodComparison]:
        """Compare current period with previous period"""
        comparisons = []
        
        if comparison_type == "week":
            days_back = 7
        else:
            days_back = 30
        
        # Get current and previous period metrics
        all_daily: Dict[date, DailyMetrics] = {}
        for campaign in period.campaigns:
            daily_agg = campaign.get_daily_aggregated_metrics()
            for d, m in daily_agg.items():
                if d not in all_daily:
                    all_daily[d] = DailyMetrics(date=d)
                dm = all_daily[d]
                dm.clicks += m.clicks
                dm.leads += m.leads
                dm.sales += m.sales
                dm.revenue += m.revenue
                dm.spend += m.spend
        
        if not all_daily:
            return comparisons
        
        sorted_dates = sorted(all_daily.keys())
        mid_point = len(sorted_dates) // 2
        
        if len(sorted_dates) < days_back * 2:
            mid_point = len(sorted_dates) // 2
        
        current_metrics = [all_daily[d] for d in sorted_dates[mid_point:]]
        previous_metrics = [all_daily[d] for d in sorted_dates[:mid_point]]
        
        if not current_metrics or not previous_metrics:
            return comparisons
        
        # Calculate totals for each period
        def calc_totals(metrics: List[DailyMetrics]) -> Dict[str, float]:
            total_revenue = sum(m.revenue for m in metrics)
            total_spend = sum(m.spend for m in metrics)
            total_leads = sum(m.leads for m in metrics)
            total_sales = sum(m.sales for m in metrics)
            total_clicks = sum(m.clicks for m in metrics)
            
            return {
                "revenue": total_revenue,
                "spend": total_spend,
                "leads": total_leads,
                "sales": total_sales,
                "romi": ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0,
                "cpl": (total_spend / total_leads) if total_leads > 0 else 0,
                "cr_cs": (total_sales / total_clicks * 100) if total_clicks > 0 else 0,
            }
        
        current_totals = calc_totals(current_metrics)
        previous_totals = calc_totals(previous_metrics)
        
        comparisons = [
            PeriodComparison("ROMI", current_totals["romi"], previous_totals["romi"]),
            PeriodComparison("CPL", current_totals["cpl"], previous_totals["cpl"]),
            PeriodComparison("CR(C→S)", current_totals["cr_cs"], previous_totals["cr_cs"]),
            PeriodComparison("Выручка", current_totals["revenue"], previous_totals["revenue"]),
            PeriodComparison("Продаж", current_totals["sales"], previous_totals["sales"]),
        ]
        
        return comparisons
    
    def format_alerts_text(self, alerts: List[Alert]) -> str:
        """Format alerts as text for display"""
        if not alerts:
            return "🧠 Всё стабильно. Аномалий не обнаружено."
        
        lines = ["⚠️ Алерты (автоматические сигналы)\n"]
        for alert in alerts:
            lines.append(f"• {alert.emoji} {alert.message_ru}")
        
        return "\n".join(lines)
    
    def format_comparison_text(
        self,
        comparisons: List[PeriodComparison],
        period_name: str = "неделя"
    ) -> str:
        """Format period comparison as text"""
        if not comparisons:
            return "Недостаточно транзакций для сравнения."
        
        lines = [f"🔁 Эта {period_name} vs прошлая:\n"]
        for comp in comparisons:
            lines.append(f"• {comp.metric_name}: {comp.formatted}")
        
        return "\n".join(lines)
    
    def get_expert_comments(
        self,
        period: AnalyticsPeriod,
        campaign: Optional[Campaign] = None
    ) -> List[str]:
        """
        Generate expert comments about sales peaks and campaign launches.
        Links sales spikes to advertising campaign starts.
        """
        comments = []
        
        campaigns_to_check = [campaign] if campaign else period.campaigns
        
        for camp in campaigns_to_check:
            daily_agg = camp.get_daily_aggregated_metrics()
            if not daily_agg:
                continue
            
            sorted_dates = sorted(daily_agg.keys())
            revenues = [daily_agg[d].revenue for d in sorted_dates]
            
            if len(revenues) < 3:
                continue
            
            mean_revenue = statistics.mean(revenues)
            stdev_revenue = statistics.stdev(revenues) if len(revenues) > 1 else 0
            
            # Find revenue spikes
            for i, (d, rev) in enumerate(zip(sorted_dates, revenues)):
                if stdev_revenue == 0:
                    continue
                
                zscore = (rev - mean_revenue) / stdev_revenue
                
                if zscore > 2.0:  # Significant spike
                    # Check if any source started advertising around this date
                    for source in camp.sources:
                        start_date = source.get_effective_start_date()
                        if start_date:
                            days_diff = (d - start_date).days
                            if 0 <= days_diff <= 3:
                                comments.append(
                                    f"🚀 Резкий пик продаж {d.strftime('%d.%m')} связан со стартом "
                                    f"рекламы в {source.social_network.value} ({source.name})"
                                )
                                break
            
            # Check for sources that started but have no sales
            for source in camp.sources:
                start_date = source.get_effective_start_date()
                if start_date and start_date >= sorted_dates[0]:
                    days_since = (sorted_dates[-1] - start_date).days
                    if 3 <= days_since <= 7:
                        # Check sales after launch
                        post_launch = [
                            m for m in source.daily_metrics 
                            if m.date >= start_date
                        ]
                        if sum(m.sales for m in post_launch) == 0 and sum(m.clicks for m in post_launch) > 20:
                            comments.append(
                                f"⚠️ Источник {source.name} стартовал {start_date.strftime('%d.%m')}, "
                                f"но продаж нет уже {days_since} дней"
                            )
        
        return comments
