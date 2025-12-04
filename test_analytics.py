#!/usr/bin/env python3
"""
Тестовый скрипт для генерации демонстрационных отчетов
"""

import sys
import os

# Добавить путь к модулю
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analytics_bot.examples.generate_sample_data import create_demo_data
from analytics_bot.main import AnalyticsReportGenerator


def main():
    print("=" * 80)
    print("ДЕМОНСТРАЦИЯ СИСТЕМЫ АНАЛИТИКИ")
    print("=" * 80)
    print("")
    
    # Шаг 1: Генерация демо-данных
    print("ШАГ 1: Генерация демонстрационных данных...")
    print("-" * 80)
    demo_period = create_demo_data()
    print("")
    
    # Шаг 2: Создание генератора отчетов
    print("ШАГ 2: Инициализация генератора отчетов...")
    print("-" * 80)
    generator = AnalyticsReportGenerator(output_dir="./analytics_bot/output")
    print("✓ Генератор инициализирован")
    print(f"✓ Выходная директория: {generator.output_dir}")
    print("")
    
    # Шаг 3: Генерация полного отчета
    print("ШАГ 3: Генерация полного набора отчетов...")
    print("-" * 80)
    result = generator.generate_full_report(demo_period)
    print("")
    
    # Шаг 4: Вывод результатов
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ ГЕНЕРАЦИИ")
    print("=" * 80)
    print("")
    
    print("📊 График 1 (Сквозная аналитика):")
    print(f"   {result['chart1']}")
    print("")
    
    print(f"📈 Графики 2 (По кампаниям): {len(result['chart2'])} файл(ов)")
    for i, path in enumerate(result['chart2'], 1):
        print(f"   {i}. {path}")
    print("")
    
    print("📄 Текстовый отчет:")
    print(f"   {result['text_report']}")
    print("")
    
    print(f"🎯 Карточки кампаний: {len(result['campaign_cards'])} файл(ов)")
    for i, path in enumerate(result['campaign_cards'], 1):
        print(f"   {i}. {path}")
    print("")
    
    print("=" * 80)
    print("✓ ВСЕ ОТЧЕТЫ УСПЕШНО СГЕНЕРИРОВАНЫ!")
    print("=" * 80)
    print("")
    print("Проверьте директорию './analytics_bot/output' для просмотра результатов.")
    print("")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("")
        print("=" * 80)
        print("❌ ОШИБКА ПРИ ГЕНЕРАЦИИ ОТЧЕТОВ")
        print("=" * 80)
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Описание: {str(e)}")
        print("")
        import traceback
        traceback.print_exc()
        sys.exit(1)
