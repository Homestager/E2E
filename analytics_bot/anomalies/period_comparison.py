"""
Модуль сравнения периодов (неделя к неделе, месяц к месяцу)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from ..models.data_models import Campaign, Source, DailyMetrics, AnalyticsPeriod


@dataclass
class PeriodComparison:
    """Результат сравнения периодов"""
    metric_name: str
    current_value: float
    previous_value: float
    change_percent: float
    is_positive: bool  # True если изменение позитивное
    
    @property
    def emoji(self) -> str:
        """Эмодзи для отображения изменения"""
        if abs(self.change_percent) < 5:
            return "➡️"  # Стабильно
        elif self.is_positive:
            return "📈"  # Рост
        else:
            return "📉"  # Падение
    
    @property
    def formatted_change(self) -> str:
        """Форматированное изменение"""
        sign = "+" if self.change_percent > 0 else ""
        return f"{sign}{self.change_percent:.0f}%"


class PeriodComparer:
    """Класс для сравнения периодов"""
    
    def calculate_change_percent(self, current: float, previous: float) -> float:
        """Рассчитать процент изменения"""
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100
    
    def compare_metrics(self, 
                       current_metrics: List[DailyMetrics], 
                       previous_metrics: List[DailyMetrics]) -> Dict[str, PeriodComparison]:
        """Сравнить метрики двух периодов"""
        
        # Суммируем метрики за каждый период
        current_revenue = sum(m.revenue for m in current_metrics)
        previous_revenue = sum(m.revenue for m in previous_metrics)
        
        current_spend = sum(m.spend for m in current_metrics)
        previous_spend = sum(m.spend for m in previous_metrics)
        
        current_leads = sum(m.leads for m in current_metrics)
        previous_leads = sum(m.leads for m in previous_metrics)
        
        current_sales = sum(m.sales for m in current_metrics)
        previous_sales = sum(m.sales for m in previous_metrics)
        
        current_clicks = sum(m.clicks for m in current_metrics)
        previous_clicks = sum(m.clicks for m in previous_metrics)
        
        # Рассчитываем производные метрики
        current_romi = ((current_revenue - current_spend) / current_spend * 100) if current_spend > 0 else 0
        previous_romi = ((previous_revenue - previous_spend) / previous_spend * 100) if previous_spend > 0 else 0
        
        current_cpl = current_spend / current_leads if current_leads > 0 else 0
        previous_cpl = previous_spend / previous_leads if previous_leads > 0 else 0
        
        current_cr_cs = (current_sales / current_clicks * 100) if current_clicks > 0 else 0
        previous_cr_cs = (previous_sales / previous_clicks * 100) if previous_clicks > 0 else 0
        
        # Создаем сравнения
        comparisons = {}
        
        comparisons['romi'] = PeriodComparison(
            metric_name="ROMI",
            current_value=current_romi,
            previous_value=previous_romi,
            change_percent=self.calculate_change_percent(current_romi, previous_romi),
            is_positive=current_romi > previous_romi
        )
        
        comparisons['cpl'] = PeriodComparison(
            metric_name="CPL",
            current_value=current_cpl,
            previous_value=previous_cpl,
            change_percent=self.calculate_change_percent(current_cpl, previous_cpl),
            is_positive=current_cpl < previous_cpl  # Для CPL меньше = лучше
        )
        
        comparisons['cr_cs'] = PeriodComparison(
            metric_name="CR(C→S)",
            current_value=current_cr_cs,
            previous_value=previous_cr_cs,
            change_percent=self.calculate_change_percent(current_cr_cs, previous_cr_cs),
            is_positive=current_cr_cs > previous_cr_cs
        )
        
        comparisons['revenue'] = PeriodComparison(
            metric_name="Выручка",
            current_value=current_revenue,
            previous_value=previous_revenue,
            change_percent=self.calculate_change_percent(current_revenue, previous_revenue),
            is_positive=current_revenue > previous_revenue
        )
        
        comparisons['sales'] = PeriodComparison(
            metric_name="Продаж",
            current_value=current_sales,
            previous_value=previous_sales,
            change_percent=self.calculate_change_percent(current_sales, previous_sales),
            is_positive=current_sales > previous_sales
        )
        
        return comparisons
    
    def get_week_metrics(self, all_metrics: List[DailyMetrics], week_offset: int = 0) -> List[DailyMetrics]:
        """Получить метрики за неделю с учетом смещения (0 = текущая неделя, 1 = прошлая неделя)"""
        if not all_metrics:
            return []
        
        # Сортируем по дате
        sorted_metrics = sorted(all_metrics, key=lambda m: m.date)
        
        # Определяем конец периода (последний день в данных)
        end_date = sorted_metrics[-1].date
        
        # Рассчитываем начало и конец нужной недели
        week_end = end_date - timedelta(days=7 * week_offset)
        week_start = week_end - timedelta(days=7)
        
        return [m for m in sorted_metrics if week_start <= m.date <= week_end]
    
    def get_month_metrics(self, all_metrics: List[DailyMetrics], month_offset: int = 0) -> List[DailyMetrics]:
        """Получить метрики за месяц с учетом смещения (0 = текущий месяц, 1 = прошлый месяц)"""
        if not all_metrics:
            return []
        
        # Сортируем по дате
        sorted_metrics = sorted(all_metrics, key=lambda m: m.date)
        
        # Определяем конец периода
        end_date = sorted_metrics[-1].date
        
        # Рассчитываем начало и конец нужного месяца
        month_end = end_date - timedelta(days=30 * month_offset)
        month_start = month_end - timedelta(days=30)
        
        return [m for m in sorted_metrics if month_start <= m.date <= month_end]
    
    def compare_weeks(self, all_metrics: List[DailyMetrics]) -> Dict[str, PeriodComparison]:
        """Сравнить текущую неделю с прошлой"""
        current_week = self.get_week_metrics(all_metrics, 0)
        previous_week = self.get_week_metrics(all_metrics, 1)
        
        if not current_week or not previous_week:
            return {}
        
        return self.compare_metrics(current_week, previous_week)
    
    def compare_months(self, all_metrics: List[DailyMetrics]) -> Dict[str, PeriodComparison]:
        """Сравнить текущий месяц с прошлым"""
        current_month = self.get_month_metrics(all_metrics, 0)
        previous_month = self.get_month_metrics(all_metrics, 1)
        
        if not current_month or not previous_month:
            return {}
        
        return self.compare_metrics(current_month, previous_month)
    
    def format_comparison_report(self, 
                                week_comparison: Dict[str, PeriodComparison],
                                month_comparison: Dict[str, PeriodComparison]) -> str:
        """Форматировать отчет сравнения периодов"""
        
        lines = []
        lines.append("🔁 Сравнение периодов\n")
        
        if week_comparison:
            lines.append("Эта неделя vs прошлая:")
            for key in ['romi', 'cpl', 'cr_cs', 'revenue']:
                if key in week_comparison:
                    comp = week_comparison[key]
                    warning = " ⚠️" if not comp.is_positive and abs(comp.change_percent) > 10 else ""
                    lines.append(f"  • {comp.metric_name}: {comp.formatted_change}{warning}")
            lines.append("")
        
        if month_comparison:
            lines.append("Этот месяц vs прошлый:")
            for key in ['romi', 'cpl', 'revenue', 'sales']:
                if key in month_comparison:
                    comp = month_comparison[key]
                    warning = " ⚠️" if not comp.is_positive and abs(comp.change_percent) > 10 else ""
                    lines.append(f"  • {comp.metric_name}: {comp.formatted_change}{warning}")
        
        if not week_comparison and not month_comparison:
            lines.append("Недостаточно транзакций для сравнения.")
        
        return "\n".join(lines)
