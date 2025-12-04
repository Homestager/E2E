"""
Базовый класс для генерации графиков
"""

import matplotlib
matplotlib.use('Agg')  # Для работы без дисплея
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import numpy as np

# Установка стиля и шрифтов для русского языка
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = False

# Цветовая палитра
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'warning': '#F77F00',
    'danger': '#D62828',
    'info': '#4895EF',
    'purple': '#7209B7',
    'pink': '#F72585',
    'teal': '#06FFF0',
    'orange': '#FF9E00',
    'green': '#52B788',
    'blue': '#0077B6',
    'red': '#DC2F02',
    'gray': '#6C757D',
}

PALETTE = [
    '#2E86AB', '#A23B72', '#06A77D', '#F77F00', '#7209B7',
    '#4895EF', '#F72585', '#06FFF0', '#FF9E00', '#52B788',
    '#0077B6', '#DC2F02', '#6C757D', '#D62828', '#F8961E'
]


class BaseChart:
    """Базовый класс для всех графиков"""
    
    def __init__(self, figsize: Tuple[int, int] = (16, 10), dpi: int = 100):
        self.figsize = figsize
        self.dpi = dpi
        self.fig = None
        self.ax = None
    
    def create_figure(self, nrows: int = 1, ncols: int = 1) -> Tuple:
        """Создать фигуру"""
        self.fig, axes = plt.subplots(nrows, ncols, figsize=self.figsize, dpi=self.dpi)
        if nrows == 1 and ncols == 1:
            self.ax = axes
        return self.fig, axes
    
    def set_title(self, title: str, ax=None):
        """Установить заголовок"""
        if ax is None:
            ax = self.ax
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    def set_labels(self, xlabel: str = None, ylabel: str = None, ax=None):
        """Установить подписи осей"""
        if ax is None:
            ax = self.ax
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=11)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=11)
    
    def add_grid(self, ax=None, alpha: float = 0.3):
        """Добавить сетку"""
        if ax is None:
            ax = self.ax
        ax.grid(True, alpha=alpha, linestyle='--', linewidth=0.5)
    
    def format_money_axis(self, ax=None):
        """Форматировать ось с деньгами"""
        if ax is None:
            ax = self.ax
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
    
    def add_kpi_lines(self, positive_kpi: float, negative_kpi: float, ax=None):
        """Добавить линии KPI"""
        if ax is None:
            ax = self.ax
        
        if positive_kpi is not None:
            ax.axhline(y=positive_kpi, color=COLORS['success'], linestyle='--', 
                      linewidth=2, alpha=0.7, label=f'KPI Positive: {positive_kpi:.0f}%')
        
        if negative_kpi is not None:
            ax.axhline(y=negative_kpi, color=COLORS['danger'], linestyle='--', 
                      linewidth=2, alpha=0.7, label=f'KPI Negative: {negative_kpi:.0f}%')
    
    def save(self, filepath: str):
        """Сохранить график"""
        if self.fig:
            self.fig.tight_layout()
            self.fig.savefig(filepath, dpi=self.dpi, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
            plt.close(self.fig)
    
    def close(self):
        """Закрыть фигуру"""
        if self.fig:
            plt.close(self.fig)


class PieChart(BaseChart):
    """График-пирог"""
    
    def plot(self, data: Dict[str, float], title: str, ax=None) -> None:
        """Построить круговую диаграмму"""
        if ax is None:
            if self.fig is None:
                self.create_figure()
            ax = self.ax
        
        labels = list(data.keys())
        values = list(data.values())
        
        # Удалить нулевые значения
        filtered = [(l, v) for l, v in zip(labels, values) if v > 0]
        if not filtered:
            return
        
        labels, values = zip(*filtered)
        
        # Создать пирог
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=PALETTE[:len(values)],
            textprops={'fontsize': 10}
        )
        
        # Улучшить читаемость процентов
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
        ax.axis('equal')


class BarChart(BaseChart):
    """Столбчатая диаграмма"""
    
    def plot_horizontal(self, data: Dict[str, float], title: str, 
                       xlabel: str = '', color: str = None, ax=None) -> None:
        """Горизонтальная столбчатая диаграмма"""
        if ax is None:
            if self.fig is None:
                self.create_figure()
            ax = self.ax
        
        labels = list(data.keys())
        values = list(data.values())
        
        # Сортировка по значениям
        sorted_data = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
        labels, values = zip(*sorted_data) if sorted_data else ([], [])
        
        y_pos = np.arange(len(labels))
        
        colors_list = [PALETTE[i % len(PALETTE)] for i in range(len(labels))] if not color else [color] * len(labels)
        
        bars = ax.barh(y_pos, values, color=colors_list, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
        
        # Добавить значения на столбцы
        for i, (bar, value) in enumerate(zip(bars, values)):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'{value:.0f}', 
                   ha='left', va='center', fontsize=9, fontweight='bold')
        
        self.add_grid(ax)
    
    def plot_vertical(self, data: Dict[str, float], title: str, 
                     ylabel: str = '', color: str = None, ax=None) -> None:
        """Вертикальная столбчатая диаграмма"""
        if ax is None:
            if self.fig is None:
                self.create_figure()
            ax = self.ax
        
        labels = list(data.keys())
        values = list(data.values())
        
        x_pos = np.arange(len(labels))
        
        colors_list = [PALETTE[i % len(PALETTE)] for i in range(len(labels))] if not color else [color] * len(labels)
        
        bars = ax.bar(x_pos, values, color=colors_list, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
        
        # Добавить значения на столбцы
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{value:.0f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        self.add_grid(ax)


class HeatmapChart(BaseChart):
    """Тепловая карта"""
    
    def plot(self, data: np.ndarray, xlabels: List[str], ylabels: List[str], 
            title: str, cmap: str = 'YlOrRd', ax=None) -> None:
        """Построить тепловую карту"""
        if ax is None:
            if self.fig is None:
                self.create_figure()
            ax = self.ax
        
        im = ax.imshow(data, cmap=cmap, aspect='auto')
        
        # Установить метки
        ax.set_xticks(np.arange(len(xlabels)))
        ax.set_yticks(np.arange(len(ylabels)))
        ax.set_xticklabels(xlabels)
        ax.set_yticklabels(ylabels)
        
        # Повернуть метки
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Добавить значения в ячейки
        for i in range(len(ylabels)):
            for j in range(len(xlabels)):
                text = ax.text(j, i, f'{data[i, j]:.0f}',
                             ha="center", va="center", color="black" if data[i, j] < data.max()/2 else "white",
                             fontsize=9, fontweight='bold')
        
        ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
        
        # Добавить colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Продажи', rotation=270, labelpad=20)
