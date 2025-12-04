"""
Graph 1 - Cross Analytics Report Generator

Generates comprehensive PNG report for all campaigns overview.
Includes:
- Header with totals
- Heatmap by day of week
- Revenue timelines by campaigns and social networks
- Budget distribution pie charts
- ROMI/LTV comparisons
- CPL/CR dynamic analysis
- Funnel efficiency analysis
- Alerts and period comparisons
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

from .models import (
    Campaign,
    Source,
    AnalyticsPeriod,
    SocialNetwork,
    DailyMetrics,
)
from .alerts import AlertEngine, AnomalyDetector
from .chart_utils import (
    create_figure,
    setup_style,
    format_currency,
    format_number,
    format_percent,
    create_header_box,
    plot_timeline_with_bars,
    plot_pie_chart,
    plot_horizontal_bar_chart,
    plot_vertical_bar_comparison,
    plot_heatmap,
    plot_dynamic_comparison,
    plot_funnel_comparison,
    plot_cr_funnel_comparison,
    add_alert_box,
    create_legend_toggles,
    save_figure,
    figure_to_bytes,
    COLORS,
    SOCIAL_NETWORK_COLORS,
)


class CrossAnalyticsReport:
    """
    Generates Graph 1 - Cross Analytics report for all campaigns.
    """
    
    def __init__(self, period: AnalyticsPeriod):
        self.period = period
        self.alert_engine = AlertEngine()
        self.alerts = self.alert_engine.get_all_alerts(period)
        self.week_comparison = self.alert_engine.compare_periods(period, "week")
        self.month_comparison = self.alert_engine.compare_periods(period, "month")
        self.expert_comments = self.alert_engine.get_expert_comments(period)
    
    def _get_daily_by_campaign(self) -> Dict[str, Dict[date, DailyMetrics]]:
        """Get daily metrics aggregated by campaign"""
        result = {}
        for campaign in self.period.campaigns:
            result[campaign.name] = campaign.get_daily_aggregated_metrics()
        return result
    
    def _get_daily_by_social_network(self) -> Dict[SocialNetwork, Dict[date, DailyMetrics]]:
        """Get daily metrics aggregated by social network"""
        result: Dict[SocialNetwork, Dict[date, DailyMetrics]] = {}
        
        for campaign in self.period.campaigns:
            for source in campaign.sources:
                sn = source.social_network
                if sn not in result:
                    result[sn] = {}
                
                for m in source.daily_metrics:
                    if m.date not in result[sn]:
                        result[sn][m.date] = DailyMetrics(date=m.date)
                    
                    dm = result[sn][m.date]
                    dm.clicks += m.clicks
                    dm.leads += m.leads
                    dm.sales += m.sales
                    dm.revenue += m.revenue
                    dm.spend += m.spend
        
        return result
    
    def _get_all_dates(self) -> List[date]:
        """Get sorted list of all dates in period"""
        all_dates = set()
        for campaign in self.period.campaigns:
            for d in campaign.get_daily_aggregated_metrics().keys():
                all_dates.add(d)
        return sorted(all_dates)
    
    def _get_total_daily_metrics(self) -> Dict[date, DailyMetrics]:
        """Get total daily metrics across all campaigns"""
        result: Dict[date, DailyMetrics] = {}
        
        for campaign in self.period.campaigns:
            daily_agg = campaign.get_daily_aggregated_metrics()
            for d, m in daily_agg.items():
                if d not in result:
                    result[d] = DailyMetrics(date=d)
                
                dm = result[d]
                dm.clicks += m.clicks
                dm.leads += m.leads
                dm.sales += m.sales
                dm.revenue += m.revenue
                dm.spend += m.spend
        
        return result
    
    def _create_heatmap_data(self) -> Tuple[np.ndarray, List[str], List[str]]:
        """Create heatmap data for sales by day of week"""
        # Days of week in Russian
        days_ru = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        
        # Get weekly data
        total_daily = self._get_total_daily_metrics()
        sorted_dates = sorted(total_daily.keys())
        
        if not sorted_dates:
            return np.zeros((1, 7)), ['Всего'], days_ru
        
        # Group by week and day of week
        weeks_data = defaultdict(lambda: [0] * 7)
        week_labels = []
        
        # Determine weeks
        start_date = sorted_dates[0]
        current_week = 0
        
        for d in sorted_dates:
            week_num = (d - start_date).days // 7
            day_of_week = d.weekday()
            weeks_data[week_num][day_of_week] = total_daily[d].sales
        
        # Create labels for weeks
        if len(weeks_data) <= 5:
            week_labels = [f'Неделя {i+1}' for i in range(len(weeks_data))]
        else:
            # Just show total
            total_by_day = [0] * 7
            for d in sorted_dates:
                day_of_week = d.weekday()
                total_by_day[day_of_week] += total_daily[d].sales
            return np.array([total_by_day]), ['Всего'], days_ru
        
        data = np.array([weeks_data[i] for i in range(len(weeks_data))])
        return data, week_labels, days_ru
    
    def generate(self, output_path: Optional[str] = None) -> bytes:
        """
        Generate the complete Graph 1 report.
        
        Returns:
            PNG image as bytes (also saves to output_path if provided)
        """
        setup_style()
        
        # Calculate figure height based on content
        fig = plt.figure(figsize=(16, 48), dpi=150)
        
        # Create grid layout
        gs = gridspec.GridSpec(
            nrows=16, ncols=2,
            height_ratios=[1.5, 1.5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1.5, 1],
            hspace=0.4, wspace=0.3
        )
        
        # Get data
        all_dates = self._get_all_dates()
        daily_by_campaign = self._get_daily_by_campaign()
        daily_by_sn = self._get_daily_by_social_network()
        total_daily = self._get_total_daily_metrics()
        
        # ===============================================
        # ROW 0: HEADER BOX
        # ===============================================
        ax_header = fig.add_subplot(gs[0, :])
        metrics = {
            "Выручка": format_currency(self.period.get_total_revenue()),
            "ROMI": format_percent(self.period.get_overall_romi()),
            "Расходы": format_currency(self.period.get_total_spend()),
            "CPL": format_currency(self.period.get_overall_cpl()),
            "Лиды": format_number(self.period.get_total_leads()),
            "LTV": format_currency(self.period.get_overall_ltv()),
            "Продажи": format_number(self.period.get_total_sales()),
            "Клики": format_number(self.period.get_total_clicks()),
        }
        
        # Calculate CR metrics
        total_clicks = self.period.get_total_clicks()
        total_leads = self.period.get_total_leads()
        total_sales = self.period.get_total_sales()
        
        cr_cl = (total_leads / total_clicks * 100) if total_clicks > 0 else 0
        cr_ls = (total_sales / total_leads * 100) if total_leads > 0 else 0
        cr_cs = (total_sales / total_clicks * 100) if total_clicks > 0 else 0
        
        create_header_box(
            ax_header,
            f"СКВОЗНАЯ АНАЛИТИКА",
            f"Период: {self.period.start_date.strftime('%d.%m.%Y')} - {self.period.end_date.strftime('%d.%m.%Y')}",
            metrics
        )
        
        # Add CR metrics below header
        ax_header.text(
            0.5, 0.15,
            f"CR(C→L): {cr_cl:.2f}%   |   CR(L→S): {cr_ls:.2f}%   |   CR(C→S): {cr_cs:.2f}%",
            transform=ax_header.transAxes,
            ha='center', va='center',
            fontsize=12, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS["bg_light"],
                     edgecolor=COLORS["grid"])
        )
        
        # ===============================================
        # ROW 1: HEATMAP
        # ===============================================
        ax_heatmap = fig.add_subplot(gs[1, :])
        heatmap_data, row_labels, col_labels = self._create_heatmap_data()
        plot_heatmap(
            ax_heatmap,
            heatmap_data,
            row_labels,
            col_labels,
            "Тепловая карта продаж по дням недели"
        )
        
        # ===============================================
        # ROW 2: BUDGET DISTRIBUTION PIES
        # ===============================================
        # Pie by campaigns
        ax_pie_campaigns = fig.add_subplot(gs[2, 0])
        campaign_spends = [(c.name, c.total_spend) for c in self.period.campaigns if c.total_spend > 0]
        if campaign_spends:
            names, values = zip(*campaign_spends)
            plot_pie_chart(
                ax_pie_campaigns,
                list(values),
                list(names),
                "Распределение бюджета по кампаниям",
                currency=True
            )
        
        # Pie by social networks
        ax_pie_sn = fig.add_subplot(gs[2, 1])
        sn_spend = self.period.get_spend_by_social_network()
        if sn_spend:
            sn_colors = [SOCIAL_NETWORK_COLORS.get(sn, COLORS["series"][i]) 
                        for i, sn in enumerate(sn_spend.keys())]
            plot_pie_chart(
                ax_pie_sn,
                list(sn_spend.values()),
                [sn.value for sn in sn_spend.keys()],
                "Распределение бюджета по соцсетям",
                colors=sn_colors,
                currency=True
            )
        
        # ===============================================
        # ROW 3: REVENUE TIMELINE BY CAMPAIGNS
        # ===============================================
        ax_timeline_campaigns = fig.add_subplot(gs[3, :])
        
        # Prepare data
        bar_values = [total_daily.get(d, DailyMetrics(date=d)).sales for d in all_dates]
        line_data = {}
        for campaign_name, daily_data in daily_by_campaign.items():
            line_data[campaign_name] = [
                daily_data.get(d, DailyMetrics(date=d)).revenue if d in daily_data else None
                for d in all_dates
            ]
        
        plot_timeline_with_bars(
            ax_timeline_campaigns,
            all_dates,
            bar_values,
            line_data,
            "Выручка по кампаниям в динамике",
            ylabel_bar="Продаж (шт)",
            ylabel_line="Выручка (₽)"
        )
        
        # ===============================================
        # ROW 4: ALERTS FOR CAMPAIGNS TIMELINE
        # ===============================================
        ax_alerts_campaigns = fig.add_subplot(gs[4, :])
        
        alerts_text = self.alert_engine.format_alerts_text(
            [a for a in self.alerts if a.source_id is None][:5]
        )
        comparison_text = self.alert_engine.format_comparison_text(
            self.week_comparison, "неделя"
        )
        
        add_alert_box(ax_alerts_campaigns, alerts_text, comparison_text)
        
        # ===============================================
        # ROW 5: REVENUE PIE BY CAMPAIGNS AND SOCIAL NETWORKS
        # ===============================================
        # Revenue by campaigns
        ax_revenue_pie_campaigns = fig.add_subplot(gs[5, 0])
        campaign_revenues = [(c.name, c.total_revenue) for c in self.period.campaigns if c.total_revenue > 0]
        if campaign_revenues:
            names, values = zip(*campaign_revenues)
            plot_pie_chart(
                ax_revenue_pie_campaigns,
                list(values),
                list(names),
                "Распределение прибыли по кампаниям",
                currency=True
            )
        
        # Revenue by social networks
        ax_revenue_pie_sn = fig.add_subplot(gs[5, 1])
        sn_revenue = self.period.get_revenue_by_social_network()
        if sn_revenue:
            sn_colors = [SOCIAL_NETWORK_COLORS.get(sn, COLORS["series"][i]) 
                        for i, sn in enumerate(sn_revenue.keys())]
            plot_pie_chart(
                ax_revenue_pie_sn,
                list(sn_revenue.values()),
                [sn.value for sn in sn_revenue.keys()],
                "Распределение прибыли по соцсетям",
                colors=sn_colors,
                currency=True
            )
        
        # ===============================================
        # ROW 6: REVENUE TIMELINE BY SOCIAL NETWORKS
        # ===============================================
        ax_timeline_sn = fig.add_subplot(gs[6, :])
        
        line_data_sn = {}
        for sn, daily_data in daily_by_sn.items():
            line_data_sn[sn.value] = [
                daily_data.get(d, DailyMetrics(date=d)).revenue if d in daily_data else None
                for d in all_dates
            ]
        
        bar_values_sn = [total_daily.get(d, DailyMetrics(date=d)).sales for d in all_dates]
        
        plot_timeline_with_bars(
            ax_timeline_sn,
            all_dates,
            bar_values_sn,
            line_data_sn,
            "Выручка по соцсетям в динамике",
            ylabel_bar="Продаж (шт)",
            ylabel_line="Выручка (₽)"
        )
        
        # ===============================================
        # ROW 7: ALERTS FOR SOCIAL NETWORKS TIMELINE
        # ===============================================
        ax_alerts_sn = fig.add_subplot(gs[7, :])
        
        month_comparison_text = self.alert_engine.format_comparison_text(
            self.month_comparison, "месяц"
        )
        expert_text = "\n".join(self.expert_comments[:3]) if self.expert_comments else "Нет комментариев"
        
        add_alert_box(ax_alerts_sn, expert_text, month_comparison_text)
        
        # ===============================================
        # ROW 8: AVERAGE LTV BY CAMPAIGNS
        # ===============================================
        ax_ltv = fig.add_subplot(gs[8, :])
        
        campaigns_with_ltv = [(c.name, c.overall_ltv) for c in self.period.campaigns if c.overall_ltv > 0]
        campaigns_with_ltv.sort(key=lambda x: x[1], reverse=True)
        
        if campaigns_with_ltv:
            names, values = zip(*campaigns_with_ltv)
            plot_horizontal_bar_chart(
                ax_ltv,
                list(values),
                list(names),
                "Средний LTV по кампаниям",
                xlabel="LTV (₽)",
                value_format="currency"
            )
        
        # ===============================================
        # ROW 9: ROMI COMPARISON BY CAMPAIGNS (VERTICAL)
        # ===============================================
        ax_romi_campaigns = fig.add_subplot(gs[9, :])
        
        campaigns_sorted = sorted(self.period.campaigns, key=lambda c: c.overall_romi, reverse=True)
        campaign_names = [c.name for c in campaigns_sorted]
        campaign_romis = [c.overall_romi for c in campaigns_sorted]
        campaign_spends = [c.total_spend for c in campaigns_sorted]
        
        plot_vertical_bar_comparison(
            ax_romi_campaigns,
            campaign_names,
            campaign_romis,
            campaign_spends,
            legend1="ROMI (%)",
            legend2="Расход (₽)",
            title="Сравнение ROMI по кампаниям"
        )
        
        # ===============================================
        # ROW 10: ROMI BY SOCIAL NETWORKS WITH CPL
        # ===============================================
        ax_romi_sn = fig.add_subplot(gs[10, :])
        
        # Calculate ROMI and CPL by social network
        sn_metrics = {}
        for campaign in self.period.campaigns:
            for source in campaign.sources:
                sn = source.social_network
                if sn not in sn_metrics:
                    sn_metrics[sn] = {'revenue': 0, 'spend': 0, 'leads': 0}
                sn_metrics[sn]['revenue'] += source.total_revenue
                sn_metrics[sn]['spend'] += source.total_spend
                sn_metrics[sn]['leads'] += source.total_leads
        
        sn_data = []
        for sn, m in sn_metrics.items():
            romi = ((m['revenue'] - m['spend']) / m['spend'] * 100) if m['spend'] > 0 else 0
            cpl = (m['spend'] / m['leads']) if m['leads'] > 0 else 0
            sn_data.append((sn.value, romi, cpl))
        
        sn_data.sort(key=lambda x: x[1], reverse=True)
        
        if sn_data:
            sn_names, sn_romis, sn_cpls = zip(*sn_data)
            plot_vertical_bar_comparison(
                ax_romi_sn,
                list(sn_names),
                list(sn_romis),
                list(sn_cpls),
                legend1="ROMI (%)",
                legend2="CPL (₽)",
                title="ROMI и CPL по соцсетям"
            )
        
        # ===============================================
        # ROW 11: CPL DYNAMIC BY SOURCES
        # ===============================================
        ax_cpl_dynamic = fig.add_subplot(gs[11, :])
        
        # Get all sources CPL by day
        source_cpl_data = {}
        all_sources = self.period.get_all_sources()
        
        for source in all_sources[:10]:  # Limit to top 10
            source_cpl_data[source.name] = []
            for d in all_dates:
                day_metrics = next((m for m in source.daily_metrics if m.date == d), None)
                if day_metrics and day_metrics.cpl > 0:
                    source_cpl_data[source.name].append(day_metrics.cpl)
                else:
                    source_cpl_data[source.name].append(None)
        
        # Calculate average CPL
        all_cpls = [m.cpl for m in total_daily.values() if m.cpl > 0]
        avg_cpl = sum(all_cpls) / len(all_cpls) if all_cpls else 0
        
        plot_dynamic_comparison(
            ax_cpl_dynamic,
            all_dates,
            source_cpl_data,
            "CPL по источникам в динамике",
            ylabel="CPL (₽)",
            average_value=avg_cpl
        )
        
        # ===============================================
        # ROW 12: ALERTS FOR CPL
        # ===============================================
        ax_alerts_cpl = fig.add_subplot(gs[12, :])
        
        cpl_alerts = [a for a in self.alerts if a.type.value == "cpl_spike"][:5]
        cpl_alerts_text = self.alert_engine.format_alerts_text(cpl_alerts)
        
        add_alert_box(ax_alerts_cpl, cpl_alerts_text, comparison_text)
        
        # ===============================================
        # ROW 13: FUNNEL COMPARISON (CPA → CPL → CAC)
        # ===============================================
        ax_funnel = fig.add_subplot(gs[13, :])
        
        source_funnel_data = []
        for source in all_sources[:8]:  # Top 8 sources
            cpc = source.total_spend / source.total_clicks if source.total_clicks > 0 else 0
            cpl = source.overall_cpl
            cac = source.overall_cac
            if cpl > 0 or cac > 0:  # Only include sources with data
                source_funnel_data.append((source.name[:15], cpc, cpl, cac))
        
        if source_funnel_data:
            names, cpcs, cpls, cacs = zip(*source_funnel_data)
            plot_funnel_comparison(
                ax_funnel,
                list(names),
                list(cpcs),
                list(cpls),
                list(cacs),
                "Анализ воронки: CPC → CPL → CAC по источникам"
            )
        
        # ===============================================
        # ROW 14: CR FUNNEL ANALYSIS
        # ===============================================
        ax_cr_funnel = fig.add_subplot(gs[14, :])
        
        source_cr_data = []
        for source in all_sources[:8]:
            cr_cl = source.overall_cr_cl
            cr_ls = source.overall_cr_ls
            cr_cs = source.overall_cr_cs
            if cr_cl > 0 or cr_cs > 0:
                source_cr_data.append((source.name[:15], cr_cl, cr_ls, cr_cs))
        
        if source_cr_data:
            names, cr_cls, cr_lss, cr_css = zip(*source_cr_data)
            plot_cr_funnel_comparison(
                ax_cr_funnel,
                list(names),
                list(cr_cls),
                list(cr_lss),
                list(cr_css),
                "Эффективность воронки: CR(C→L) → CR(L→S) → CR(C→S)"
            )
        
        # ===============================================
        # ROW 15: LEGEND TOGGLES PLACEHOLDER
        # ===============================================
        ax_toggles = fig.add_subplot(gs[15, :])
        ax_toggles.axis('off')
        ax_toggles.text(
            0.5, 0.5,
            "💡 Совет: В интерактивной версии можно включать/выключать отдельные кампании и источники на графиках",
            transform=ax_toggles.transAxes,
            ha='center', va='center',
            fontsize=10, style='italic', color='gray'
        )
        
        # Save or return
        if output_path:
            save_figure(fig, output_path)
        
        return figure_to_bytes(fig)
    
    def generate_summary_card(self, campaign: Campaign) -> str:
        """
        Generate text summary card for a campaign (for bot message).
        
        Returns formatted string like:
        🎯 Campaign Name
        ID: 1410089
        Lead: 18 | Sale: 5 | Revenue: 2.4M ₽
        ROMI: 450% | CPL: 240 руб | CR C→S: 125%
        """
        return (
            f"🎯 {campaign.name}\n"
            f"ID: {campaign.id}\n"
            f"Создана: {campaign.created_at.strftime('%Y-%m-%d')}\n"
            f"Lead: {campaign.total_leads} | Sale: {campaign.total_sales} | "
            f"Revenue: {format_currency(campaign.total_revenue)}\n"
            f"ROMI: {campaign.overall_romi:.0f}% | "
            f"CPL: {format_currency(campaign.overall_cpl)} | "
            f"CR C→S: {campaign.overall_cr_cs:.2f}%"
        )
    
    def generate_campaign_card(self, campaign: Campaign) -> str:
        """
        Generate detailed campaign card for bot.
        """
        top_sources = campaign.get_top_sources(3, "romi")
        worst_sources = campaign.get_worst_sources(3, "romi")
        
        # Top sources text
        top_text = ""
        for source in top_sources:
            if source.overall_romi > 0:
                top_text += f"{source.social_network.value}_{source.name} — ROMI {source.overall_romi:.0f}%\n"
        
        # Worst sources text
        worst_text = ""
        for source in worst_sources:
            if source.overall_romi < 100:
                worst_text += f"{source.social_network.value}_{source.name} — ROMI {source.overall_romi:.0f}%\n"
        
        # Social network breakdown
        sn_breakdown = {}
        for source in campaign.sources:
            sn = source.social_network.value
            if sn not in sn_breakdown:
                sn_breakdown[sn] = {'revenue': 0, 'spend': 0, 'leads': 0}
            sn_breakdown[sn]['revenue'] += source.total_revenue
            sn_breakdown[sn]['spend'] += source.total_spend
            sn_breakdown[sn]['leads'] += source.total_leads
        
        sn_text = ""
        total_spend = campaign.total_spend
        for sn, m in sn_breakdown.items():
            romi = ((m['revenue'] - m['spend']) / m['spend'] * 100) if m['spend'] > 0 else 0
            cpl = (m['spend'] / m['leads']) if m['leads'] > 0 else 0
            pct = (m['spend'] / total_spend * 100) if total_spend > 0 else 0
            sn_text += f"{sn} — ROMI {romi:.0f}% | CPL {format_currency(cpl)}\n"
        
        # Budget distribution
        budget_text = ""
        for sn, m in sorted(sn_breakdown.items(), key=lambda x: x[1]['spend'], reverse=True):
            pct = (m['spend'] / total_spend * 100) if total_spend > 0 else 0
            budget_text += f"{sn} — {pct:.0f}%\n"
        
        # Express analytics for sources
        express_text = ""
        for source in campaign.sources[:5]:
            express_text += f"{source.social_network.value}_{source.name} (RID {source.rid}) — ROMI {source.overall_romi:.0f}%\n"
        
        return f"""📊 Кампания: {campaign.name}
