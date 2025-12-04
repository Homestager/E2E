"""
Генератор ГРАФИК 1 - Сквозная аналитика по всем кампаниям
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict

from .base_chart import BaseChart, PieChart, BarChart, HeatmapChart, COLORS, PALETTE
from ..models.data_models import AnalyticsPeriod, Campaign, SocialNetwork, DailyMetrics
from ..anomalies.detector import AnomalyDetector
from ..anomalies.period_comparison import PeriodComparer
from ..formatters.text_formatter import TextFormatter


class Chart1Generator(BaseChart):
    """Генератор графика 1 - Сквозная аналитика"""
    
    def __init__(self):
        super().__init__(figsize=(20, 28), dpi=120)
        self.period: AnalyticsPeriod = None
        self.anomaly_detector = AnomalyDetector()
        self.period_comparer = PeriodComparer()
    
    def generate(self, period: AnalyticsPeriod, output_path: str):
        """Генерировать полный отчет - График 1"""
        self.period = period
        
        # Создать фигуру с подграфиками
        self.fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        # Создать сетку для размещения графиков
        gs = self.fig.add_gridspec(10, 2, hspace=0.4, wspace=0.3)
        
        # 1. Шапка с основными метриками (текстовый блок)
        ax_header = self.fig.add_subplot(gs[0, :])
        self._plot_header(ax_header)
        
        # 2. Тепловая карта по дням недели
        ax_heatmap = self.fig.add_subplot(gs[1, :])
        self._plot_weekday_heatmap(ax_heatmap)
        
        # 3. Выручка по кампаниям в динамике + пирог
        ax_revenue_campaigns = self.fig.add_subplot(gs[2, 0])
        ax_pie_campaigns = self.fig.add_subplot(gs[2, 1])
        self._plot_revenue_by_campaigns(ax_revenue_campaigns)
        self._plot_revenue_pie_campaigns(ax_pie_campaigns)
        
        # 4. Выручка по соцсетям в динамике + пирог
        ax_revenue_socials = self.fig.add_subplot(gs[3, 0])
        ax_pie_socials = self.fig.add_subplot(gs[3, 1])
        self._plot_revenue_by_socials(ax_revenue_socials)
        self._plot_revenue_pie_socials(ax_pie_socials)
        
        # 5. Распределение бюджета
        ax_budget_socials = self.fig.add_subplot(gs[4, 0])
        ax_budget_campaigns = self.fig.add_subplot(gs[4, 1])
        self._plot_budget_distribution_socials(ax_budget_socials)
        self._plot_budget_distribution_campaigns(ax_budget_campaigns)
        
        # 6. Средний LTV по кампаниям
        ax_ltv = self.fig.add_subplot(gs[5, :])
        self._plot_ltv_by_campaigns(ax_ltv)
        
        # 7. Сравнение ROMI по кампаниям
        ax_romi = self.fig.add_subplot(gs[6, :])
        self._plot_romi_comparison_campaigns(ax_romi)
        
        # 8. ROMI по соцсетям с CPL
        ax_romi_socials = self.fig.add_subplot(gs[7, :])
        self._plot_romi_socials_with_cpl(ax_romi_socials)
        
        # 9. Стоимость лида по кампаниям
        ax_cpl = self.fig.add_subplot(gs[8, :])
        self._plot_cpl_by_campaigns(ax_cpl)
        
        # 10. CR (C→S) по кампаниям
        ax_cr = self.fig.add_subplot(gs[9, :])
        self._plot_cr_cs_by_campaigns(ax_cr)
        
        # Сохранить
        self.save(output_path)
    
    def _plot_header(self, ax):
        """Отобразить шапку с метриками"""
        ax.axis('off')
        
        # Основные метрики
        revenue = self.period.total_revenue
        spend = self.period.total_spend
        leads = self.period.total_leads
        sales = self.period.total_sales
        clicks = self.period.total_clicks
        romi = self.period.avg_romi
        cpl = self.period.avg_cpl
        
        ltv = revenue / sales if sales > 0 else 0
        cr_cl = (leads / clicks * 100) if clicks > 0 else 0
        cr_ls = (sales / leads * 100) if leads > 0 else 0
        cr_cs = (sales / clicks * 100) if clicks > 0 else 0
        
        header_text = f"""
════════════════════════════════════════════════════════════════════════════
                          СКВОЗНАЯ АНАЛИТИКА
        {self.period.start_date.strftime('%Y-%m-%d')} — {self.period.end_date.strftime('%Y-%m-%d')}
════════════════════════════════════════════════════════════════════════════
 Выручка: {TextFormatter.format_money(revenue):<20}  ROMI: {romi:.0f}%
 Расходы: {TextFormatter.format_money(spend):<20}  CPL: {cpl:.0f} ₽
 Лиды: {leads:<25}  LTV: {ltv:.0f} ₽
 Продажи: {sales:<22}  Клики: {clicks}
