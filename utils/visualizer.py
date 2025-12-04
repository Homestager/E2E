"""
Модуль для визуализации графиков аналитики
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Настройка стиля
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('dark_background')
sns.set_palette("husl")

class AnalyticsVisualizer:
    """Класс для создания визуализаций аналитики"""
    
    def __init__(self, figsize: Tuple[int, int] = (20, 24)):
        """
        Инициализация визуализатора
        
        Args:
            figsize: Размер фигуры (ширина, высота)
        """
        self.figsize = figsize
        self.colors = sns.color_palette("husl", 20)
        
    def create_header(self, ax, title: str, metrics: Dict):
        """
        Создание шапки с итогами
        
        Args:
            ax: Ось matplotlib
            title: Заголовок
            metrics: Словарь с метриками
        """
        ax.axis('off')
        
        # Рамка
        rect = Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                        fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        
        # Заголовок
        ax.text(0.5, 0.95, title, ha='center', va='top', 
               fontsize=16, fontweight='bold', transform=ax.transAxes)
        
        # Метрики
        y_pos = 0.8
        metrics_text = [
            f"Выручка: {metrics.get('revenue', 0):,.0f} ₽",
            f"ROMI: {metrics.get('romi', 0):.1f}%",
            f"Расходы: {metrics.get('spend', 0):,.0f} ₽",
            f"CPL: {metrics.get('cpl', 0):.0f} RUB",
            f"Лиды: {metrics.get('leads', 0):,}",
            f"LTV: {metrics.get('ltv', 0):.0f} RUB",
            f"Продажи: {metrics.get('sales', 0):,}",
            f"Клики: {metrics.get('clicks', 0):,}",
        ]
        
        for i, text in enumerate(metrics_text):
            x_pos = 0.1 + (i % 2) * 0.4
            if i >= 4:
                y_pos = 0.6
            ax.text(x_pos, y_pos - (i // 2) * 0.1, text, 
                   fontsize=10, transform=ax.transAxes)
        
        # CR метрики
        cr_text = (
            f"CR(C->L): {metrics.get('cr_cl', 0):.2f}% | "
            f"CR(L->S): {metrics.get('cr_ls', 0):.2f}% | "
            f"CR(C->S): {metrics.get('cr_cs', 0):.2f}%"
        )
        ax.text(0.5, 0.3, cr_text, ha='center', fontsize=10, 
               transform=ax.transAxes, 
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    def create_heatmap_weekdays(self, ax, df_daily: pd.DataFrame):
        """
        Тепловая карта по дням недели
        
        Args:
            ax: Ось matplotlib
            df_daily: DataFrame с данными по дням
        """
        if df_daily.empty or 'date' not in df_daily.columns:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', 
                   transform=ax.transAxes)
            ax.axis('off')
            return
        
        df_daily['date'] = pd.to_datetime(df_daily['date'])
        df_daily['weekday'] = df_daily['date'].dt.day_name()
        df_daily['week'] = df_daily['date'].dt.isocalendar().week
        
        # Группировка по дням недели
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                        'Friday', 'Saturday', 'Sunday']
        weekday_ru = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        
        heatmap_data = df_daily.groupby('weekday')['sales'].sum().reindex(weekday_order)
        heatmap_data.index = weekday_ru
        
        # Создание матрицы для тепловой карты
        weeks = df_daily['week'].unique()
        matrix = []
        for day in weekday_order:
            row = []
            for week in sorted(weeks):
                value = df_daily[(df_daily['weekday'] == day) & 
                               (df_daily['week'] == week)]['sales'].sum()
                row.append(value)
            matrix.append(row)
        
        sns.heatmap(matrix, ax=ax, cmap='YlOrRd', annot=True, fmt='.0f',
                   xticklabels=[f'Неделя {w}' for w in sorted(weeks)],
                   yticklabels=weekday_ru, cbar_kws={'label': 'Продажи'})
        ax.set_title('Тепловая карта продаж по дням недели', fontsize=12, fontweight='bold')
        ax.set_xlabel('Недели')
        ax.set_ylabel('Дни недели')
    
    def create_pie_chart(self, ax, data: pd.DataFrame, value_col: str, 
                        label_col: str, title: str):
        """
        Создание круговой диаграммы
        
        Args:
            ax: Ось matplotlib
            data: DataFrame с данными
            value_col: Колонка со значениями
            label_col: Колонка с метками
            title: Заголовок
        """
        if data.empty:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', 
                   transform=ax.transAxes)
            ax.axis('off')
            return
        
        # Сортировка по убыванию
        data_sorted = data.sort_values(value_col, ascending=False)
        
        # Ограничение до топ-10 для читаемости
        if len(data_sorted) > 10:
            other_sum = data_sorted.iloc[10:][value_col].sum()
            data_sorted = data_sorted.iloc[:10]
            if other_sum > 0:
                new_row = pd.DataFrame({label_col: ['Другие'], value_col: [other_sum]})
                data_sorted = pd.concat([data_sorted, new_row], ignore_index=True)
        
        colors = self.colors[:len(data_sorted)]
        wedges, texts, autotexts = ax.pie(data_sorted[value_col], 
                                         labels=data_sorted[label_col],
                                         autopct='%1.1f%%',
                                         colors=colors,
                                         startangle=90)
        
        # Улучшение читаемости
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)
        
        ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
        
        # Легенда с деталями
        legend_labels = [f"{row[label_col]}: {row[value_col]:,.0f} ₽" 
                        for _, row in data_sorted.iterrows()]
        ax.legend(wedges, legend_labels, loc="center left", 
                bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
    
    def create_timeline_chart(self, ax, df_daily: pd.DataFrame, 
                             group_cols: List[str], title: str,
                             show_bars: bool = True, show_pie: bool = True):
        """
        Создание графика временной линии с наложением кривых
        
        Args:
            ax: Ось matplotlib
            df_daily: DataFrame с данными по дням
            group_cols: Список колонок для группировки (кампании/источники)
            title: Заголовок
            show_bars: Показывать столбики продаж на фоне
            show_pie: Показывать пирог выручки
        """
        if df_daily.empty or 'date' not in df_daily.columns:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', 
                   transform=ax.transAxes)
            ax.axis('off')
            return
        
        df_daily['date'] = pd.to_datetime(df_daily['date'])
        
        # Столбики продаж на фоне
        if show_bars and 'sales' in df_daily.columns:
            ax2 = ax.twinx()
            ax2.bar(df_daily['date'], df_daily['sales'], 
                   alpha=0.3, color='gray', label='Продажи')
            ax2.set_ylabel('Количество продаж', fontsize=9)
            ax2.tick_params(axis='y', labelsize=8)
        
        # Кривые по группам
        for i, col in enumerate(group_cols):
            if col in df_daily.columns:
                ax.plot(df_daily['date'], df_daily[col], 
                       alpha=0.6, linewidth=2, label=col,
                       color=self.colors[i % len(self.colors)])
        
        ax.set_xlabel('Дата', fontsize=10)
        ax.set_ylabel('Выручка, ₽', fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        
        # Пирог выручки (в отдельной области или под графиком)
        if show_pie:
            # Вычисление общей выручки по группам
            pie_data = {}
            for col in group_cols:
                if col in df_daily.columns:
                    pie_data[col] = df_daily[col].sum()
            
            if pie_data:
                # Создание мини-пирога в углу
                from matplotlib.patches import Circle
                pie_ax = ax.inset_axes([0.02, 0.7, 0.25, 0.25])
                pie_df = pd.DataFrame(list(pie_data.items()), 
                                     columns=['name', 'value'])
                self.create_pie_chart(pie_ax, pie_df, 'value', 'name', 
                                     'Распределение выручки')
    
    def create_bar_chart(self, ax, data: pd.DataFrame, x_col: str, 
                        y_cols: List[str], title: str, orientation: str = 'vertical',
                        kpi_lines: Optional[Dict] = None):
        """
        Создание столбчатой диаграммы
        
        Args:
            ax: Ось matplotlib
            data: DataFrame с данными
            x_col: Колонка для оси X
            y_cols: Список колонок для оси Y
            title: Заголовок
            orientation: 'vertical' или 'horizontal'
            kpi_lines: Словарь с KPI линиями {'positive': value, 'negative': value}
        """
        if data.empty:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', 
                   transform=ax.transAxes)
            ax.axis('off')
            return
        
        # Сортировка данных
        data_sorted = data.sort_values(y_cols[0], ascending=(orientation == 'vertical'))
        
        x = np.arange(len(data_sorted))
        width = 0.35
        
        if orientation == 'vertical':
            for i, y_col in enumerate(y_cols):
                offset = (i - len(y_cols)/2 + 0.5) * width
                ax.bar(x + offset, data_sorted[y_col], width, 
                      label=y_col, color=self.colors[i])
            
            ax.set_xticks(x)
            ax.set_xticklabels(data_sorted[x_col], rotation=45, ha='right', fontsize=8)
            ax.set_ylabel(y_cols[0], fontsize=10)
            
            # KPI линии
            if kpi_lines:
                if 'positive' in kpi_lines and kpi_lines['positive'] is not None:
                    ax.axhline(y=kpi_lines['positive'], color='green', 
                             linestyle='--', linewidth=2, label='KPI+', alpha=0.7)
                if 'negative' in kpi_lines and kpi_lines['negative'] is not None:
                    ax.axhline(y=kpi_lines['negative'], color='red', 
                             linestyle='--', linewidth=2, label='KPI-', alpha=0.7)
        else:
            for i, y_col in enumerate(y_cols):
                offset = (i - len(y_cols)/2 + 0.5) * width
                ax.barh(x + offset, data_sorted[y_col], width, 
                       label=y_col, color=self.colors[i])
            
            ax.set_yticks(x)
            ax.set_yticklabels(data_sorted[x_col], fontsize=8)
            ax.set_xlabel(y_cols[0], fontsize=10)
            
            # KPI линии
            if kpi_lines:
                if 'positive' in kpi_lines and kpi_lines['positive'] is not None:
                    ax.axvline(x=kpi_lines['positive'], color='green', 
                             linestyle='--', linewidth=2, label='KPI+', alpha=0.7)
                if 'negative' in kpi_lines and kpi_lines['negative'] is not None:
                    ax.axvline(x=kpi_lines['negative'], color='red', 
                             linestyle='--', linewidth=2, label='KPI-', alpha=0.7)
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, axis='y' if orientation == 'vertical' else 'x')
    
    def create_dynamic_chart(self, ax, df_daily: pd.DataFrame, 
                           value_cols: List[str], title: str,
                           avg_line: bool = True):
        """
        Создание динамического графика с наложением показателей
        
        Args:
            ax: Ось matplotlib
            df_daily: DataFrame с данными по дням
            value_cols: Список колонок для отображения
            title: Заголовок
            avg_line: Показывать среднюю линию на фоне
        """
        if df_daily.empty or 'date' not in df_daily.columns:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', 
                   transform=ax.transAxes)
            ax.axis('off')
            return
        
        df_daily['date'] = pd.to_datetime(df_daily['date'])
        
        # Средняя линия
        if avg_line:
            for col in value_cols:
                if col in df_daily.columns:
                    avg_value = df_daily[col].mean()
                    ax.axhline(y=avg_value, color='gray', linestyle='--', 
                             alpha=0.5, linewidth=1, label=f'Среднее {col}')
        
        # Кривые по источникам/кампаниям
        for i, col in enumerate(value_cols):
            if col in df_daily.columns:
                ax.plot(df_daily['date'], df_daily[col], 
                       alpha=0.6, linewidth=2, label=col,
                       color=self.colors[i % len(self.colors)])
        
        ax.set_xlabel('Дата', fontsize=10)
        ax.set_ylabel('Значение', fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend(loc='best', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
    
    def create_correlation_chart(self, ax, data: pd.DataFrame, 
                                metrics: List[str], title: str):
        """
        Создание графика соответствия метрик (CAC/CPL/CPA или CR)
        
        Args:
            ax: Ось matplotlib
            data: DataFrame с данными
            metrics: Список метрик для сравнения
            title: Заголовок
        """
        if data.empty:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', 
                   transform=ax.transAxes)
            ax.axis('off')
            return
        
        x = np.arange(len(data))
        width = 0.25
        
        for i, metric in enumerate(metrics):
            if metric in data.columns:
                offset = (i - len(metrics)/2 + 0.5) * width
                ax.bar(x + offset, data[metric], width, 
                      label=metric, color=self.colors[i])
        
        ax.set_xticks(x)
        if 'source_name' in data.columns:
            ax.set_xticklabels(data['source_name'], rotation=45, ha='right', fontsize=8)
        elif 'campaign_name' in data.columns:
            ax.set_xticklabels(data['campaign_name'], rotation=45, ha='right', fontsize=8)
        
        ax.set_ylabel('Значение', fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, axis='y')
    
    def add_alerts_and_comparison(self, ax, alerts: List[Dict], 
                                 comparison: Optional[Dict] = None):
        """
        Добавление алертов и сравнения периодов под графиком
        
        Args:
            ax: Ось matplotlib
            alerts: Список алертов
            comparison: Словарь со сравнением периодов
        """
        ax.axis('off')
        
        y_pos = 0.95
        
        # Алерты
        if alerts:
            ax.text(0.05, y_pos, '⚠️ Алерты (автоматические сигналы)', 
                   fontsize=11, fontweight='bold', transform=ax.transAxes)
            y_pos -= 0.08
            
            for alert in alerts[:5]:  # Ограничение до 5 алертов
                text = f"{alert.get('icon', '•')} {alert.get('text', '')}"
                ax.text(0.1, y_pos, text, fontsize=9, 
                       transform=ax.transAxes,
                       color='red' if alert.get('type') == 'error' else 'orange')
                y_pos -= 0.06
        else:
            ax.text(0.05, y_pos, '🧠 Всё стабильно. Аномалий не обнаружено.', 
                   fontsize=10, transform=ax.transAxes, color='green')
            y_pos -= 0.08
        
        y_pos -= 0.05
        
        # Сравнение периодов
        if comparison:
            ax.text(0.05, y_pos, '🔁 Сравнение периодов', 
                   fontsize=11, fontweight='bold', transform=ax.transAxes)
            y_pos -= 0.08
            
            if 'week' in comparison:
                ax.text(0.1, y_pos, 'Эта неделя vs прошлая:', 
                       fontsize=9, fontweight='bold', transform=ax.transAxes)
                y_pos -= 0.06
                for key, value in comparison['week'].items():
                    sign = '+' if value >= 0 else ''
                    color = 'red' if abs(value) > 20 else 'black'
                    ax.text(0.15, y_pos, 
                           f"• {key.upper()}: {sign}{value:.1f}%", 
                           fontsize=9, transform=ax.transAxes, color=color)
                    y_pos -= 0.05
            
            if 'month' in comparison:
                y_pos -= 0.02
                ax.text(0.1, y_pos, 'Этот месяц vs прошлый:', 
                       fontsize=9, fontweight='bold', transform=ax.transAxes)
                y_pos -= 0.06
                for key, value in comparison['month'].items():
                    sign = '+' if value >= 0 else ''
                    color = 'red' if abs(value) > 20 else 'black'
                    ax.text(0.15, y_pos, 
                           f"• {key.upper()}: {sign}{value:.1f}%", 
                           fontsize=9, transform=ax.transAxes, color=color)
                    y_pos -= 0.05
        else:
            ax.text(0.05, y_pos, 'Недостаточно транзакций для сравнения.', 
                   fontsize=9, transform=ax.transAxes, style='italic')
