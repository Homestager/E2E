"""
Модуль для обработки данных аналитики
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class DataProcessor:
    """Класс для обработки данных аналитики"""
    
    def __init__(self, data: Dict):
        """
        Инициализация процессора данных
        
        Args:
            data: Словарь с данными аналитики
        """
        self.data = data
        self.df_campaigns = pd.DataFrame(data.get('campaigns', []))
        self.df_sources = pd.DataFrame(data.get('sources', []))
        self.df_transactions = pd.DataFrame(data.get('transactions', []))
        self.period_start = pd.to_datetime(data.get('period_start'))
        self.period_end = pd.to_datetime(data.get('period_end'))
        
    def calculate_metrics(self, group_by: str = 'campaign') -> pd.DataFrame:
        """
        Расчет метрик по группировке
        
        Args:
            group_by: 'campaign', 'source', 'social_network'
        """
        if group_by == 'campaign':
            df = self.df_campaigns.copy()
        elif group_by == 'source':
            df = self.df_sources.copy()
        else:
            df = self.df_sources.copy()
            df = df.groupby('social_network').agg({
                'revenue': 'sum',
                'spend': 'sum',
                'leads': 'sum',
                'sales': 'sum',
                'clicks': 'sum'
            }).reset_index()
        
        # Расчет метрик
        if df.empty:
            return df
        
        # Заполнение нулями если колонки отсутствуют
        for col in ['revenue', 'spend', 'leads', 'sales', 'clicks']:
            if col not in df.columns:
                df[col] = 0
        
        df['romi'] = df.apply(lambda row: ((row['revenue'] - row['spend']) / row['spend'] * 100) 
                             if row['spend'] > 0 else 0, axis=1)
        df['cpl'] = df.apply(lambda row: (row['spend'] / row['leads']) 
                            if row['leads'] > 0 else 0, axis=1)
        df['cpa'] = df.apply(lambda row: (row['spend'] / row['sales']) 
                            if row['sales'] > 0 else 0, axis=1)
        df['cac'] = df['cpl']  # Упрощение
        df['ltv'] = df.apply(lambda row: (row['revenue'] / row['sales']) 
                           if row['sales'] > 0 else 0, axis=1)
        df['cr_cl'] = df.apply(lambda row: (row['leads'] / row['clicks'] * 100) 
                              if row['clicks'] > 0 else 0, axis=1)
        df['cr_ls'] = df.apply(lambda row: (row['sales'] / row['leads'] * 100) 
                              if row['leads'] > 0 else 0, axis=1)
        df['cr_cs'] = df.apply(lambda row: (row['sales'] / row['clicks'] * 100) 
                              if row['clicks'] > 0 else 0, axis=1)
        
        return df
    
    def get_daily_data(self, group_by: str = 'campaign') -> pd.DataFrame:
        """
        Получение данных по дням
        
        Args:
            group_by: 'campaign', 'source', 'social_network'
        """
        if self.df_transactions.empty:
            # Генерация тестовых данных если нет транзакций
            dates = pd.date_range(self.period_start, self.period_end, freq='D')
            df_daily = pd.DataFrame({'date': dates})
            
            if group_by == 'campaign' and not self.df_campaigns.empty:
                for campaign in self.df_campaigns['campaign_name'].unique():
                    df_daily[campaign] = np.random.randint(0, 100000, len(dates))
            elif group_by == 'source' and not self.df_sources.empty:
                for source in self.df_sources['source_name'].unique():
                    df_daily[source] = np.random.randint(0, 50000, len(dates))
            elif not self.df_sources.empty:
                for sn in self.df_sources['social_network'].unique():
                    df_daily[sn] = np.random.randint(0, 50000, len(dates))
            
            # Добавляем колонку продаж для тепловой карты
            df_daily['sales'] = np.random.randint(0, 50, len(dates))
            
            return df_daily
        
        # Реальная обработка транзакций
        if 'date' not in self.df_transactions.columns:
            self.df_transactions['date'] = pd.to_datetime(self.df_transactions.get('date', 
                                                                                   pd.Timestamp.now()))
        
        if group_by == 'campaign':
            group_col = 'campaign_id'
            # Маппинг ID на имена
            if not self.df_campaigns.empty:
                id_to_name = dict(zip(self.df_campaigns['campaign_id'], 
                                    self.df_campaigns['campaign_name']))
        elif group_by == 'source':
            group_col = 'source_id'
            if not self.df_sources.empty:
                id_to_name = dict(zip(self.df_sources['source_id'], 
                                    self.df_sources['source_name']))
        else:
            group_col = 'social_network'
            id_to_name = {}
        
        if group_col in self.df_transactions.columns:
            df_daily = self.df_transactions.groupby(['date', group_col])['revenue'].sum().reset_index()
            df_daily = df_daily.pivot(index='date', columns=group_col, values='revenue').fillna(0)
            df_daily = df_daily.reset_index()
            
            # Переименование колонок если есть маппинг
            if id_to_name and group_col != 'social_network':
                rename_dict = {k: id_to_name.get(k, k) for k in df_daily.columns if k != 'date'}
                df_daily = df_daily.rename(columns=rename_dict)
        else:
            # Если нет нужной колонки, создаем пустой DataFrame
            dates = pd.date_range(self.period_start, self.period_end, freq='D')
            df_daily = pd.DataFrame({'date': dates})
        
        return df_daily
    
    def calculate_alerts(self, metrics_df: pd.DataFrame, kpi: Optional[Dict] = None) -> List[Dict]:
        """
        Расчет алертов на основе метрик
        
        Args:
            metrics_df: DataFrame с метриками
            kpi: Словарь с KPI значениями
        """
        alerts = []
        
        if kpi is None:
            kpi = {
                'romi_positive': 1200,
                'romi_negative': 700,
                'cpl_positive': None,
                'cpl_negative': None
            }
        
        # Расчет скользящих средних
        if 'date' in metrics_df.columns:
            metrics_df['romi_ma7'] = metrics_df['romi'].rolling(7, min_periods=1).mean()
            metrics_df['cpl_ma7'] = metrics_df['cpl'].rolling(7, min_periods=1).mean()
            metrics_df['revenue_ma7'] = metrics_df['revenue'].rolling(7, min_periods=1).mean()
        
        # Проверка аномалий
        for idx, row in metrics_df.iterrows():
            # ROMI упал ниже KPI
            if kpi.get('romi_negative') and row['romi'] < kpi['romi_negative']:
                alerts.append({
                    'type': 'warning',
                    'icon': '⚠️',
                    'text': f"ROMI упал ниже KPI по {row.get('campaign_name', row.get('source_name', 'источнику'))}"
                })
            
            # CPL вырос
            if 'cpl_ma7' in row and row['cpl'] > row['cpl_ma7'] * 1.4:
                alerts.append({
                    'type': 'warning',
                    'icon': '🔥',
                    'text': f"CPL вырос на {int((row['cpl'] / row['cpl_ma7'] - 1) * 100)}%"
                })
            
            # Источник перестал приносить трафик
            if row.get('leads', 0) == 0 and row.get('clicks', 0) > 0:
                alerts.append({
                    'type': 'error',
                    'icon': '🚫',
                    'text': f"Источник {row.get('source_name', '')} перестал приносить трафик"
                })
        
        return alerts
    
    def compare_periods(self, current_period: pd.DataFrame, 
                       previous_period: pd.DataFrame) -> Dict:
        """
        Сравнение периодов
        
        Args:
            current_period: Данные текущего периода
            previous_period: Данные предыдущего периода
        """
        comparison = {}
        
        current_total = current_period.sum()
        previous_total = previous_period.sum()
        
        if previous_total.get('revenue', 0) > 0:
            comparison['revenue'] = ((current_total['revenue'] - previous_total['revenue']) / 
                                   previous_total['revenue'] * 100)
        
        if previous_total.get('romi', 0) > 0:
            comparison['romi'] = ((current_total['romi'] - previous_total['romi']) / 
                                previous_total['romi'] * 100)
        
        if previous_total.get('cpl', 0) > 0:
            comparison['cpl'] = ((current_total['cpl'] - previous_total['cpl']) / 
                               previous_total['cpl'] * 100)
        
        if previous_total.get('cr_cs', 0) > 0:
            comparison['cr_cs'] = ((current_total['cr_cs'] - previous_total['cr_cs']) / 
                                  previous_total['cr_cs'] * 100)
        
        return comparison
