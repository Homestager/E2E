"""
Генератор ГРАФИК 2 - Аналитика по конкретной кампании
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from typing import List, Dict
from datetime import datetime
from collections import defaultdict

from .base_chart import BaseChart, PieChart, BarChart, HeatmapChart, COLORS, PALETTE
from ..models.data_models import Campaign, Source, DailyMetrics
from ..anomalies.detector import AnomalyDetector
from ..anomalies.period_comparison import PeriodComparer
from ..formatters.text_formatter import TextFormatter


class Chart2Generator(BaseChart):
    """Генератор графика 2 - Аналитика по кампании"""
    
    def __init__(self):
        super().__init__(figsize=(20, 32), dpi=120)
        self.campaign: Campaign = None
        self.anomaly_detector = AnomalyDetector()
        self.period_comparer = PeriodComparer()
    
    def generate(self, campaign: Campaign, output_path: str):
        """Генерировать полный отчет - График 2"""
        self.campaign = campaign
        
        # Создать фигуру с подграфиками
        self.fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        # Создать сетку для размещения графиков
        gs = self.fig.add_gridspec(14, 2, hspace=0.45, wspace=0.3)
        
        # 1. Шапка с основными метриками
        ax_header = self.fig.add_subplot(gs[0, :])
        self._plot_header(ax_header)
        
        # 2. Выручка по источникам (RID) в динамике + пирог
        ax_revenue_sources = self.fig.add_subplot(gs[1, 0])
        ax_pie_sources = self.fig.add_subplot(gs[1, 1])
        self._plot_revenue_by_sources(ax_revenue_sources)
        self._plot_revenue_pie_sources(ax_pie_sources)
        
        # 3. Выручка по соцсетям в динамике + пирог
        ax_revenue_socials = self.fig.add_subplot(gs[2, 0])
        ax_pie_socials = self.fig.add_subplot(gs[2, 1])
        self._plot_revenue_by_socials(ax_revenue_socials)
        self._plot_revenue_pie_socials(ax_pie_socials)
        
        # 4. Распределение бюджета
        ax_budget_socials = self.fig.add_subplot(gs[3, 0])
        ax_budget_sources = self.fig.add_subplot(gs[3, 1])
        self._plot_budget_distribution_socials(ax_budget_socials)
        self._plot_budget_distribution_sources(ax_budget_sources)
        
        # 5. Средний LTV по источникам
        ax_ltv = self.fig.add_subplot(gs[4, :])
        self._plot_ltv_by_sources(ax_ltv)
        
        # 6. Сравнение ROMI по источникам (с KPI линиями)
        ax_romi_sources = self.fig.add_subplot(gs[5, :])
        self._plot_romi_comparison_sources(ax_romi_sources)
        
        # 7. Сравнение ROMI по соцсетям (с KPI линиями)
        ax_romi_socials = self.fig.add_subplot(gs[6, :])
        self._plot_romi_comparison_socials(ax_romi_socials)
        
        # 8. Стоимость лида по источникам
        ax_cpl = self.fig.add_subplot(gs[7, :])
        self._plot_cpl_by_sources(ax_cpl)
        
        # 9. Стоимость клиента (CAC) по источникам
        ax_cac = self.fig.add_subplot(gs[8, :])
        self._plot_cac_by_sources(ax_cac)
        
        # 10. Стоимость клика (CPA) по источникам
        ax_cpa = self.fig.add_subplot(gs[9, :])
        self._plot_cpa_by_sources(ax_cpa)
        
        # 11. Сравнение CAC / CPL / CPA по источникам (воронка)
        ax_funnel_costs = self.fig.add_subplot(gs[10, :])
        self._plot_funnel_costs_comparison(ax_funnel_costs)
        
        # 12. CR (C→S) по источникам
        ax_cr_cs = self.fig.add_subplot(gs[11, :])
        self._plot_cr_cs_by_sources(ax_cr_cs)
        
        # 13. CR (C→L) по источникам
        ax_cr_cl = self.fig.add_subplot(gs[12, :])
        self._plot_cr_cl_by_sources(ax_cr_cl)
        
        # 14. CR (L→S) по источникам
        ax_cr_ls = self.fig.add_subplot(gs[13, :])
        self._plot_cr_ls_by_sources(ax_cr_ls)
        
        # Сохранить
        self.save(output_path)
    
    def _plot_header(self, ax):
        """Отобразить шапку с метриками кампании"""
        ax.axis('off')
        
        c = self.campaign
        header_text = TextFormatter.format_header(c)
        
        ax.text(0.02, 0.5, header_text, 
               horizontalalignment='left',
               verticalalignment='center',
               fontsize=10,
               fontfamily='monospace',
               transform=ax.transAxes)
    
    def _plot_revenue_by_sources(self, ax):
        """График выручки по источникам в динамике"""
        dates_dict = defaultdict(lambda: defaultdict(float))
        
        for source in self.campaign.sources:
            for metric in source.daily_metrics:
                dates_dict[metric.date][source.name] += metric.revenue
        
        if not dates_dict:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        dates = sorted(dates_dict.keys())
        sources = [s.name for s in self.campaign.sources[:8]]  # Макс 8 источников
        
        for i, source in enumerate(sources):
            values = [dates_dict[d].get(source, 0) for d in dates]
            if sum(values) > 0:
                ax.plot(dates, values, label=source[:20], color=PALETTE[i % len(PALETTE)], 
                       alpha=0.7, linewidth=2)
        
        # Столбики общего количества продаж на фоне
        all_metrics = []
        for source in self.campaign.sources:
            all_metrics.extend(source.daily_metrics)
        
        sales_by_date = defaultdict(int)
        for m in all_metrics:
            sales_by_date[m.date] += m.sales
        
        sales_values = [sales_by_date[d] for d in dates]
        ax2 = ax.twinx()
        ax2.bar(dates, sales_values, alpha=0.15, color='gray', width=0.8, label='Продажи')
        ax2.set_ylabel('Продажи (шт)', fontsize=9, color='gray')
        ax2.tick_params(axis='y', labelcolor='gray')
        
        ax.set_xlabel('Дата', fontsize=10)
        ax.set_ylabel('Выручка (₽)', fontsize=10)
        ax.set_title('Выручка по источникам (динамика)', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=7, ncol=2)
        ax.grid(True, alpha=0.3)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_revenue_pie_sources(self, ax):
        """Пирог распределения выручки по источникам"""
        data = {s.name[:20]: s.total_revenue for s in self.campaign.sources if s.total_revenue > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        # Показывать топ-10
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:10]
        data = dict(sorted_data)
        
        pie_chart = PieChart()
        pie_chart.plot(data, 'Доля выручки по источникам', ax)
    
    def _plot_revenue_by_socials(self, ax):
        """График выручки по соцсетям в динамике"""
        dates_dict = defaultdict(lambda: defaultdict(float))
        
        for source in self.campaign.sources:
            for metric in source.daily_metrics:
                dates_dict[metric.date][source.social_network.value] += metric.revenue
        
        if not dates_dict:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        dates = sorted(dates_dict.keys())
        socials = list(set(s.social_network.value for s in self.campaign.sources))
        
        for i, social in enumerate(socials):
            values = [dates_dict[d].get(social, 0) for d in dates]
            if sum(values) > 0:
                ax.plot(dates, values, label=social, color=PALETTE[i % len(PALETTE)], 
                       alpha=0.7, linewidth=2)
        
        ax.set_xlabel('Дата', fontsize=10)
        ax.set_ylabel('Выручка (₽)', fontsize=10)
        ax.set_title('Выручка по соцсетям (динамика)', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_revenue_pie_socials(self, ax):
        """Пирог распределения выручки по соцсетям"""
        data = defaultdict(float)
        for source in self.campaign.sources:
            data[source.social_network.value] += source.total_revenue
        
        data = {k: v for k, v in data.items() if v > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        pie_chart = PieChart()
        pie_chart.plot(data, 'Доля выручки по соцсетям', ax)
    
    def _plot_budget_distribution_socials(self, ax):
        """Распределение бюджета по соцсетям"""
        data = defaultdict(float)
        for source in self.campaign.sources:
            data[source.social_network.value] += source.total_spend
        
        data = {k: v for k, v in data.items() if v > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        pie_chart = PieChart()
        pie_chart.plot(data, 'Распределение бюджета по соцсетям', ax)
    
    def _plot_budget_distribution_sources(self, ax):
        """Распределение бюджета по источникам"""
        data = {s.name[:20]: s.total_spend for s in self.campaign.sources if s.total_spend > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        # Показывать топ-10
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:10]
        data = dict(sorted_data)
        
        pie_chart = PieChart()
        pie_chart.plot(data, 'Распределение бюджета по источникам (топ-10)', ax)
    
    def _plot_ltv_by_sources(self, ax):
        """Средний LTV по источникам"""
        data = {s.name[:25]: s.avg_ltv for s in self.campaign.sources if s.total_sales > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        # Топ-15
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:15]
        data = dict(sorted_data)
        
        bar_chart = BarChart()
        bar_chart.plot_horizontal(data, 'Средний LTV по источникам (топ-15)', 'LTV (₽)', ax=ax)
    
    def _plot_romi_comparison_sources(self, ax):
        """Сравнение ROMI по источникам с KPI линиями"""
        sources = sorted(self.campaign.sources, key=lambda s: s.avg_romi, reverse=True)[:20]
        
        names = [s.name[:25] for s in sources]
        romi_values = [s.avg_romi for s in sources]
        spend_values = [s.total_spend / 1000 for s in sources]  # В тысячах
        
        x = np.arange(len(names))
        width = 0.35
        
        # Цвета столбов в зависимости от ROMI
        colors = []
        for romi in romi_values:
            if self.campaign.kpi_romi_positive and romi >= self.campaign.kpi_romi_positive:
                colors.append(COLORS['success'])
            elif self.campaign.kpi_romi_negative and romi < self.campaign.kpi_romi_negative:
                colors.append(COLORS['danger'])
            else:
                colors.append(COLORS['warning'])
        
        bars1 = ax.bar(x - width/2, romi_values, width, label='ROMI (%)', 
                      color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax2 = ax.twinx()
        bars2 = ax2.bar(x + width/2, spend_values, width, label='Расход (тыс ₽)', 
                       color=COLORS['gray'], alpha=0.5)
        
        # Добавить линии KPI
        if self.campaign.kpi_romi_positive:
            ax.axhline(y=self.campaign.kpi_romi_positive, color=COLORS['success'], 
                      linestyle='--', linewidth=2, alpha=0.7, label=f'KPI+ ({self.campaign.kpi_romi_positive:.0f}%)')
        if self.campaign.kpi_romi_negative:
            ax.axhline(y=self.campaign.kpi_romi_negative, color=COLORS['danger'], 
                      linestyle='--', linewidth=2, alpha=0.7, label=f'KPI- ({self.campaign.kpi_romi_negative:.0f}%)')
        
        ax.set_xlabel('Источник', fontsize=10)
        ax.set_ylabel('ROMI (%)', fontsize=10)
        ax2.set_ylabel('Расход (тыс ₽)', fontsize=10, color=COLORS['gray'])
        ax.set_title('Сравнение ROMI по источникам (с KPI)', fontsize=12, fontweight='bold')
        
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=7)
        
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend(loc='upper left', fontsize=8)
        ax2.legend(loc='upper right', fontsize=8)
    
    def _plot_romi_comparison_socials(self, ax):
        """Сравнение ROMI по соцсетям с KPI"""
        social_stats = defaultdict(lambda: {'revenue': 0, 'spend': 0, 'leads': 0})
        
        for source in self.campaign.sources:
            sn = source.social_network.value
            social_stats[sn]['revenue'] += source.total_revenue
            social_stats[sn]['spend'] += source.total_spend
            social_stats[sn]['leads'] += source.total_leads
        
        names = []
        romi_values = []
        cpl_values = []
        
        for sn, stats in social_stats.items():
            if stats['spend'] > 0:
                names.append(sn)
                romi = ((stats['revenue'] - stats['spend']) / stats['spend']) * 100
                cpl = stats['spend'] / stats['leads'] if stats['leads'] > 0 else 0
                romi_values.append(romi)
                cpl_values.append(cpl)
        
        if not names:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        y = np.arange(len(names))
        height = 0.35
        
        # Цвета в зависимости от ROMI
        colors = []
        for romi in romi_values:
            if self.campaign.kpi_romi_positive and romi >= self.campaign.kpi_romi_positive:
                colors.append(COLORS['success'])
            elif self.campaign.kpi_romi_negative and romi < self.campaign.kpi_romi_negative:
                colors.append(COLORS['danger'])
            else:
                colors.append(COLORS['warning'])
        
        bars1 = ax.barh(y - height/2, romi_values, height, label='ROMI (%)', 
                       color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax2 = ax.twiny()
        bars2 = ax2.barh(y + height/2, cpl_values, height, label='CPL (₽)', 
                        color=COLORS['secondary'], alpha=0.6)
        
        # Добавить вертикальные линии KPI
        if self.campaign.kpi_romi_positive:
            ax.axvline(x=self.campaign.kpi_romi_positive, color=COLORS['success'], 
                      linestyle='--', linewidth=2, alpha=0.7)
        if self.campaign.kpi_romi_negative:
            ax.axvline(x=self.campaign.kpi_romi_negative, color=COLORS['danger'], 
                      linestyle='--', linewidth=2, alpha=0.7)
        
        ax.set_yticks(y)
        ax.set_yticklabels(names)
        ax.set_xlabel('ROMI (%)', fontsize=10)
        ax2.set_xlabel('CPL (₽)', fontsize=10, color=COLORS['secondary'])
        ax.set_title('ROMI и CPL по соцсетям (с KPI)', fontsize=12, fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='x')
        ax.legend(loc='lower right', fontsize=9)
        ax2.legend(loc='upper right', fontsize=9)
    
    def _plot_cpl_by_sources(self, ax):
        """Стоимость лида по источникам"""
        sources = [s for s in self.campaign.sources if s.total_leads > 0]
        sources = sorted(sources, key=lambda s: s.avg_cpl)[:20]
        
        names = [s.name[:25] for s in sources]
        cpl_values = [s.avg_cpl for s in sources]
        
        # Цвета в зависимости от KPI
        colors = []
        for cpl in cpl_values:
            if self.campaign.kpi_cpl_positive and cpl <= self.campaign.kpi_cpl_positive:
                colors.append(COLORS['success'])
            elif self.campaign.kpi_cpl_negative and cpl >= self.campaign.kpi_cpl_negative:
                colors.append(COLORS['danger'])
            else:
                colors.append(COLORS['primary'])
        
        y = np.arange(len(names))
        bars = ax.barh(y, cpl_values, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Добавить линии KPI
        if self.campaign.kpi_cpl_positive:
            ax.axvline(x=self.campaign.kpi_cpl_positive, color=COLORS['success'], 
                      linestyle='--', linewidth=2, alpha=0.7, label=f'KPI+ ({self.campaign.kpi_cpl_positive:.0f} ₽)')
        if self.campaign.kpi_cpl_negative:
            ax.axvline(x=self.campaign.kpi_cpl_negative, color=COLORS['danger'], 
                      linestyle='--', linewidth=2, alpha=0.7, label=f'KPI- ({self.campaign.kpi_cpl_negative:.0f} ₽)')
        
        ax.set_yticks(y)
        ax.set_yticklabels(names, fontsize=8)
        ax.invert_yaxis()
        ax.set_xlabel('CPL (₽)', fontsize=10)
        ax.set_title('Стоимость лида по источникам (с KPI)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        if self.campaign.kpi_cpl_positive or self.campaign.kpi_cpl_negative:
            ax.legend(loc='lower right', fontsize=9)
    
    def _plot_cac_by_sources(self, ax):
        """Стоимость клиента (CAC) по источникам"""
        data = {s.name[:25]: s.avg_cac for s in self.campaign.sources if s.total_sales > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        sorted_data = sorted(data.items(), key=lambda x: x[1])[:20]
        data = dict(sorted_data)
        
        bar_chart = BarChart()
        bar_chart.plot_horizontal(data, 'Стоимость клиента (CAC) по источникам', 'CAC (₽)', ax=ax)
    
    def _plot_cpa_by_sources(self, ax):
        """Стоимость клика (CPA) по источникам"""
        data = {s.name[:25]: s.avg_cpa for s in self.campaign.sources if s.total_clicks > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        sorted_data = sorted(data.items(), key=lambda x: x[1])[:20]
        data = dict(sorted_data)
        
        bar_chart = BarChart()
        bar_chart.plot_horizontal(data, 'Стоимость клика (CPA) по источникам', 'CPA (₽)', ax=ax)
    
    def _plot_funnel_costs_comparison(self, ax):
        """Сравнение CAC / CPL / CPA - анализ воронки"""
        sources = [s for s in self.campaign.sources if s.total_clicks > 0 and s.total_sales > 0][:15]
        
        if not sources:
            ax.text(0.5, 0.5, 'Нет данных для анализа воронки', ha='center', va='center')
            ax.axis('off')
            return
        
        names = [s.name[:20] for s in sources]
        cpa_values = [s.avg_cpa for s in sources]
        cpl_values = [s.avg_cpl for s in sources]
        cac_values = [s.avg_cac for s in sources]
        
        x = np.arange(len(names))
        width = 0.25
        
        bars1 = ax.bar(x - width, cpa_values, width, label='CPA (клик)', 
                      color=COLORS['info'], alpha=0.8)
        bars2 = ax.bar(x, cpl_values, width, label='CPL (лид)', 
                      color=COLORS['warning'], alpha=0.8)
        bars3 = ax.bar(x + width, cac_values, width, label='CAC (клиент)', 
                      color=COLORS['danger'], alpha=0.8)
        
        ax.set_xlabel('Источник', fontsize=10)
        ax.set_ylabel('Стоимость (₽)', fontsize=10)
        ax.set_title('Анализ воронки: CPA → CPL → CAC', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=7)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Добавить пояснение
        ax.text(0.02, 0.98, 
               'Если CPA низкий, а CPL и CAC высокие → проблема в воронке конверсии',
               transform=ax.transAxes, fontsize=8, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    def _plot_cr_cs_by_sources(self, ax):
        """CR (C→S) по источникам"""
        data = {}
        for s in self.campaign.sources:
            if s.total_clicks > 0:
                cr = (s.total_sales / s.total_clicks) * 100
                data[s.name[:25]] = cr
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:20]
        data = dict(sorted_data)
        
        bar_chart = BarChart()
        bar_chart.plot_horizontal(data, 'Конверсия C→S по источникам', 'CR (%)', ax=ax)
    
    def _plot_cr_cl_by_sources(self, ax):
        """CR (C→L) по источникам"""
        data = {}
        for s in self.campaign.sources:
            if s.total_clicks > 0:
                cr = (s.total_leads / s.total_clicks) * 100
                data[s.name[:25]] = cr
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:20]
        data = dict(sorted_data)
        
        bar_chart = BarChart()
        bar_chart.plot_horizontal(data, 'Конверсия C→L по источникам', 'CR (%)', ax=ax)
    
    def _plot_cr_ls_by_sources(self, ax):
        """CR (L→S) по источникам"""
        data = {}
        for s in self.campaign.sources:
            if s.total_leads > 0:
                cr = (s.total_sales / s.total_leads) * 100
                data[s.name[:25]] = cr
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:20]
        data = dict(sorted_data)
        
        bar_chart = BarChart()
        bar_chart.plot_horizontal(data, 'Конверсия L→S по источникам', 'CR (%)', ax=ax)
