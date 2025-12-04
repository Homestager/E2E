# Генератор графиков сквозной аналитики

Система для автоматической генерации PNG графиков сквозной аналитики для бота.

## Структура проекта

```
/workspace
├── main.py                    # Основной скрипт для генерации графиков
├── requirements.txt           # Зависимости Python
├── utils/
│   ├── data_processor.py     # Обработка данных и расчет метрик
│   └── visualizer.py         # Визуализация графиков
└── graph_generators/
    ├── graph1_generator.py    # Генератор Графика 1 (сквозная аналитика)
    └── graph2_generator.py    # Генератор Графика 2 (аналитика по кампании)
```

## Установка

```bash
pip install -r requirements.txt
```

## Использование

### Базовое использование

```python
from graph_generators.graph1_generator import Graph1Generator
from graph_generators.graph2_generator import Graph2Generator

# Загрузка данных
data = {
    'period_start': '2025-01-01',
    'period_end': '2025-01-31',
    'campaigns': [...],
    'sources': [...],
    'transactions': [...]
}

# Генерация Графика 1
graph1 = Graph1Generator(data)
graph1.generate('graph1_analytics.png')

# Генерация Графика 2 для конкретной кампании
graph2 = Graph2Generator(data, campaign_id=1)
kpi = {
    'romi_positive': 1200,
    'romi_negative': 700,
    'cpl_positive': None,
    'cpl_negative': None
}
graph2.generate('graph2_campaign_1_analytics.png', kpi)
```

### Запуск с примерными данными

```bash
python3 main.py
```

### Запуск с данными из файла

```bash
python3 main.py data.json
```

## Формат данных

### Структура входных данных (JSON)

```json
{
  "period_start": "2025-01-01",
  "period_end": "2025-01-31",
  "campaign_name": "ОБЩАЯ",
  "campaigns": [
    {
      "campaign_id": 1,
      "campaign_name": "BLACKFRIDAY_2025",
      "revenue": 1230000,
      "spend": 240000,
      "leads": 1304,
      "sales": 225,
      "clicks": 10500
    }
  ],
  "sources": [
    {
      "source_id": 1,
      "source_name": "Instagram_source_1",
      "campaign_id": 1,
      "social_network": "Instagram",
      "revenue": 246000,
      "spend": 48000,
      "leads": 261,
      "sales": 45,
      "clicks": 2100
    }
  ],
  "transactions": [
    {
      "date": "2025-01-01",
      "campaign_id": 1,
      "source_id": 1,
      "revenue": 5000,
      "social_network": "Instagram"
    }
  ]
}
```

## График 1: Сквозная аналитика

Включает:
- Шапка с итогами по всем кампаниям
- Тепловая карта продаж по дням недели
- Пироги распределения бюджета и прибыли
- Динамика выручки по кампаниям и соцсетям
- Сравнение ROMI, CPL, LTV
- Графики соответствия CAC/CPL/CPA
- Алерты и сравнение периодов

## График 2: Аналитика по кампании

Включает:
- Шапка с итогами кампании
- Динамика выручки по источникам и соцсетям
- Распределение бюджета
- Сравнение источников по ROMI, CPL, CPA, CPC
- Сравнение CR показателей
- Графики эффективности воронки
- Алерты с учетом KPI кампании

## Особенности

- Автоматическое обнаружение аномалий
- Сравнение периодов (неделя к неделе, месяц к месяцу)
- Поддержка KPI для кампаний
- Обработка пустых данных
- Гибкая настройка визуализаций

## Зависимости

- matplotlib >= 3.8.2
- seaborn >= 0.13.0
- pandas >= 2.1.4
- numpy >= 1.26.2
- Pillow >= 10.1.0