ID: {campaign.id}
Создана: {campaign.created_at.strftime('%Y-%m-%d')}

💰 Итоги:
Выручка: {format_currency(campaign.total_revenue)}
Расходы: {format_currency(campaign.total_spend)}
ROMI: {campaign.overall_romi:.0f}%
CPL: {format_currency(campaign.overall_cpl)}

🔥 Топ источник:
{top_text or "Нет данных"}
⚠️ Хуже всех:
{worst_text or "Нет данных"}
📈 Конверсии:
CR(C→L): {campaign.overall_cr_cl:.2f}%
CR(L→S): {campaign.overall_cr_ls:.2f}%
CR(C→S): {campaign.overall_cr_cs:.2f}%

📂 Соцсети:
{sn_text or "Нет данных"}
💸 Распределение бюджета:
{budget_text or "Нет данных"}
----------------------------------

📁 Графики:
1. Сквозная по кампании: /analytics_source_{campaign.id}
2. CSV кампании: /analytics_file_{campaign.id}

----------------------------------

🎯 KPI:
ROMI positive: {campaign.kpi.romi_positive}%
ROMI negative: {campaign.kpi.romi_negative}%
CPL positive: {format_currency(campaign.kpi.cpl_positive) if campaign.kpi.cpl_positive else "не задан"}
CPL negative: {format_currency(campaign.kpi.cpl_negative) if campaign.kpi.cpl_negative else "не задан"}

💡 Задать KPI:
/kpi_positive_{campaign.id} число
/kpi_negative_{campaign.id} число
/cpl_positive_{campaign.id} число
/cpl_negative_{campaign.id} число

----------------------------------

📌 Экспресс-аналитика по источникам:
{express_text}
(каждый источник → кнопка /rid_{{rid_id}})
"""
