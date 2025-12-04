"""
Главный модуль для генерации аналитических отчетов
"""

import os
from datetime import datetime
from typing import Optional

from .models.data_models import AnalyticsPeriod, Campaign
from .charts.chart1_generator import Chart1Generator
from .charts.chart2_generator import Chart2Generator
from .anomalies.detector import AnomalyDetector
from .anomalies.period_comparison import PeriodComparer
from .formatters.text_formatter import TextFormatter


class AnalyticsReportGenerator:
    """Генератор аналитических отчетов"""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        self.anomaly_detector = AnomalyDetector()
        self.period_comparer = PeriodComparer()
        
        # Создать директорию для выходных файлов
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_chart1(self, period: AnalyticsPeriod, 
                       output_filename: Optional[str] = None) -> str:
        """
        Сгенерировать ГРАФИК 1 - Сквозная аналитика
        
        Args:
            period: Период аналитики с данными
            output_filename: Имя выходного файла (по умолчанию автогенерация)
        
        Returns:
            Путь к сохраненному файлу
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"chart1_analytics_{timestamp}.png"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        print(f"Генерация ГРАФИК 1 (Сквозная аналитика)...")
        print(f"Период: {period.start_date.date()} — {period.end_date.date()}")
        print(f"Кампаний: {len(period.campaigns)}")
        
        generator = Chart1Generator()
        generator.generate(period, output_path)
        
        print(f"✓ График сохранен: {output_path}")
        
        return output_path
    
    def generate_chart2(self, campaign: Campaign, 
                       output_filename: Optional[str] = None) -> str:
        """
        Сгенерировать ГРАФИК 2 - Аналитика по кампании
        
        Args:
            campaign: Кампания для анализа
            output_filename: Имя выходного файла (по умолчанию автогенерация)
        
        Returns:
            Путь к сохраненному файлу
        """
        if output_filename is None:
            output_filename = f"chart2_campaign_{campaign.campaign_id}.png"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        print(f"Генерация ГРАФИК 2 (Аналитика по кампании)...")
        print(f"Кампания: {campaign.name} (ID: {campaign.campaign_id})")
        print(f"Источников: {len(campaign.sources)}")
        
        generator = Chart2Generator()
        generator.generate(campaign, output_path)
        
        print(f"✓ График сохранен: {output_path}")
        
        return output_path
    
    def generate_text_report(self, period: AnalyticsPeriod, 
                           output_filename: Optional[str] = None) -> str:
        """
        Сгенерировать текстовый отчет с алертами и сравнением периодов
        
        Args:
            period: Период аналитики
            output_filename: Имя выходного файла
        
        Returns:
            Путь к сохраненному файлу
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"text_report_{timestamp}.txt"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        print(f"Генерация текстового отчета...")
        
        lines = []
        lines.append("=" * 80)
        lines.append("АНАЛИТИЧЕСКИЙ ОТЧЕТ")
        lines.append(f"Период: {period.start_date.date()} — {period.end_date.date()}")
        lines.append("=" * 80)
        lines.append("")
        
        # Обнаружить аномалии
        alerts = self.anomaly_detector.analyze_period(period)
        
        lines.append(TextFormatter.format_alerts(alerts))
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
        
        # Сравнение периодов
        for campaign in period.campaigns:
            all_metrics = []
            for source in campaign.sources:
                all_metrics.extend(source.daily_metrics)
            
            if all_metrics:
                week_comparison = self.period_comparer.compare_weeks(all_metrics)
                month_comparison = self.period_comparer.compare_months(all_metrics)
                
                if week_comparison or month_comparison:
                    lines.append(f"Кампания: {campaign.name}")
                    lines.append(self.period_comparer.format_comparison_report(
                        week_comparison, month_comparison))
                    lines.append("")
                    lines.append("-" * 80)
                    lines.append("")
        
        # Список кампаний
        lines.append("СПИСОК КАМПАНИЙ")
        lines.append("=" * 80)
        lines.append("")
        
        for campaign in period.campaigns:
            lines.append(TextFormatter.format_campaign_list_item(campaign))
            lines.append("")
            lines.append("-" * 80)
            lines.append("")
        
        # Сохранить отчет
        report_text = "\n".join(lines)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"✓ Текстовый отчет сохранен: {output_path}")
        
        return output_path
    
    def generate_campaign_card(self, campaign: Campaign, 
                              output_filename: Optional[str] = None) -> str:
        """
        Сгенерировать карточку кампании (текстовый формат для бота)
        
        Args:
            campaign: Кампания
            output_filename: Имя выходного файла
        
        Returns:
            Путь к сохраненному файлу
        """
        if output_filename is None:
            output_filename = f"campaign_card_{campaign.campaign_id}.txt"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        card_text = TextFormatter.format_campaign_card(campaign)
        
        # Добавить алерты для кампании
        alerts = self.anomaly_detector.analyze_campaign(campaign)
        
        if alerts:
            card_text += "\n\n" + "=" * 80 + "\n\n"
            card_text += TextFormatter.format_alerts(alerts)
        
        # Добавить сравнение периодов
        all_metrics = []
        for source in campaign.sources:
            all_metrics.extend(source.daily_metrics)
        
        if all_metrics:
            week_comparison = self.period_comparer.compare_weeks(all_metrics)
            month_comparison = self.period_comparer.compare_months(all_metrics)
            
            if week_comparison or month_comparison:
                card_text += "\n\n" + "=" * 80 + "\n\n"
                card_text += self.period_comparer.format_comparison_report(
                    week_comparison, month_comparison)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(card_text)
        
        print(f"✓ Карточка кампании сохранена: {output_path}")
        
        return output_path
    
    def generate_full_report(self, period: AnalyticsPeriod) -> dict:
        """
        Сгенерировать полный набор отчетов (все графики + текстовые отчеты)
        
        Args:
            period: Период аналитики
        
        Returns:
            Словарь с путями к сгенерированным файлам
        """
        print("=" * 80)
        print("ГЕНЕРАЦИЯ ПОЛНОГО АНАЛИТИЧЕСКОГО ОТЧЕТА")
        print("=" * 80)
        print("")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        result = {
            'chart1': None,
            'chart2': [],
            'text_report': None,
            'campaign_cards': []
        }
        
        # График 1 - Сквозная аналитика
        result['chart1'] = self.generate_chart1(
            period, 
            f"chart1_analytics_{timestamp}.png"
        )
        print("")
        
        # График 2 для каждой кампании
        for campaign in period.campaigns:
            chart2_path = self.generate_chart2(
                campaign, 
                f"chart2_campaign_{campaign.campaign_id}_{timestamp}.png"
            )
            result['chart2'].append(chart2_path)
            print("")
        
        # Текстовый отчет
        result['text_report'] = self.generate_text_report(
            period,
            f"text_report_{timestamp}.txt"
        )
        print("")
        
        # Карточки кампаний
        for campaign in period.campaigns:
            card_path = self.generate_campaign_card(
                campaign,
                f"campaign_card_{campaign.campaign_id}_{timestamp}.txt"
            )
            result['campaign_cards'].append(card_path)
            print("")
        
        print("=" * 80)
        print("✓ ПОЛНЫЙ ОТЧЕТ СГЕНЕРИРОВАН")
        print("=" * 80)
        
        return result


# Пример использования
if __name__ == "__main__":
    from .examples.generate_sample_data import create_demo_data
    
    # Создать демо-данные
    demo_period = create_demo_data()
    print("")
    
    # Создать генератор отчетов
    generator = AnalyticsReportGenerator(output_dir="./analytics_bot/output")
    
    # Сгенерировать полный отчет
    result = generator.generate_full_report(demo_period)
    
    print("\nСгенерированные файлы:")
    print(f"  График 1: {result['chart1']}")
    print(f"  Графики 2: {len(result['chart2'])} файл(ов)")
    for path in result['chart2']:
        print(f"    - {path}")
    print(f"  Текстовый отчет: {result['text_report']}")
    print(f"  Карточки кампаний: {len(result['campaign_cards'])} файл(ов)")
    for path in result['campaign_cards']:
        print(f"    - {path}")
