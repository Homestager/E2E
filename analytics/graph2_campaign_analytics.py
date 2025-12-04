"""
Graph 2 - Campaign Analytics Report Generator

Generates detailed PNG report for a single campaign.
Includes:
- Header with campaign summary
- Revenue by sources (RIDs) timeline
- Revenue by social networks timeline  
- Budget distribution by sources and social networks
- LTV by sources
- ROMI comparison with KPI lines
- CPL/CAC/CPA analysis
- CR funnel analysis
- Alerts and expert comments
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
    KPISettings,
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
    save_figure,
    figure_to_bytes,
    COLORS,
    SOCIAL_NETWORK_COLORS,
)


class CampaignAnalyticsReport:
    """
    Generates Graph 2 - Detailed analytics report for a single campaign.
    """
    
    def __init__(self, campaign: Campaign, period: AnalyticsPeriod):
        self.campaign = campaign
        self.period = period
        self.alert_engine = AlertEngine()
        
        # Create a period with just this campaign for alerts
        single_campaign_period = AnalyticsPeriod(
            start_date=period.start_date,
            end_date=period.end_date,
            campaigns=[campaign]
        )
        
        self.alerts = self.alert_engine.get_all_alerts(single_campaign_period)
        self.week_comparison = self.alert_engine.compare_periods(single_campaign_period, "week")
        self.month_comparison = self.alert_engine.compare_periods(single_campaign_period, "month")
        self.expert_comments = self.alert_engine.get_expert_comments(single_campaign_period, campaign)
    
    def _get_all_dates(self) -> List[date]:
        """Get sorted list of all dates with data"""
        all_dates = set()
        for source in self.campaign.sources:
            for m in source.daily_metrics:
                all_dates.add(m.date)
        return sorted(all_dates)
    
    def _get_daily_by_source(self) -> Dict[str, Dict[date, DailyMetrics]]:
        """Get daily metrics by source"""
        result = {}
        for source in self.campaign.sources:
            result[source.name] = {m.date: m for m in source.daily_metrics}
        return result
    
    def _get_daily_by_social_network(self) -> Dict[SocialNetwork, Dict[date, DailyMetrics]]:
        """Get daily metrics aggregated by social network"""
        result: Dict[SocialNetwork, Dict[date, DailyMetrics]] = {}
        
        for source in self.campaign.sources:
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
    
    def _get_total_daily_metrics(self) -> Dict[date, DailyMetrics]:
        """Get total daily metrics for campaign"""
        return self.campaign.get_daily_aggregated_metrics()
    
    def generate(self, output_path: Optional[str] = None) -> bytes:
        """
        Generate the complete Graph 2 report.
        
        Returns:
            PNG image as bytes (also saves to output_path if provided)
        """
        setup_style()
        
        # Calculate figure height based on content
        fig = plt.figure(figsize=(16, 60), dpi=150)
        
        # Create grid layout
        gs = gridspec.GridSpec(
            nrows=20, ncols=2,
            height_ratios=[1.5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            hspace=0.4, wspace=0.3
        )
        
        # Get data
        all_dates = self._get_all_dates()
        daily_by_source = self._get_daily_by_source()
        daily_by_sn = self._get_daily_by_social_network()
        total_daily = self._get_total_daily_metrics()
        
        # ===============================================
        # ROW 0: HEADER BOX
        # ===============================================
        ax_header = fig.add_subplot(gs[0, :])
        
        metrics = {
            "Выручка": format_currency(self.campaign.total_revenue),
            "ROMI": format_percent(self.campaign.overall_romi),
            "Расходы": format_currency(self.campaign.total_spend),
            "CPL": format_currency(self.campaign.overall_cpl),
            "Лиды": format_number(self.campaign.total_leads),
            "LTV": format_currency(self.campaign.overall_ltv),
            "Продажи": format_number(self.campaign.total_sales),
            "Клики": format_number(self.campaign.total_clicks),
        }
        
        create_header_box(
            ax_header,
            f"АНАЛИТИКА КАМПАНИИ: {self.campaign.name}",
            f"ID: {self.campaign.id} | Создана: {self.campaign.created_at.strftime('%d.%m.%Y')}",
            metrics
        )
        
        # Add CR metrics
        ax_header.text(
            0.5, 0.1,
            f"CR(C→L): {self.campaign.overall_cr_cl:.2f}%   |   "
            f"CR(L→S): {self.campaign.overall_cr_ls:.2f}%   |   "
            f"CR(C→S): {self.campaign.overall_cr_cs:.2f}%",
            transform=ax_header.transAxes,
            ha='center', va='center',
            fontsize=12, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS["bg_light"],
                     edgecolor=COLORS["grid"])
        )
        
        # ===============================================
        # ROW 1: REVENUE TIMELINE BY SOURCES (RIDs)
        # ===============================================
        ax_timeline_sources = fig.add_subplot(gs[1, :])
        
        bar_values = [total_daily.get(d, DailyMetrics(date=d)).sales for d in all_dates]
        line_data = {}
        for source_name, daily_data in daily_by_source.items():
            line_data[source_name] = [
                daily_data.get(d, DailyMetrics(date=d)).revenue if d in daily_data else None
                for d in all_dates
            ]
        
        plot_timeline_with_bars(
            ax_timeline_sources,
            all_dates,
            bar_values,
            line_data,
            "Выручка по источникам (RID) в динамике",
            ylabel_bar="Продаж (шт)",
            ylabel_line="Выручка (₽)"
        )
        
        # ===============================================
        # ROW 2: ALERTS FOR SOURCES TIMELINE
        # ===============================================
        ax_alerts_sources = fig.add_subplot(gs[2, :])
        
        source_alerts = [a for a in self.alerts if a.source_id is not None][:5]
        alerts_text = self.alert_engine.format_alerts_text(source_alerts)
        comparison_text = self.alert_engine.format_comparison_text(
            self.week_comparison, "неделя"
        )
        
        add_alert_box(ax_alerts_sources, alerts_text, comparison_text)
        
        # ===============================================
        # ROW 3: REVENUE PIE BY SOURCES
        # ===============================================
        ax_pie_sources = fig.add_subplot(gs[3, 0])
        
        source_revenues = [(s.name, s.total_revenue) for s in self.campaign.sources if s.total_revenue > 0]
        source_revenues.sort(key=lambda x: x[1], reverse=True)
        
        if source_revenues:
            names, values = zip(*source_revenues[:10])  # Top 10
            plot_pie_chart(
                ax_pie_sources,
                list(values),
                list(names),
                "Распределение выручки по источникам",
                currency=True
            )
        
        # REVENUE PIE BY SOCIAL NETWORKS
        ax_pie_sn = fig.add_subplot(gs[3, 1])
        
        sn_revenue = {}
        for source in self.campaign.sources:
            sn = source.social_network
            if sn not in sn_revenue:
                sn_revenue[sn] = 0
            sn_revenue[sn] += source.total_revenue
        
        if sn_revenue:
            sn_colors = [SOCIAL_NETWORK_COLORS.get(sn, COLORS["series"][i]) 
                        for i, sn in enumerate(sn_revenue.keys())]
            plot_pie_chart(
                ax_pie_sn,
                list(sn_revenue.values()),
                [sn.value for sn in sn_revenue.keys()],
                "Распределение выручки по соцсетям",
                colors=sn_colors,
                currency=True
            )
        
        # ===============================================
        # ROW 4: REVENUE TIMELINE BY SOCIAL NETWORKS
        # ===============================================
        ax_timeline_sn = fig.add_subplot(gs[4, :])
        
        line_data_sn = {}
        for sn, daily_data in daily_by_sn.items():
            line_data_sn[sn.value] = [
                daily_data.get(d, DailyMetrics(date=d)).revenue if d in daily_data else None
                for d in all_dates
            ]
        
        plot_timeline_with_bars(
            ax_timeline_sn,
            all_dates,
            bar_values,
            line_data_sn,
            "Выручка по соцсетям в динамике",
            ylabel_bar="Продаж (шт)",
            ylabel_line="Выручка (₽)"
        )
        
        # ===============================================
        # ROW 5: ALERTS FOR SOCIAL NETWORKS
        # ===============================================
        ax_alerts_sn = fig.add_subplot(gs[5, :])
        
        month_text = self.alert_engine.format_comparison_text(
            self.month_comparison, "месяц"
        )
        expert_text = "\n".join(self.expert_comments[:3]) if self.expert_comments else "Нет комментариев"
        
        add_alert_box(ax_alerts_sn, expert_text, month_text)
        
        # ===============================================
        # ROW 6: BUDGET DISTRIBUTION BY SOURCES AND SOCIAL NETWORKS
        # ===============================================
        ax_budget_sources = fig.add_subplot(gs[6, 0])
        
        source_spends = [(s.name, s.total_spend) for s in self.campaign.sources if s.total_spend > 0]
        source_spends.sort(key=lambda x: x[1], reverse=True)
        
        if source_spends:
            names, values = zip(*source_spends[:10])
            plot_pie_chart(
                ax_budget_sources,
                list(values),
                list(names),
                "Распределение бюджета по источникам",
                currency=True
            )
        
        ax_budget_sn = fig.add_subplot(gs[6, 1])
        
        sn_spend = {}
        for source in self.campaign.sources:
            sn = source.social_network
            if sn not in sn_spend:
                sn_spend[sn] = 0
            sn_spend[sn] += source.total_spend
        
        if sn_spend:
            sn_colors = [SOCIAL_NETWORK_COLORS.get(sn, COLORS["series"][i]) 
                        for i, sn in enumerate(sn_spend.keys())]
            plot_pie_chart(
                ax_budget_sn,
                list(sn_spend.values()),
                [sn.value for sn in sn_spend.keys()],
                "Распределение бюджета по соцсетям",
                colors=sn_colors,
                currency=True
            )
        
        # ===============================================
        # ROW 7: AVERAGE LTV BY SOURCES
        # ===============================================
        ax_ltv_sources = fig.add_subplot(gs[7, :])
        
        source_ltvs = [(s.name, s.overall_ltv) for s in self.campaign.sources if s.overall_ltv > 0]
        source_ltvs.sort(key=lambda x: x[1], reverse=True)
        
        if source_ltvs:
            names, values = zip(*source_ltvs[:10])
            plot_horizontal_bar_chart(
                ax_ltv_sources,
                list(values),
                list(names),
                "Средний LTV по источникам",
                xlabel="LTV (₽)",
                value_format="currency"
            )
        
        # ===============================================
        # ROW 8: ROMI COMPARISON BY SOURCES WITH KPI LINES
        # ===============================================
        ax_romi_sources = fig.add_subplot(gs[8, :])
        
        sources_sorted = sorted(self.campaign.sources, key=lambda s: s.overall_romi, reverse=True)
        source_names = [s.name[:15] for s in sources_sorted[:12]]
        source_romis = [s.overall_romi for s in sources_sorted[:12]]
        source_spends = [s.total_spend for s in sources_sorted[:12]]
        
        plot_vertical_bar_comparison(
            ax_romi_sources,
            source_names,
            source_romis,
            source_spends,
            legend1="ROMI (%)",
            legend2="Расход (₽)",
            title="Сравнение ROMI по источникам (с KPI)",
            kpi_positive=self.campaign.kpi.romi_positive,
            kpi_negative=self.campaign.kpi.romi_negative
        )
        
        # ===============================================
        # ROW 9: ROMI COMPARISON BY SOCIAL NETWORKS WITH CPL
        # ===============================================
        ax_romi_sn = fig.add_subplot(gs[9, :])
        
        sn_metrics = {}
        for source in self.campaign.sources:
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
                title="ROMI и CPL по соцсетям (с KPI)",
                kpi_positive=self.campaign.kpi.romi_positive,
                kpi_negative=self.campaign.kpi.romi_negative
            )
        
        # ===============================================
        # ROW 10: CPL COMPARISON BY SOURCES (HORIZONTAL)
        # ===============================================
        ax_cpl_sources = fig.add_subplot(gs[10, :])
        
        sources_by_cpl = sorted(
            [s for s in self.campaign.sources if s.overall_cpl > 0],
            key=lambda s: s.overall_cpl
        )[:12]
        
        if sources_by_cpl:
            plot_horizontal_bar_chart(
                ax_cpl_sources,
                [s.overall_cpl for s in sources_by_cpl],
                [s.name[:15] for s in sources_by_cpl],
                "Стоимость лида (CPL) по источникам",
                xlabel="CPL (₽)",
                kpi_positive=self.campaign.kpi.cpl_positive,
                kpi_negative=self.campaign.kpi.cpl_negative,
                value_format="currency"
            )
        
        # ===============================================
        # ROW 11: CAC COMPARISON BY SOURCES
        # ===============================================
        ax_cac_sources = fig.add_subplot(gs[11, :])
        
        sources_by_cac = sorted(
            [s for s in self.campaign.sources if s.overall_cac > 0],
            key=lambda s: s.overall_cac
        )[:12]
        
        if sources_by_cac:
            plot_horizontal_bar_chart(
                ax_cac_sources,
                [s.overall_cac for s in sources_by_cac],
                [s.name[:15] for s in sources_by_cac],
                "Стоимость клиента (CAC) по источникам",
                xlabel="CAC (₽)",
                kpi_positive=self.campaign.kpi.cac_positive,
                kpi_negative=self.campaign.kpi.cac_negative,
                value_format="currency"
            )
        
        # ===============================================
        # ROW 12: CPC (COST PER CLICK) BY SOURCES
        # ===============================================
        ax_cpc_sources = fig.add_subplot(gs[12, :])
        
        sources_with_cpc = [
            (s.name[:15], s.total_spend / s.total_clicks if s.total_clicks > 0 else 0)
            for s in self.campaign.sources
        ]
        sources_with_cpc = [(n, v) for n, v in sources_with_cpc if v > 0]
        sources_with_cpc.sort(key=lambda x: x[1])
        
        if sources_with_cpc:
            names, values = zip(*sources_with_cpc[:12])
            plot_horizontal_bar_chart(
                ax_cpc_sources,
                list(values),
                list(names),
                "Стоимость клика (CPC) по источникам",
                xlabel="CPC (₽)",
                value_format="currency"
            )
        
        # ===============================================
        # ROW 13: CR(C→S) BY SOURCES (HORIZONTAL)
        # ===============================================
        ax_cr_cs_sources = fig.add_subplot(gs[13, :])
        
        sources_by_cr_cs = sorted(
            [s for s in self.campaign.sources if s.overall_cr_cs > 0],
            key=lambda s: s.overall_cr_cs,
            reverse=True
        )[:12]
        
        if sources_by_cr_cs:
            plot_horizontal_bar_chart(
                ax_cr_cs_sources,
                [s.overall_cr_cs for s in sources_by_cr_cs],
                [s.name[:15] for s in sources_by_cr_cs],
                "CR(C→S) по источникам",
                xlabel="CR (%)",
                value_format="percent"
            )
        
        # ===============================================
        # ROW 14: CR(C→L) BY SOURCES
        # ===============================================
        ax_cr_cl_sources = fig.add_subplot(gs[14, :])
        
        sources_by_cr_cl = sorted(
            [s for s in self.campaign.sources if s.overall_cr_cl > 0],
            key=lambda s: s.overall_cr_cl,
            reverse=True
        )[:12]
        
        if sources_by_cr_cl:
            plot_horizontal_bar_chart(
                ax_cr_cl_sources,
                [s.overall_cr_cl for s in sources_by_cr_cl],
                [s.name[:15] for s in sources_by_cr_cl],
                "CR(C→L) по источникам",
                xlabel="CR (%)",
                value_format="percent"
            )
        
        # ===============================================
        # ROW 15: CR(L→S) BY SOURCES
        # ===============================================
        ax_cr_ls_sources = fig.add_subplot(gs[15, :])
        
        sources_by_cr_ls = sorted(
            [s for s in self.campaign.sources if s.overall_cr_ls > 0],
            key=lambda s: s.overall_cr_ls,
            reverse=True
        )[:12]
        
        if sources_by_cr_ls:
            plot_horizontal_bar_chart(
                ax_cr_ls_sources,
                [s.overall_cr_ls for s in sources_by_cr_ls],
                [s.name[:15] for s in sources_by_cr_ls],
                "CR(L→S) по источникам",
                xlabel="CR (%)",
                value_format="percent"
            )
        
        # ===============================================
        # ROW 16: FUNNEL COST COMPARISON (CPA → CPL → CAC)
        # ===============================================
        ax_funnel_cost = fig.add_subplot(gs[16, :])
        
        source_funnel_data = []
        for source in self.campaign.sources[:8]:
            cpc = source.total_spend / source.total_clicks if source.total_clicks > 0 else 0
            cpl = source.overall_cpl
            cac = source.overall_cac
            if cpl > 0 or cac > 0:
                source_funnel_data.append((source.name[:12], cpc, cpl, cac))
        
        if source_funnel_data:
            names, cpcs, cpls, cacs = zip(*source_funnel_data)
            plot_funnel_comparison(
                ax_funnel_cost,
                list(names),
                list(cpcs),
                list(cpls),
                list(cacs),
                "Анализ воронки: CPC → CPL → CAC"
            )
        
        # ===============================================
        # ROW 17: CR FUNNEL COMPARISON
        # ===============================================
        ax_cr_funnel = fig.add_subplot(gs[17, :])
        
        source_cr_data = []
        for source in self.campaign.sources[:8]:
            cr_cl = source.overall_cr_cl
            cr_ls = source.overall_cr_ls
            cr_cs = source.overall_cr_cs
            if cr_cl > 0 or cr_cs > 0:
                source_cr_data.append((source.name[:12], cr_cl, cr_ls, cr_cs))
        
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
        # ROW 18: DYNAMIC CPL OVER TIME
        # ===============================================
        ax_cpl_dynamic = fig.add_subplot(gs[18, :])
        
        source_cpl_data = {}
        for source in self.campaign.sources[:10]:
            source_cpl_data[source.name[:15]] = []
            for d in all_dates:
                day_metrics = next((m for m in source.daily_metrics if m.date == d), None)
                if day_metrics and day_metrics.cpl > 0:
                    source_cpl_data[source.name[:15]].append(day_metrics.cpl)
                else:
                    source_cpl_data[source.name[:15]].append(None)
        
        # Calculate average CPL
        all_cpls = []
        for d in all_dates:
            day_m = total_daily.get(d)
            if day_m and day_m.cpl > 0:
                all_cpls.append(day_m.cpl)
        avg_cpl = sum(all_cpls) / len(all_cpls) if all_cpls else 0
        
        plot_dynamic_comparison(
            ax_cpl_dynamic,
            all_dates,
            source_cpl_data,
            "CPL по источникам в динамике",
            ylabel="CPL (₽)",
            average_value=avg_cpl,
            kpi_positive=self.campaign.kpi.cpl_positive,
            kpi_negative=self.campaign.kpi.cpl_negative
        )
        
        # ===============================================
        # ROW 19: FINAL ALERTS AND EXPERT COMMENTS
        # ===============================================
        ax_final = fig.add_subplot(gs[19, :])
        ax_final.axis('off')
        
        # Compile all expert comments
        all_comments = []
        all_comments.extend(self.expert_comments[:5])
        
        # Add funnel analysis comments
        for source in self.campaign.sources[:3]:
            # Check for funnel issues
            if source.overall_cr_cl > 10 and source.overall_cr_cs < 0.5:
                all_comments.append(
                    f"🔧 {source.name}: Высокий CR(C→L) ({source.overall_cr_cl:.1f}%), "
                    f"но низкий CR(C→S) ({source.overall_cr_cs:.2f}%) - проблема на этапе продаж"
                )
            
            if source.total_clicks > 100 and source.total_leads < 3:
                all_comments.append(
                    f"⚠️ {source.name}: Много кликов ({source.total_clicks}), мало лидов ({source.total_leads}) - "
                    f"проверьте посадочную страницу"
                )
        
        if all_comments:
            comments_text = "🧠 Экспертные комментарии:\n" + "\n".join(f"• {c}" for c in all_comments[:5])
        else:
            comments_text = "🧠 Всё стабильно. Аномалий не обнаружено."
        
        ax_final.text(
            0.5, 0.5, comments_text,
            transform=ax_final.transAxes,
            ha='center', va='center',
            fontsize=10,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9',
                     edgecolor='#4CAF50', alpha=0.9),
            family='monospace'
        )
        
        # Save or return
        if output_path:
            save_figure(fig, output_path)
        
        return figure_to_bytes(fig)
    
    def generate_source_card(self, source: Source) -> str:
        """
        Generate text card for a specific source/RID.
        """
        return f"""📊 Источник: {source.name}
RID: {source.rid}
Соцсеть: {source.social_network.value}
Создан: {source.created_at.strftime('%Y-%m-%d')}
Старт рекламы: {source.ad_start_date.strftime('%Y-%m-%d') if source.ad_start_date else 'Не указан'}

💰 Метрики:
Выручка: {format_currency(source.total_revenue)}
Расходы: {format_currency(source.total_spend)}
ROMI: {source.overall_romi:.0f}%
CPL: {format_currency(source.overall_cpl)}
CAC: {format_currency(source.overall_cac)}
LTV: {format_currency(source.overall_ltv)}

📈 Воронка:
Клики: {format_number(source.total_clicks)}
Лиды: {format_number(source.total_leads)}
Продажи: {format_number(source.total_sales)}

📊 Конверсии:
CR(C→L): {source.overall_cr_cl:.2f}%
CR(L→S): {source.overall_cr_ls:.2f}%
CR(C→S): {source.overall_cr_cs:.2f}%

🎯 KPI источника:
ROMI positive: {source.kpi.romi_positive}%
ROMI negative: {source.kpi.romi_negative}%

💡 Задать KPI:
/rid_kpi_positive_{source.rid} число
/rid_kpi_negative_{source.rid} число
"""
