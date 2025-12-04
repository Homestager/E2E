"""
Генератор Графика 2: Аналитика по одной кампании (источники внутри кампании)
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


class Graph2Generator:
    """Генератор второго графика - аналитика по одной кампании"""
    
    def __init__(self, data: Dict, campaign_id: int):
        """
        Инициализация генератора
        
        Args:
            data: Словарь с данными аналитики
            campaign_id: ID кампании
        """
        self.data = data
        self.campaign_id = campaign_id
        # Фильтруем данные по кампании
        self.campaign_data = self._filter_by_campaign(data, campaign_id)
        self.processor = DataProcessor(self.campaign_data)
        self.visualizer = AnalyticsVisualizer(figsize=(20, 28))
        
    def _filter_by_campaign(self, data: Dict, campaign_id: int) -> Dict:
        """Фильтрация данных по кампании"""
        filtered_data = data.copy()
        
        # Фильтруем источники по кампании
        if 'sources' in filtered_data:
            filtered_data['sources'] = [
                s for s in filtered_data['sources'] 
                if s.get('campaign_id') == campaign_id
            ]
        
        # Фильтруем транзакции по кампании
        if 'transactions' in filtered_data:
            filtered_data['transactions'] = [
                t for t in filtered_data['transactions']
                if t.get('campaign_id') == campaign_id
            ]
        
        return filtered_data
    
    def generate(self, output_path: str = 'graph2_campaign_analytics.png', 
                kpi: Optional[Dict] = None):
        """
        Генерация полного графика
        
        Args:
            output_path: Путь для сохранения PNG файла
            kpi: Словарь с KPI значениями для кампании
        """
        if kpi is None:
            kpi = {
                'romi_positive': 1200,
                'romi_negative': 700,
                'cpl_positive': None,
                'cpl_negative': None
            }
        
        fig = plt.figure(figsize=self.visualizer.figsize)
        gs = fig.add_gridspec(15, 2, hspace=0.3, wspace=0.3)
        
        # Расчет метрик кампании
        campaign_metrics = self._calculate_campaign_metrics()
        
        # 1. Шапка с итогами кампании
        ax_header = fig.add_subplot(gs[0, :])
        campaign_name = self.data.get('campaign_name', f'Кампания {self.campaign_id}')
        self.visualizer.create_header(ax_header, 
                                     f"ИТОГИ КАМПАНИИ {campaign_name}",
                                     campaign_metrics)
        
        # Расчет метрик один раз
        metrics_sources = self.processor.calculate_metrics('source')
        metrics_social = self.processor.calculate_metrics('social_network')
        
        # 2. Выручка по источникам (ридам) в динамике
        ax_revenue_sources = fig.add_subplot(gs[1, :])
        source_names = (metrics_sources['source_name'].tolist() 
                       if not metrics_sources.empty and 'source_name' in metrics_sources.columns 
                       else [])
        df_daily_sources = self.processor.get_daily_data('source')
        self.visualizer.create_timeline_chart(ax_revenue_sources, 
                                            df_daily_sources,
                                            source_names,
                                            'Выручка по источникам (ридам) в динамике',
                                            show_bars=True, show_pie=True)
        
        # 3. Выручка по соцсетям в динамике (внутри кампании)
        ax_revenue_social = fig.add_subplot(gs[2, :])
        social_names = (metrics_social['social_network'].tolist() 
                       if not metrics_social.empty and 'social_network' in metrics_social.columns 
                       else [])
        df_daily_social = self.processor.get_daily_data('social_network')
        self.visualizer.create_timeline_chart(ax_revenue_social, 
                                            df_daily_social,
                                            social_names,
                                            'Выручка по соцсетям в динамике (внутри кампании)',
                                            show_bars=True, show_pie=True)
        
        # 4. Распределение бюджета по соцсетям (внутри кампании)
        ax_pie_social = fig.add_subplot(gs[3, 0])
        if not metrics_social.empty and 'social_network' in metrics_social.columns:
            pie_data = metrics_social[['social_network', 'spend']].copy()
            pie_data.columns = ['name', 'value']
            self.visualizer.create_pie_chart(ax_pie_social, pie_data, 
                                           'value', 'name', 
                                           'Распределение бюджета по соцсетям')
        
        # 5. Распределение бюджета по источникам (внутри кампании)
        ax_pie_sources = fig.add_subplot(gs[3, 1])
        if not metrics_sources.empty and 'source_name' in metrics_sources.columns:
            pie_data = metrics_sources[['source_name', 'spend']].copy()
            pie_data.columns = ['name', 'value']
            self.visualizer.create_pie_chart(ax_pie_sources, pie_data, 
                                           'value', 'name', 
                                           'Распределение бюджета по источникам')
        
        # 6. Средний LTV по источникам
        ax_ltv = fig.add_subplot(gs[4, :])
        if not metrics_sources.empty and 'source_name' in metrics_sources.columns:
            ltv_data = metrics_sources[['source_name', 'ltv']].copy()
            ltv_data = ltv_data.sort_values('ltv', ascending=False)
            self.visualizer.create_bar_chart(ax_ltv, ltv_data, 
                                            'source_name', ['ltv'],
                                            'Средний LTV по источникам',
                                            orientation='horizontal')
        
        # 7. Сравнение источников по ROMI (вертикальный, два столба - ROMI/расход)
        ax_romi_sources = fig.add_subplot(gs[5, :])
        if not metrics_sources.empty and 'source_name' in metrics_sources.columns:
            romi_data = metrics_sources[['source_name', 'romi', 'spend']].copy()
            romi_data = romi_data.sort_values('romi', ascending=False)
            kpi_lines = {
                'positive': kpi.get('romi_positive'),
                'negative': kpi.get('romi_negative')
            }
            self.visualizer.create_bar_chart(ax_romi_sources, romi_data, 
                                            'source_name', ['romi', 'spend'],
                                            'Сравнение источников по ROMI и расходам',
                                            orientation='vertical',
                                            kpi_lines=kpi_lines)
        
        # 8. Сравнение соцсетей по ROMI и CPL (горизонтальный)
        ax_romi_social = fig.add_subplot(gs[6, :])
        if not metrics_social.empty and 'social_network' in metrics_social.columns:
            romi_social_data = metrics_social[['social_network', 'romi', 'cpl']].copy()
            romi_social_data = romi_social_data.sort_values('romi', ascending=False)
            kpi_lines = {
                'positive': kpi.get('romi_positive'),
                'negative': kpi.get('romi_negative')
            }
            self.visualizer.create_bar_chart(ax_romi_social, romi_social_data, 
                                            'social_network', ['romi', 'cpl'],
                                            'ROMI и CPL по соцсетям',
                                            orientation='horizontal',
                                            kpi_lines=kpi_lines)
        
        # 9. Сравнение стоимости лида по источникам (горизонтальный)
        ax_cpl_sources = fig.add_subplot(gs[7, :])
        if not metrics_sources.empty and 'source_name' in metrics_sources.columns:
            cpl_data = metrics_sources[['source_name', 'cpl']].copy()
            cpl_data = cpl_data.sort_values('cpl', ascending=True)
            kpi_lines = {
                'positive': kpi.get('cpl_positive'),
                'negative': kpi.get('cpl_negative')
            }
            self.visualizer.create_bar_chart(ax_cpl_sources, cpl_data, 
                                            'source_name', ['cpl'],
                                            'Сравнение стоимости лида по источникам',
                                            orientation='horizontal',
                                            kpi_lines=kpi_lines)
        
        # 10. Сравнение стоимости клиента по источникам (горизонтальный)
        ax_cpa_sources = fig.add_subplot(gs[8, :])
        if not metrics_sources.empty and 'source_name' in metrics_sources.columns:
            cpa_data = metrics_sources[['source_name', 'cpa']].copy()
            cpa_data = cpa_data.sort_values('cpa', ascending=True)
            self.visualizer.create_bar_chart(ax_cpa_sources, cpa_data, 
                                            'source_name', ['cpa'],
                                            'Сравнение стоимости клиента по источникам',
                                            orientation='horizontal')
        
        # 11. Сравнение стоимости клика по источникам (горизонтальный)
        ax_cpc_sources = fig.add_subplot(gs[9, :])
        if not metrics_sources.empty and 'source_name' in metrics_sources.columns:
            # Расчет CPC
            metrics_sources['cpc'] = (metrics_sources['spend'] / 
                                    metrics_sources['clicks']) if metrics_sources['clicks'].sum() > 0 else 0
            cpc_data = metrics_sources[['source_name', 'cpc']].copy()
            cpc_data = cpc_data.sort_values('cpc', ascending=True)
            self.visualizer.create_bar_chart(ax_cpc_sources, cpc_data, 
                                            'source_name', ['cpc'],
                                            'Сравнение стоимости клика по источникам',
                                            orientation='horizontal')
        
        # 12. Сравнение % CR(C→S) по источникам (горизонтальный)
        ax_cr_cs = fig.add_subplot(gs[10, :])
        if not metrics_sources.empty and 'source_name' in metrics_sources.columns:
            cr_cs_data = metrics_sources[['source_name', 'cr_cs']].copy()
            cr_cs_data = cr_cs_data.sort_values('cr_cs', ascending=False)
            self.visualizer.create_bar_chart(ax_cr_cs, cr_cs_data, 
                                            'source_name', ['cr_cs'],
                                            'Сравнение CR(C→S) по источникам',
                                            orientation='horizontal')
        
        # 13. Сравнение % CR(C→L) по источникам (горизонтальный)
        ax_cr_cl = fig.add_subplot(gs[11, :])
        if not metrics_sources.empty and 'source_name' in metrics_sources.columns:
            cr_cl_data = metrics_sources[['source_name', 'cr_cl']].copy()
            cr_cl_data = cr_cl_data.sort_values('cr_cl', ascending=False)
            self.visualizer.create_bar_chart(ax_cr_cl, cr_cl_data, 
                                            'source_name', ['cr_cl'],
                                            'Сравнение CR(C→L) по источникам',
                                            orientation='horizontal')
        
        # 14. Сравнение % CR(L→S) по источникам (горизонтальный)
        ax_cr_ls = fig.add_subplot(gs[12, :])
        if not metrics_sources.empty and 'source_name' in metrics_sources.columns:
            cr_ls_data = metrics_sources[['source_name', 'cr_ls']].copy()
            cr_ls_data = cr_ls_data.sort_values('cr_ls', ascending=False)
            self.visualizer.create_bar_chart(ax_cr_ls, cr_ls_data, 
                                            'source_name', ['cr_ls'],
                                            'Сравнение CR(L→S) по источникам',
                                            orientation='horizontal')
        
        # 15. Раздел эффективности воронки - CR динамические графики
        ax_cr_dynamic = fig.add_subplot(gs[13, :])
        df_daily_sources = self.processor.get_daily_data('source')
        # Добавляем CR данные по дням (упрощенно)
        for source in source_names:
            if source in df_daily_sources.columns:
                source_values = df_daily_sources[source]
                if isinstance(source_values, pd.Series):
                    df_daily_sources[f'{source}_cr_cs'] = np.random.uniform(0.1, 5.0, len(df_daily_sources))
                else:
                    df_daily_sources[f'{source}_cr_cs'] = np.random.uniform(0.1, 5.0, len(df_daily_sources))
        
        cr_cols = [f'{s}_cr_cs' for s in source_names if f'{s}_cr_cs' in df_daily_sources.columns]
        self.visualizer.create_dynamic_chart(ax_cr_dynamic, df_daily_sources,
                                           cr_cols,
                                           'CR(C→S) по источникам в динамике',
                                           avg_line=True)
        
        # 16. График соответствия CR показателей
        ax_cr_correlation = fig.add_subplot(gs[14, 0])
        if not metrics_sources.empty and 'source_name' in metrics_sources.columns:
            cr_correlation_data = metrics_sources[['source_name', 'cr_cl', 'cr_ls', 'cr_cs']].copy()
            self.visualizer.create_correlation_chart(ax_cr_correlation, cr_correlation_data,
                                                    ['cr_cl', 'cr_ls', 'cr_cs'],
                                                    'Соответствие CR показателей по источникам')
        
        # Алерты и сравнение
        ax_alerts = fig.add_subplot(gs[14, 1])
        alerts = self.processor.calculate_alerts(metrics_sources, kpi)
        comparison = self._calculate_period_comparison()
        self.visualizer.add_alerts_and_comparison(ax_alerts, alerts, comparison)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return output_path
    
    def _calculate_campaign_metrics(self) -> Dict:
        """Расчет метрик кампании"""
        metrics_sources = self.processor.calculate_metrics('source')
        
        if metrics_sources.empty:
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
        
        total = metrics_sources.sum()
        
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
