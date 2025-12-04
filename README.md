# Marketing Analytics Report Generator

Система генерации PNG-отчетов для Telegram-бота сквозной маркетинговой аналитики.

## Возможности

### График 1 - Сквозная аналитика (все кампании)

- **Шапка с итогами**: Выручка, расходы, ROMI, CPL, LTV, конверсии
- **Тепловая карта**: Продажи по дням недели
- **Распределение бюджета**: Пироговые диаграммы по кампаниям и соцсетям
- **Выручка в динамике**: Таймлайн с полупрозрачными кривыми по кампаниям
- **Выручка по соцсетям**: Аналогичный таймлайн с разбивкой по соцсетям
- **Сравнение ROMI**: Вертикальные столбики с расходами по кампаниям
- **Анализ CPL**: Динамические графики по источникам
- **Анализ воронки**: CPC → CPL → CAC, CR анализ
- **Алерты и сравнение периодов**: Автоматические сигналы и сравнение неделя/месяц

### График 2 - Аналитика кампании (детально)

- **Шапка кампании**: Все метрики по конкретной кампании
- **Выручка по источникам (RID)**: Таймлайн с разбивкой по источникам
- **Выручка по соцсетям**: Внутри одной кампании
- **Распределение бюджета**: По источникам и соцсетям
- **LTV по источникам**: Средний LTV для каждого RID
- **ROMI сравнение**: С линиями KPI (зелёная/красная)
- **CPL/CAC/CPC анализ**: По каждому источнику
- **CR анализ**: CR(C→L), CR(L→S), CR(C→S) по источникам
- **Анализ воронки**: Диагностика просадок в конверсии

### Система алертов

Автоматическое обнаружение аномалий:

- 🔥 CPL вырос на X% за неделю
- ⚠️ ROMI упал ниже KPI
- 💤 Бюджет не обновлялся N дней
- 🚫 Источник перестал приносить трафик
- 🎯 Не заданы KPI для кампаний
- 🚀 Резкий пик продаж связан со стартом рекламы
- ⚠️ Источник стартовал, но продаж нет

### Сравнение периодов

- Неделя к неделе
- Месяц к месяцу
- Автоматические выводы с предупреждениями

## Установка

```bash
pip install -r requirements.txt
```

## Использование

### Командная строка

```bash
# Сгенерировать все отчеты с демо-данными
python main.py --all --demo

# Только График 1
python main.py --graph1

# График 2 для конкретной кампании
python main.py --graph2 1234

# Свои параметры данных
python main.py --all --days 60 --campaigns 5 --sources 8

# Показать список кампаний
python main.py --list-campaigns

# Показать алерты
python main.py --alerts
```

### Интеграция с Telegram-ботом

```python
from analytics import AnalyticsPeriod
from analytics.bot_integration import MarketingAnalyticsBot

# Загрузить данные (из вашей БД)
period = AnalyticsPeriod(
    start_date=start,
    end_date=end,
    campaigns=campaigns_from_db
)

# Инициализировать бота
bot = MarketingAnalyticsBot(period)

# Получить PNG для Graph 1
png_bytes = bot.generate_graph1()

# Получить PNG для Graph 2
png_bytes = bot.generate_graph2(campaign_id)

# Получить текстовую карточку кампании
card = bot.get_campaign_card(campaign_id)

# Получить алерты
alerts_text = bot.get_alerts_text()

# Получить сравнение периодов
comparison = bot.get_comparison_text("week")

# Установить KPI
bot.set_campaign_kpi(campaign_id, romi_positive=1500, romi_negative=800)
```

## Структура проекта

```
├── analytics/
│   ├── __init__.py           # Экспорты модуля
│   ├── models.py             # Модели данных (Campaign, Source, etc.)
│   ├── alerts.py             # Система алертов и детекция аномалий
│   ├── chart_utils.py        # Утилиты для графиков
│   ├── graph1_cross_analytics.py    # Генератор Graph 1
│   ├── graph2_campaign_analytics.py # Генератор Graph 2
│   ├── data_generator.py     # Генератор тестовых данных
│   └── bot_integration.py    # Интеграция с Telegram-ботом
├── main.py                   # Точка входа CLI
├── example_bot_usage.py      # Пример интеграции с ботом
├── requirements.txt          # Зависимости
└── README.md                 # Документация
```

## Модели данных

### Campaign
```python
Campaign(
    id="1234",
    name="BLACKFRIDAY_2025",
    created_at=date(2025, 11, 1),
    sources=[...],
    kpi=KPISettings(romi_positive=1200, romi_negative=700)
)
```

### Source (RID)
```python
Source(
    rid="746233",
    name="petrova",
    campaign_id="1234",
    social_network=SocialNetwork.INSTAGRAM,
    created_at=date(2025, 11, 1),
    ad_start_date=date(2025, 11, 5),
    daily_metrics=[...],
    kpi=KPISettings()
)
```

### DailyMetrics
```python
DailyMetrics(
    date=date(2025, 11, 15),
    clicks=150,
    leads=18,
    sales=5,
    revenue=240000,
    spend=45000,
    refunds=0,
    refund_amount=0
)
```

## Правила аномалий

### ROMI
- Падение >30% от 7-дневной средней → Alert
- Рост >50% → Info
- Ниже KPI negative → Critical
- Выше KPI positive → Success

### CPL
- Рост >40% от средней → Warning
- Превышает KPI negative → Warning

### Источники
- 0 лидов за 3 дня → No Traffic
- Много кликов, 0 продаж → Funnel Issue
- Старт рекламы без продаж → Launch Issue

### Воронка
- Высокий CR(C→L), низкий CR(C→S) → Проблема на этапе продаж
- Много кликов, мало лидов → Проблема посадочной

## Форматы карточек

### Карточка кампании (для списка)
```
🎯 BLACKFRIDAY_2025
ID: 1932
Создана: 2025-11-01
Lead: 18 | Sale: 5 | Revenue: 2.4M ₽
ROMI: 450% | CPL: 240 руб | CR C→S: 1.25%
```

### Детальная карточка кампании
```
📊 Кампания: BLACKFRIDAY_2025
ID: 1932
Создана: 2025-11-01

💰 Итоги:
Выручка: 1 230 000 ₽
Расходы: 240 000 ₽
ROMI: 412%
CPL: 184 ₽

🔥 Топ источник:
INSTAGRAM_petrova — ROMI 244%

⚠️ Хуже всех:
TG_ads — ROMI -80%

📈 Конверсии:
CR(C→L): 12.4%
CR(L→S): 3.1%
CR(C→S): 0.36%

📂 Соцсети:
Instagram — ROMI 210% | CPL 170 ₽
Telegram — ROMI 60% | CPL 330 ₽

💸 Распределение бюджета:
Instagram — 44%
Telegram — 31%

📁 Графики:
1. Сквозная по кампании: /analytics_source_1932
2. CSV кампании: /analytics_file_1932

🎯 KPI:
ROMI positive: 1200%
ROMI negative: 700%

💡 Задать KPI:
/kpi_positive_1932 число
/kpi_negative_1932 число
```

## Команды бота

- `/analytics_graph1` - Сквозная аналитика (PNG)
- `/analytics_source_{campaign_id}` - Аналитика кампании (PNG)
- `/campaign_{id}` - Карточка кампании
- `/rid_{rid_id}` - Карточка источника
- `/kpi_positive_{id} число` - Установить положительный KPI
- `/kpi_negative_{id} число` - Установить отрицательный KPI
- `/alerts` - Показать алерты
- `/analytics_file_{id}` - CSV отчет

## Лицензия

MIT
