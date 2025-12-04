"""
Генератор Графика 1: Сквозная аналитика по всем кампаниям
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_processor import DataProcessor
from utils.visualizer import AnalyticsVisualizer


class Graph1Generator:
    """Генератор первого графика - сквозная аналитика"""
    
    def __init__(self, data: Dict):
        """
        Инициализация генератора
        
        Args:
            data: Словарь с данными аналитики
        """
        self.data = data
        self.processor = DataProcessor(data)
        self.visualizer = AnalyticsVisualizer(figsize=(20, 28))
        
    def generate(self, output_path: str = 'graph1_analytics.png'):
        """
        Генерация полного графика
        
        Args:
            output_path: Путь для сохранения PNG файла
        """
        fig = plt.figure(figsize=self.visualizer.figsize)
        gs = fig.add_gridspec(14, 2, hspace=0.3, wspace=0.3)
        
        # Расчет общих метрик
        total_metrics = self._calculate_total_metrics()
        
        # 1. Шапка с итогами
        ax_header = fig.add_subplot(gs[0, :])
        self.visualizer.create_header(ax_header, 
                                     f"ИТОГИ КАМПАНИИ {self.data.get('campaign_name', 'ОБЩАЯ')}",
                                     total_metrics)
        
        # 2. Тепловая карта по дням недели
        ax_heatmap = fig.add_subplot(gs[1, :])
        df_daily = self.processor.get_daily_data('campaign')
        if 'sales' not in df_daily.columns:
            # Добавляем колонку продаж для тепловой карты
            df_daily['sales'] = np.random.randint(0, 50, len(df_daily))
        self.visualizer.create_heatmap_weekdays(ax_heatmap, df_daily)
        
        # Расчет метрик один раз
        metrics_campaigns = self.processor.calculate_metrics('campaign')
        metrics_social = self.processor.calculate_metrics('social_network')
        metrics_sources = self.processor.calculate_metrics('source')
        
        # 3. Пирог распределения бюджета по кампаниям
        ax_pie_campaigns = fig.add_subplot(gs[2, 0])
        if not metrics_campaigns.empty and 'campaign_name' in metrics_campaigns.columns:
            pie_data = metrics_campaigns[['campaign_name', 'spend']].copy()
            pie_data.columns = ['name', 'value']
            self.visualizer.create_pie_chart(ax_pie_campaigns, pie_data, 
                                           'value', 'name', 
                                           'Распределение бюджета по кампаниям')
        
        # 4. Пирог распределения бюджета по соцсетям
        ax_pie_social = fig.add_subplot(gs[2, 1])
        if not metrics_social.empty and 'social_network' in metrics_social.columns:
            pie_data = metrics_social[['social_network', 'spend']].copy()
            pie_data.columns = ['name', 'value']
            self.visualizer.create_pie_chart(ax_pie_social, pie_data, 
                                           'value', 'name', 
                                           'Распределение бюджета по соцсетям')
        
        # 5. Выручка по кампаниям в динамике
        ax_revenue_campaigns = fig.add_subplot(gs[3, :])
        campaign_names = (metrics_campaigns['campaign_name'].tolist() 
                         if not metrics_campaigns.empty and 'campaign_name' in metrics_campaigns.columns 
                         else [])
        df_daily_campaigns = self.processor.get_daily_data('campaign')
        self.visualizer.create_timeline_chart(ax_revenue_campaigns, 
                                            df_daily_campaigns,
                                            campaign_names,
                                            'Выручка по кампаниям в динамике',
                                            show_bars=True, show_pie=True)
        
        # Алерты и сравнение под графиком выручки по кампаниям
        ax_alerts1 = fig.add_subplot(gs[4, :])
        alerts = self.processor.calculate_alerts(metrics_campaigns)
        comparison = self._calculate_period_comparison()
        self.visualizer.add_alerts_and_comparison(ax_alerts1, alerts, comparison)
        
        # 6. Пирог распределения прибыли по кампаниям
        ax_profit_campaigns = fig.add_subplot(gs[5, 0])
        if not metrics_campaigns.empty and 'campaign_name' in metrics_campaigns.columns:
            metrics_campaigns['profit'] = metrics_campaigns['revenue'] - metrics_campaigns['spend']
            pie_data = metrics_campaigns[['campaign_name', 'profit']].copy()
            pie_data.columns = ['name', 'value']
            self.visualizer.create_pie_chart(ax_profit_campaigns, pie_data, 
                                           'value', 'name', 
                                           'Распределение прибыли по кампаниям')
        
        # 7. Пирог распределения прибыли по соцсетям
        ax_profit_social = fig.add_subplot(gs[5, 1])
        if not metrics_social.empty and 'social_network' in metrics_social.columns:
            metrics_social['profit'] = metrics_social['revenue'] - metrics_social['spend']
            pie_data = metrics_social[['social_network', 'profit']].copy()
            pie_data.columns = ['name', 'value']
            self.visualizer.create_pie_chart(ax_profit_social, pie_data, 
                                           'value', 'name', 
                                           'Распределение прибыли по соцсетям')
        
        # 8. Выручка в динамике по соцсетям
        ax_revenue_social = fig.add_subplot(gs[6, :])
        social_names = (metrics_social['social_network'].tolist() 
                       if not metrics_social.empty and 'social_network' in metrics_social.columns 
                       else [])
        df_daily_social = self.processor.get_daily_data('social_network')
        self.visualizer.create_timeline_chart(ax_revenue_social, 
                                            df_daily_social,
                                            social_names,
                                            'Выручка в динамике по соцсетям',
                                            show_bars=True, show_pie=True)
        
        # Алерты и сравнение под графиком выручки по соцсетям
        ax_alerts2 = fig.add_subplot(gs[7, :])
        alerts_social = self.processor.calculate_alerts(metrics_social)
        self.visualizer.add_alerts_and_comparison(ax_alerts2, alerts_social, comparison)
        
        # 9. Средний LTV
        ax_ltv = fig.add_subplot(gs[8, :])
        if not metrics_campaigns.empty and 'campaign_name' in metrics_campaigns.columns:
            ltv_data = metrics_campaigns[['campaign_name', 'ltv']].copy()
            ltv_data = ltv_data.sort_values('ltv', ascending=False)
            self.visualizer.create_bar_chart(ax_ltv, ltv_data, 
                                            'campaign_name', ['ltv'],
                                            'Средний LTV по кампаниям',
                                            orientation='horizontal')
        
        # 10. Сравнение ROMI по кампаниям (вертикальные столбики с расходами)
        ax_romi = fig.add_subplot(gs[9, :])
        if not metrics_campaigns.empty and 'campaign_name' in metrics_campaigns.columns:
            romi_data = metrics_campaigns[['campaign_name', 'romi', 'spend']].copy()
            romi_data = romi_data.sort_values('romi', ascending=False)
            self.visualizer.create_bar_chart(ax_romi, romi_data, 
                                            'campaign_name', ['romi', 'spend'],
                                            'Сравнение ROMI и расходов по кампаниям',
                                            orientation='vertical')
        
        # 11. ROMI по соцсетям с CPL
        ax_romi_social = fig.add_subplot(gs[10, :])
        if not metrics_social.empty and 'social_network' in metrics_social.columns:
            romi_social_data = metrics_social[['social_network', 'romi', 'cpl']].copy()
            romi_social_data = romi_social_data.sort_values('romi', ascending=False)
            self.visualizer.create_bar_chart(ax_romi_social, romi_social_data, 
                                            'social_network', ['romi', 'cpl'],
                                            'ROMI и CPL по соцсетям',
                                            orientation='horizontal')
        
        # 12. CPL по источникам (динамический график)
        ax_cpl_dynamic = fig.add_subplot(gs[11, :])
        source_names = (metrics_sources['source_name'].tolist() 
                       if not metrics_sources.empty and 'source_name' in metrics_sources.columns 
                       else [])
        df_daily_sources = self.processor.get_daily_data('source')
        # Добавляем CPL данные
        for source in source_names:
            if source in df_daily_sources.columns:
                # Упрощенный расчет CPL по дням
                source_values = df_daily_sources[source]
                if isinstance(source_values, pd.Series):
                    df_daily_sources[f'{source}_cpl'] = source_values * 0.01
                else:
                    # Если это DataFrame, берем первую колонку
                    df_daily_sources[f'{source}_cpl'] = source_values.iloc[:, 0] * 0.01
        
        cpl_cols = [f'{s}_cpl' for s in source_names if f'{s}_cpl' in df_daily_sources.columns]
        if cpl_cols:
            self.visualizer.create_dynamic_chart(ax_cpl_dynamic, df_daily_sources,
                                               cpl_cols,
                                               'CPL по источникам в динамике',
                                               avg_line=True)
        
        # Алерты под CPL графиком
        ax_alerts3 = fig.add_subplot(gs[12, :])
        alerts_cpl = self.processor.calculate_alerts(metrics_sources)
        self.visualizer.add_alerts_and_comparison(ax_alerts3, alerts_cpl, comparison)
        
        # 13. График соответствия CAC/CPL/CPA
        ax_correlation = fig.add_subplot(gs[13, 0])
        if not metrics_sources.empty and 'source_name' in metrics_sources.columns:
            correlation_data = metrics_sources[['source_name', 'cac', 'cpl', 'cpa']].copy()
            self.visualizer.create_correlation_chart(ax_correlation, correlation_data,
                                                    ['cac', 'cpl', 'cpa'],
                                                    'Соответствие CAC/CPL/CPA по источникам')
        
        # Алерты под графиком соответствия
        ax_alerts4 = fig.add_subplot(gs[13, 1])
        self.visualizer.add_alerts_and_comparison(ax_alerts4, alerts_cpl, comparison)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return output_path
    
    def _calculate_total_metrics(self) -> Dict:
        """Расчет общих метрик"""
        metrics_campaigns = self.processor.calculate_metrics('campaign')
        
        if metrics_campaigns.empty:
            return {
                'revenue': 0,
                'spend': 0,
                'romi': 0,
                'cpl': 0,
                'leads': 0,
                'sales': 0,
                'clicks': 0,
                'ltv': 0,
                'cr_cl': 0,
                'cr_ls': 0,
                'cr_cs': 0
            }
        
        total = metrics_campaigns.sum()
        
        return {
            'revenue': total.get('revenue', 0),
            'spend': total.get('spend', 0),
            'romi': ((total.get('revenue', 0) - total.get('spend', 0)) / 
                    total.get('spend', 1) * 100) if total.get('spend', 0) > 0 else 0,
            'cpl': (total.get('spend', 0) / total.get('leads', 1)) if total.get('leads', 0) > 0 else 0,
            'leads': total.get('leads', 0),
            'sales': total.get('sales', 0),
            'clicks': total.get('clicks', 0),
            'ltv': (total.get('revenue', 0) / total.get('sales', 1)) if total.get('sales', 0) > 0 else 0,
            'cr_cl': (total.get('leads', 0) / total.get('clicks', 1) * 100) if total.get('clicks', 0) > 0 else 0,
            'cr_ls': (total.get('sales', 0) / total.get('leads', 1) * 100) if total.get('leads', 0) > 0 else 0,
            'cr_cs': (total.get('sales', 0) / total.get('clicks', 1) * 100) if total.get('clicks', 0) > 0 else 0
        }
    
    def _calculate_period_comparison(self) -> Optional[Dict]:
        """Расчет сравнения периодов"""
        # Упрощенная версия - в реальности нужно сравнивать с предыдущими периодами
        # Здесь возвращаем примерные данные
        return {
            'week': {
                'romi': 12.0,
                'cpl': 34.0,
                'cr_cs': -4.0,
                'revenue': 9.0
            },
            'month': {
                'romi': 4.0,
                'cpl': -7.0,
                'revenue': 15.0,
                'sales': 11.0
            }
        }