════════════════════════════════════════════════════════════════════════════
   CR(C→L): {cr_cl:.2f}%   |   CR(L→S): {cr_ls:.2f}%   |   CR(C→S): {cr_cs:.2f}%
════════════════════════════════════════════════════════════════════════════
        """
        
        ax.text(0.5, 0.5, header_text, 
               horizontalalignment='center',
               verticalalignment='center',
               fontsize=11,
               fontfamily='monospace',
               transform=ax.transAxes)
    
    def _plot_weekday_heatmap(self, ax):
        """Тепловая карта по дням недели"""
        # Собрать данные по дням недели
        weekday_data = defaultdict(lambda: defaultdict(int))
        
        for campaign in self.period.campaigns:
            for source in campaign.sources:
                for metric in source.daily_metrics:
                    weekday = metric.date.weekday()  # 0=Пн, 6=Вс
                    hour_bucket = metric.date.hour if hasattr(metric.date, 'hour') else 12
                    weekday_data[weekday][campaign.name] = weekday_data[weekday].get(campaign.name, 0) + metric.sales
        
        # Преобразовать в матрицу
        weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        campaigns = list(set(c.name for c in self.period.campaigns))[:10]  # Макс 10 кампаний
        
        if not campaigns:
            ax.text(0.5, 0.5, 'Нет данных для отображения', ha='center', va='center')
            ax.axis('off')
            return
        
        data_matrix = np.zeros((len(weekdays), len(campaigns)))
        
        for i, weekday_idx in enumerate(range(7)):
            for j, campaign in enumerate(campaigns):
                data_matrix[i, j] = weekday_data[weekday_idx].get(campaign, 0)
        
        # Построить тепловую карту
        im = ax.imshow(data_matrix, cmap='YlOrRd', aspect='auto')
        
        ax.set_xticks(np.arange(len(campaigns)))
        ax.set_yticks(np.arange(len(weekdays)))
        ax.set_xticklabels([c[:15] for c in campaigns], rotation=45, ha='right')
        ax.set_yticklabels(weekdays)
        
        ax.set_title('Тепловая карта продаж по дням недели', fontsize=13, fontweight='bold', pad=15)
        
        # Добавить colorbar
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Продажи', rotation=270, labelpad=20)
    
    def _plot_revenue_by_campaigns(self, ax):
        """График выручки по кампаниям в динамике"""
        dates_dict = defaultdict(lambda: defaultdict(float))
        
        # Собрать данные
        for campaign in self.period.campaigns:
            for source in campaign.sources:
                for metric in source.daily_metrics:
                    dates_dict[metric.date][campaign.name] += metric.revenue
        
        if not dates_dict:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        # Сортировка по датам
        dates = sorted(dates_dict.keys())
        campaigns = [c.name for c in self.period.campaigns][:8]  # Макс 8 кампаний
        
        # Построить кривые
        for i, campaign in enumerate(campaigns):
            values = [dates_dict[d].get(campaign, 0) for d in dates]
            ax.plot(dates, values, label=campaign, color=PALETTE[i % len(PALETTE)], 
                   alpha=0.7, linewidth=2)
        
        # Столбики общего количества продаж
        total_sales = [sum(dates_dict[d].values()) for d in dates]
        ax2 = ax.twinx()
        ax2.bar(dates, [sum(c.total_sales for c in self.period.campaigns) / len(dates)] * len(dates), 
               alpha=0.2, color='gray', width=0.8)
        ax2.set_ylabel('Продажи (шт)', fontsize=10)
        
        ax.set_xlabel('Дата', fontsize=10)
        ax.set_ylabel('Выручка (₽)', fontsize=10)
        ax.set_title('Выручка по кампаниям (динамика)', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
        
        # Форматировать оси
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_revenue_pie_campaigns(self, ax):
        """Пирог распределения выручки по кампаниям"""
        data = {c.name: c.total_revenue for c in self.period.campaigns if c.total_revenue > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        pie_chart = PieChart()
        pie_chart.plot(data, 'Доля выручки по кампаниям', ax)
    
    def _plot_revenue_by_socials(self, ax):
        """График выручки по соцсетям в динамике"""
        dates_dict = defaultdict(lambda: defaultdict(float))
        
        for campaign in self.period.campaigns:
            for source in campaign.sources:
                for metric in source.daily_metrics:
                    dates_dict[metric.date][source.social_network.value] += metric.revenue
        
        if not dates_dict:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        dates = sorted(dates_dict.keys())
        socials = list(SocialNetwork)
        
        for i, social in enumerate(socials):
            values = [dates_dict[d].get(social.value, 0) for d in dates]
            if sum(values) > 0:  # Отображать только если есть данные
                ax.plot(dates, values, label=social.value, color=PALETTE[i % len(PALETTE)], 
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
        data = self.period.get_revenue_by_social()
        data = {k.value: v for k, v in data.items() if v > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        pie_chart = PieChart()
        pie_chart.plot(data, 'Доля выручки по соцсетям', ax)
    
    def _plot_budget_distribution_socials(self, ax):
        """Распределение бюджета по соцсетям"""
        data = self.period.get_spend_by_social()
        data = {k.value: v for k, v in data.items() if v > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        pie_chart = PieChart()
        pie_chart.plot(data, 'Распределение бюджета по соцсетям', ax)
    
    def _plot_budget_distribution_campaigns(self, ax):
        """Распределение бюджета по кампаниям"""
        data = {c.name: c.total_spend for c in self.period.campaigns if c.total_spend > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        pie_chart = PieChart()
        pie_chart.plot(data, 'Распределение бюджета по кампаниям', ax)
    
    def _plot_ltv_by_campaigns(self, ax):
        """Средний LTV по кампаниям (горизонтальный)"""
        data = {c.name: c.avg_ltv for c in self.period.campaigns if c.total_sales > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        bar_chart = BarChart()
        bar_chart.plot_horizontal(data, 'Средний LTV по кампаниям', 'LTV (₽)', ax=ax)
    
    def _plot_romi_comparison_campaigns(self, ax):
        """Сравнение ROMI по кампаниям (вертикальные столбики с расходами)"""
        campaigns = sorted(self.period.campaigns, key=lambda c: c.avg_romi, reverse=True)
        
        names = [c.name[:20] for c in campaigns]
        romi_values = [c.avg_romi for c in campaigns]
        spend_values = [c.total_spend / 1000 for c in campaigns]  # В тысячах
        
        x = np.arange(len(names))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, romi_values, width, label='ROMI (%)', 
                      color=COLORS['success'], alpha=0.8)
        
        ax2 = ax.twinx()
        bars2 = ax2.bar(x + width/2, spend_values, width, label='Расход (тыс ₽)', 
                       color=COLORS['warning'], alpha=0.8)
        
        ax.set_xlabel('Кампания', fontsize=10)
        ax.set_ylabel('ROMI (%)', fontsize=10, color=COLORS['success'])
        ax2.set_ylabel('Расход (тыс ₽)', fontsize=10, color=COLORS['warning'])
        ax.set_title('Сравнение ROMI и расходов по кампаниям', fontsize=12, fontweight='bold')
        
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
        
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
    
    def _plot_romi_socials_with_cpl(self, ax):
        """ROMI по соцсетям с CPL (горизонтальный)"""
        social_stats = {}
        
        for campaign in self.period.campaigns:
            for source in campaign.sources:
                sn = source.social_network.value
                if sn not in social_stats:
                    social_stats[sn] = {'revenue': 0, 'spend': 0, 'leads': 0}
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
        
        bars1 = ax.barh(y - height/2, romi_values, height, label='ROMI (%)', 
                       color=COLORS['primary'], alpha=0.8)
        
        ax2 = ax.twiny()
        bars2 = ax2.barh(y + height/2, cpl_values, height, label='CPL (₽)', 
                        color=COLORS['secondary'], alpha=0.8)
        
        ax.set_yticks(y)
        ax.set_yticklabels(names)
        ax.set_xlabel('ROMI (%)', fontsize=10, color=COLORS['primary'])
        ax2.set_xlabel('CPL (₽)', fontsize=10, color=COLORS['secondary'])
        ax.set_title('ROMI и CPL по соцсетям', fontsize=12, fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='x')
        ax.legend(loc='lower right')
        ax2.legend(loc='upper right')
    
    def _plot_cpl_by_campaigns(self, ax):
        """Стоимость лида по кампаниям (горизонтальный)"""
        data = {c.name: c.avg_cpl for c in self.period.campaigns if c.total_leads > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        bar_chart = BarChart()
        bar_chart.plot_horizontal(data, 'Стоимость лида (CPL) по кампаниям', 'CPL (₽)', ax=ax)
    
    def _plot_cr_cs_by_campaigns(self, ax):
        """CR (C→S) по кампаниям (горизонтальный)"""
        data = {c.name: c.cr_c_s for c in self.period.campaigns if c.total_clicks > 0}
        
        if not data:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center')
            ax.axis('off')
            return
        
        bar_chart = BarChart()
        bar_chart.plot_horizontal(data, 'Конверсия C→S по кампаниям', 'CR (%)', ax=ax)
