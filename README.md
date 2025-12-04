# Система Аналитики для Телеграм-Бота

Комплексная система генерации аналитических отчетов в виде PNG-графиков и текстовых карточек для телеграм-бота сквозной аналитики.

## 📋 Содержание

- [Возможности](#возможности)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Структура проекта](#структура-проекта)
- [График 1 - Сквозная аналитика](#график-1---сквозная-аналитика)
- [График 2 - Аналитика по кампании](#график-2---аналитика-по-кампании)
- [Система обнаружения аномалий](#система-обнаружения-аномалий)
- [Сравнение периодов](#сравнение-периодов)
- [Использование в коде](#использование-в-коде)
- [Примеры](#примеры)

---

## 🎯 Возможности

### График 1 - Сквозная аналитика по всем кампаниям

- **Шапка с основными метриками** (выручка, расходы, ROMI, CPL, LTV, конверсии)
- **Тепловая карта продаж** по дням недели
- **Динамика выручки** по кампаниям с полупрозрачными кривыми
- **Динамика выручки** по соцсетям
- **Пироги распределения**:
  - Выручка по кампаниям
  - Выручка по соцсетям
  - Бюджет по кампаниям
  - Бюджет по соцсетям
- **Средний LTV** по кампаниям (горизонтальный график)
- **Сравнение ROMI** по кампаниям с расходами (вертикальные столбики)
- **ROMI и CPL** по соцсетям (горизонтальный)
- **Стоимость лида (CPL)** по кампаниям
- **Конверсия C→S** по кампаниям

### График 2 - Детальная аналитика по кампании

- **Шапка с метриками кампании**
- **Динамика выручки** по источникам (RID) с наложением кривых
- **Динамика выручки** по соцсетям внутри кампании
- **Пироги распределения**:
  - Выручка по источникам
  - Выручка по соцсетям
  - Бюджет по источникам
  - Бюджет по соцсетям
- **Средний LTV** по источникам
- **Сравнение ROMI** по источникам с линиями KPI
- **Сравнение ROMI** по соцсетям с линиями KPI
- **Анализ стоимости**:
  - CPL (Cost Per Lead) по источникам с KPI
  - CAC (Customer Acquisition Cost) по источникам
  - CPA (Cost Per Action / Click) по источникам
- **Анализ воронки**: сравнение CPA → CPL → CAC для выявления просадок
- **Конверсии по источникам**:
  - CR(C→S) - клики в продажи
  - CR(C→L) - клики в лиды
  - CR(L→S) - лиды в продажи

### Система обнаружения аномалий

Автоматическое обнаружение проблем:

- 🔥 Резкое падение ROMI (>30% от скользящей средней)
- 🚀 Резкий рост ROMI (>50%)
- 🚫 Источник перестал приносить трафик (0 лидов 3+ дней)
- ⚠️ Рост CPL (>40% от нормы)
- 📉 Падение конверсии (>50% от нормы)
- 💤 Бюджет не обновлялся N дней
- 🎯 ROMI ниже заданного KPI
- 🤔 Нет продаж после запуска источника
- 📊 Корреляция пиков продаж с запуском источников

### Сравнение периодов

- **Неделя к неделе**: сравнение текущей недели с предыдущей
- **Месяц к месяцу**: сравнение текущего месяца с предыдущим
- **Метрики**: ROMI, CPL, CR(C→S), Выручка, Продажи
- **Автоматическая маркировка** негативных изменений

---

## 🚀 Установка

### Требования

- Python 3.8+
- pip

### Установка зависимостей

```bash
pip install -r requirements.txt
```

Зависимости:
- `matplotlib` - генерация графиков
- `numpy` - математические операции
- `seaborn` - улучшенная визуализация
- `python-dateutil` - работа с датами

---

## ⚡ Быстрый старт

### 1. Запуск демонстрации

```bash
python test_analytics.py
```

Этот скрипт:
- Сгенерирует демонстрационные данные (4 кампании, 45 дней)
- Создаст все типы отчетов
- Сохранит результаты в `./analytics_bot/output/`

### 2. Использование в коде

```python
from analytics_bot.main import AnalyticsReportGenerator
from analytics_bot.examples.generate_sample_data import create_demo_data

# Создать данные
period = create_demo_data()

# Создать генератор
generator = AnalyticsReportGenerator(output_dir="./output")

# Сгенерировать все отчеты
result = generator.generate_full_report(period)

print(f"График 1: {result['chart1']}")
print(f"Графики 2: {result['chart2']}")
print(f"Текстовый отчет: {result['text_report']}")
```

### 3. Генерация отдельных графиков

```python
# Только График 1
chart1_path = generator.generate_chart1(period)

# Только График 2 для конкретной кампании
chart2_path = generator.generate_chart2(period.campaigns[0])

# Только текстовый отчет
text_path = generator.generate_text_report(period)

# Только карточка кампании
card_path = generator.generate_campaign_card(period.campaigns[0])
```

---

## 📁 Структура проекта

```
analytics_bot/
├── __init__.py
├── main.py                          # Главный модуль генератора
├── models/
│   ├── __init__.py
│   └── data_models.py               # Модели данных (Campaign, Source, DailyMetrics)
├── charts/
│   ├── __init__.py
│   ├── base_chart.py                # Базовые классы графиков
│   ├── chart1_generator.py          # Генератор Графика 1
│   └── chart2_generator.py          # Генератор Графика 2
├── anomalies/
│   ├── __init__.py
│   ├── detector.py                  # Детектор аномалий
│   └── period_comparison.py         # Сравнение периодов
├── formatters/
│   ├── __init__.py
│   └── text_formatter.py            # Форматтеры текста
├── examples/
│   ├── __init__.py
│   └── generate_sample_data.py      # Генератор демо-данных
└── output/                          # Выходная директория

requirements.txt                     # Зависимости
test_analytics.py                    # Тестовый скрипт
README.md                            # Документация
```

---

## 📊 График 1 - Сквозная аналитика

### Что включает

#### 1. Шапка с метриками
```
════════════════════════════════════════════════════════════════════════════
                          СКВОЗНАЯ АНАЛИТИКА
        2024-11-01 — 2024-12-15
════════════════════════════════════════════════════════════════════════════
 Выручка: 5.9M ₽              ROMI: 155%
 Расходы: 2.3M ₽              CPL: 611 RUB
 Лиды: 3784                   LTV: 9023 RUB
 Продажи: 654                 Клики: 34629
════════════════════════════════════════════════════════════════════════════
   CR(C→L): 10.93%   |   CR(L→S): 17.28%   |   CR(C→S): 1.89%
════════════════════════════════════════════════════════════════════════════
```

#### 2. Тепловая карта продаж по дням недели
- Показывает, в какие дни недели каждая кампания приносит больше продаж
- Помогает оптимизировать расписание рекламы

#### 3. Динамика выручки по кампаниям
- Временной график с полупрозрачными кривыми для каждой кампании
- Столбики общего количества продаж на фоне
- Возможность включения/выключения отображения кампаний

#### 4. Динамика выручки по соцсетям
- Показывает, как меняется выручка от каждой соцсети во времени
- Помогает увидеть появление/исчезновение источников

#### 5. Пироги распределения
- **Выручка по кампаниям**: доля каждой кампании в общей выручке
- **Выручка по соцсетям**: доля каждой соцсети
- **Бюджет по кампаниям**: как распределены расходы
- **Бюджет по соцсетям**: распределение бюджета

#### 6. Средний LTV по кампаниям
- Горизонтальный график
- Сортировка от большего к меньшему

#### 7. Сравнение ROMI и расходов
- Вертикальные столбики ROMI
- Наложение столбиков расходов
- Быстрая оценка эффективности vs затрат

#### 8. ROMI и CPL по соцсетям
- Горизонтальный двойной график
- Показывает эффективность и стоимость лида одновременно

#### 9. CPL по кампаниям
- Стоимость лида для каждой кампании
- Горизонтальный график

#### 10. CR(C→S) по кампаниям
- Конверсия из клика в продажу
- Горизонтальный график

### Использование

```python
from analytics_bot.charts.chart1_generator import Chart1Generator
from analytics_bot.models.data_models import AnalyticsPeriod

generator = Chart1Generator()
generator.generate(period, output_path="chart1.png")
```

---

## 📈 График 2 - Аналитика по кампании

### Что включает

#### 1. Шапка с метриками кампании
Детальная информация о кампании с форматированием

#### 2. Динамика по источникам (RID)
- Выручка по каждому источнику во времени
- Столбики продаж на фоне
- Пирог распределения выручки между источниками

#### 3. Динамика по соцсетям
- Выручка по соцсетям внутри кампании
- Пирог распределения

#### 4. Распределение бюджета
- По соцсетям (пирог)
- По источникам (пирог топ-10)

#### 5. Средний LTV по источникам
- Топ-15 источников
- Горизонтальный график

#### 6. ROMI по источникам с KPI
- Вертикальные столбики ROMI
- **Линии KPI** (положительный и отрицательный)
- Цветовое кодирование:
  - Зеленый: ROMI выше положительного KPI
  - Красный: ROMI ниже отрицательного KPI
  - Оранжевый: между KPI
- Наложение расходов

#### 7. ROMI по соцсетям с KPI
- Горизонтальный график
- Линии KPI
- CPL на втором графике

#### 8. CPL по источникам
- С линиями KPI CPL
- Цветовое кодирование по KPI

#### 9. CAC по источникам
- Стоимость привлечения клиента

#### 10. CPA по источникам
- Стоимость клика

#### 11. **Анализ воронки: CPA → CPL → CAC**
Ключевой график для выявления проблем:
- Три столбца для каждого источника (CPA, CPL, CAC)
- Если CPA низкий, а CPL и CAC высокие → **проблема в воронке конверсии**
- Помогает выявить проблемы с:
  - Посадочной страницей
  - Ботом для захвата подписчиков
  - Релевантностью креатива и ЦА

#### 12-14. Конверсии по источникам
- **CR(C→S)**: клики → продажи
- **CR(C→L)**: клики → лиды
- **CR(L→S)**: лиды → продажи

### Использование

```python
from analytics_bot.charts.chart2_generator import Chart2Generator

generator = Chart2Generator()
generator.generate(campaign, output_path="chart2.png")
```

---

## 🚨 Система обнаружения аномалий

### Типы аномалий

#### 1. Аномалии ROMI
```python
# Резкое падение ROMI >30%
🔥 ROMI упал на 37% за последние дни

# Резкий рост ROMI >50%
🚀 ROMI вырос на 65% - отличный результат!

# ROMI ниже KPI
⚠️ ROMI кампании BLACKFRIDAY_2025 ниже KPI (450% < 700%)
```

#### 2. Аномалии источников
```python
# Источник перестал работать
🚫 Источник TG_ads перестал приносить трафик (0 лидов за 3 дня)

# Нет продаж после запуска
🤔 Источник blogger_Instagram_5 запущен 4 дней назад, но продаж нет
```

#### 3. Аномалии CPL
```python
# Рост CPL >40%
⚠️ CPL вырос на 43% за неделю
```

#### 4. Аномалии конверсий
```python
# Падение CR >50%
📉 CR(C→S) упала на 58%
```

#### 5. Аномалии бюджета
```python
# Бюджет не обновлялся
💤 Бюджет не обновлялся 6 дней
```

#### 6. Корреляция с запусками
```python
# Пик продаж связан с запуском
🎯 Резкий пик продаж связан со стартом blogger_YouTube_3
```

### Использование

```python
from analytics_bot.anomalies.detector import AnomalyDetector

detector = AnomalyDetector()

# Анализ кампании
alerts = detector.analyze_campaign(campaign)

# Анализ всего периода
alerts = detector.analyze_period(period)

# Вывод алертов
for alert in alerts:
    print(f"{alert.emoji} {alert.message}")
```

### Настройка порогов

Пороги обнаружения можно изменить в `detector.py`:

```python
# Падение ROMI
threshold = 0.7  # 30% падение

# Рост CPL
threshold = 1.4  # 40% рост

# Падение CR
threshold = 0.5  # 50% падение
```

---

## 📅 Сравнение периодов

### Автоматическое сравнение

Система автоматически сравнивает:
- **Текущую неделю** с прошлой неделей
- **Текущий месяц** с прошлым месяцем

### Метрики сравнения

- ROMI
- CPL
- CR(C→S)
- Выручка
- Продажи

### Формат отчета

```
🔁 Сравнение периодов

Эта неделя vs прошлая:
  • ROMI: +12%
  • CPL: +34% ⚠️
  • CR(C→S): –4%
  • Выручка: +9%

Этот месяц vs прошлый:
  • ROMI: +4%
  • CPL: –7%
  • Выручка: +15%
  • Продажи: +11%
```

### Использование

```python
from analytics_bot.anomalies.period_comparison import PeriodComparer

comparer = PeriodComparer()

# Получить метрики за периоды
all_metrics = []  # Список DailyMetrics

# Сравнить недели
week_comparison = comparer.compare_weeks(all_metrics)

# Сравнить месяцы
month_comparison = comparer.compare_months(all_metrics)

# Форматировать отчет
report = comparer.format_comparison_report(week_comparison, month_comparison)
print(report)
```

---

## 💻 Использование в коде

### Создание данных

#### Вручную

```python
from datetime import datetime, timedelta
from analytics_bot.models.data_models import (
    Campaign, Source, DailyMetrics, AnalyticsPeriod, SocialNetwork
)

# Создать кампанию
campaign = Campaign(
    campaign_id=1000,
    name="BLACKFRIDAY_2025",
    created_date=datetime(2025, 11, 1),
    sources=[],
    kpi_romi_positive=1200.0,
    kpi_romi_negative=700.0,
    kpi_cpl_positive=200.0,
    kpi_cpl_negative=500.0
)

# Создать источник
source = Source(
    rid=746233,
    name="Instagram_petrova",
    social_network=SocialNetwork.INSTAGRAM,
    campaign_id=1000,
    start_date=datetime(2025, 11, 5),
    daily_metrics=[]
)

# Добавить метрики по дням
for day in range(30):
    date = datetime(2025, 11, 1) + timedelta(days=day)
    metric = DailyMetrics(
        date=date,
        clicks=150,
        leads=20,
        sales=5,
        revenue=75000,
        spend=10000,
        refunds=0
    )
    source.daily_metrics.append(metric)

campaign.sources.append(source)

# Создать период
period = AnalyticsPeriod(
    start_date=datetime(2025, 11, 1),
    end_date=datetime(2025, 11, 30),
    campaigns=[campaign]
)
```

#### С генератором

```python
from analytics_bot.examples.generate_sample_data import (
    generate_sample_period,
    generate_sample_campaign
)

# Сгенерировать период с данными
period = generate_sample_period(days=45, num_campaigns=5)

# Или отдельную кампанию
campaign = generate_sample_campaign(
    campaign_id=1000,
    name="TEST_CAMPAIGN",
    start_date=datetime.now() - timedelta(days=30),
    days=30
)
```

### Генерация отчетов

```python
from analytics_bot.main import AnalyticsReportGenerator

# Создать генератор
generator = AnalyticsReportGenerator(output_dir="./my_reports")

# График 1
chart1 = generator.generate_chart1(period, "analytics_report.png")

# График 2 для каждой кампании
for campaign in period.campaigns:
    chart2 = generator.generate_chart2(campaign, f"campaign_{campaign.campaign_id}.png")

# Текстовый отчет
text_report = generator.generate_text_report(period, "report.txt")

# Карточка кампании
card = generator.generate_campaign_card(campaign, "campaign_card.txt")

# Все сразу
results = generator.generate_full_report(period)
```

### Интеграция с ботом

```python
import telebot
from analytics_bot.main import AnalyticsReportGenerator

bot = telebot.TeleBot("YOUR_TOKEN")
generator = AnalyticsReportGenerator()

@bot.message_handler(commands=['analytics'])
def send_analytics(message):
    # Получить данные из БД
    period = get_period_from_database()
    
    # Сгенерировать график
    chart_path = generator.generate_chart1(period)
    
    # Отправить пользователю
    with open(chart_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

@bot.message_handler(commands=['campaign'])
def send_campaign(message):
    # Получить ID кампании
    campaign_id = extract_campaign_id(message.text)
    campaign = get_campaign_from_database(campaign_id)
    
    # Сгенерировать график и карточку
    chart_path = generator.generate_chart2(campaign)
    card_path = generator.generate_campaign_card(campaign)
    
    # Отправить
    with open(chart_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    
    with open(card_path, 'r', encoding='utf-8') as f:
        bot.send_message(message.chat.id, f.read())
```

---

## 📝 Примеры

### Пример 1: Простой отчет

```python
from analytics_bot.examples.generate_sample_data import create_demo_data
from analytics_bot.main import AnalyticsReportGenerator

# Данные
period = create_demo_data()

# Генератор
gen = AnalyticsReportGenerator()

# Отчет
gen.generate_full_report(period)
```

### Пример 2: Анализ одной кампании

```python
from analytics_bot.main import AnalyticsReportGenerator
from analytics_bot.anomalies.detector import AnomalyDetector

# Получить кампанию
campaign = period.campaigns[0]

# Сгенерировать график
gen = AnalyticsReportGenerator()
chart2_path = gen.generate_chart2(campaign)

# Проанализировать аномалии
detector = AnomalyDetector()
alerts = detector.analyze_campaign(campaign)

print(f"Найдено аномалий: {len(alerts)}")
for alert in alerts:
    print(f"{alert.emoji} {alert.message}")
```

### Пример 3: Сравнение периодов

```python
from analytics_bot.anomalies.period_comparison import PeriodComparer

# Собрать метрики
all_metrics = []
for campaign in period.campaigns:
    for source in campaign.sources:
        all_metrics.extend(source.daily_metrics)

# Сравнить
comparer = PeriodComparer()
week_comp = comparer.compare_weeks(all_metrics)
month_comp = comparer.compare_months(all_metrics)

# Показать
report = comparer.format_comparison_report(week_comp, month_comp)
print(report)
```

### Пример 4: Форматирование карточки

```python
from analytics_bot.formatters.text_formatter import TextFormatter

# Форматировать список кампаний
for campaign in period.campaigns:
    card = TextFormatter.format_campaign_list_item(campaign)
    print(card)
    print("-" * 80)

# Полная карточка
full_card = TextFormatter.format_campaign_card(campaign)
print(full_card)
```

---

## 🔧 Настройка

### Изменение размера графиков

В `base_chart.py`:
```python
class BaseChart:
    def __init__(self, figsize: Tuple[int, int] = (16, 10), dpi: int = 100):
        # Изменить размер и DPI
        pass
```

### Изменение цветовой схемы

В `base_chart.py`:
```python
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    # ... изменить цвета
}
```

### Настройка KPI

```python
campaign.kpi_romi_positive = 1500.0  # 1500%
campaign.kpi_romi_negative = 800.0   # 800%
campaign.kpi_cpl_positive = 150.0    # 150 ₽
campaign.kpi_cpl_negative = 600.0    # 600 ₽
```

---

## 📊 Модели данных

### DailyMetrics
```python
@dataclass
class DailyMetrics:
    date: datetime
    clicks: int
    leads: int
    sales: int
    revenue: float
    spend: float
    refunds: int
    
    # Автоматические свойства
    @property
    def romi(self) -> float
    
    @property
    def cpl(self) -> float
    
    @property
    def cac(self) -> float
    
    @property
    def cpa(self) -> float
    
    @property
    def cr_c_l(self) -> float
    
    @property
    def cr_l_s(self) -> float
    
    @property
    def cr_c_s(self) -> float
```

### Source
```python
@dataclass
class Source:
    rid: int
    name: str
    social_network: SocialNetwork
    campaign_id: int
    start_date: Optional[datetime]
    daily_metrics: List[DailyMetrics]
    
    # Агрегированные метрики
    @property
    def total_revenue(self) -> float
    
    @property
    def avg_romi(self) -> float
    
    @property
    def avg_cpl(self) -> float
    # ... и другие
```

### Campaign
```python
@dataclass
class Campaign:
    campaign_id: int
    name: str
    created_date: datetime
    sources: List[Source]
    kpi_romi_positive: Optional[float]
    kpi_romi_negative: Optional[float]
    kpi_cpl_positive: Optional[float]
    kpi_cpl_negative: Optional[float]
    
    # Методы
    def get_top_sources(n: int, by: str) -> List[Source]
    def get_worst_sources(n: int, by: str) -> List[Source]
```

### AnalyticsPeriod
```python
@dataclass
class AnalyticsPeriod:
    start_date: datetime
    end_date: datetime
    campaigns: List[Campaign]
    
    # Методы
    def get_revenue_by_social() -> Dict[SocialNetwork, float]
    def get_spend_by_social() -> Dict[SocialNetwork, float]
```

---

## 🤝 Интеграция с базой данных

Пример функции для загрузки данных из БД:

```python
def load_period_from_db(start_date, end_date, db_connection):
    """Загрузить период из базы данных"""
    
    period = AnalyticsPeriod(
        start_date=start_date,
        end_date=end_date,
        campaigns=[]
    )
    
    # Загрузить кампании
    campaigns_data = db_connection.execute(
        "SELECT * FROM campaigns WHERE created_date BETWEEN ? AND ?",
        (start_date, end_date)
    )
    
    for camp_row in campaigns_data:
        campaign = Campaign(
            campaign_id=camp_row['id'],
            name=camp_row['name'],
            created_date=camp_row['created_date'],
            sources=[],
            kpi_romi_positive=camp_row['kpi_romi_pos'],
            kpi_romi_negative=camp_row['kpi_romi_neg'],
            kpi_cpl_positive=camp_row['kpi_cpl_pos'],
            kpi_cpl_negative=camp_row['kpi_cpl_neg']
        )
        
        # Загрузить источники
        sources_data = db_connection.execute(
            "SELECT * FROM sources WHERE campaign_id = ?",
            (campaign.campaign_id,)
        )
        
        for src_row in sources_data:
            source = Source(
                rid=src_row['rid'],
                name=src_row['name'],
                social_network=SocialNetwork(src_row['social_network']),
                campaign_id=campaign.campaign_id,
                start_date=src_row['start_date'],
                daily_metrics=[]
            )
            
            # Загрузить метрики
            metrics_data = db_connection.execute(
                "SELECT * FROM daily_metrics WHERE rid = ? AND date BETWEEN ? AND ?",
                (source.rid, start_date, end_date)
            )
            
            for metric_row in metrics_data:
                metric = DailyMetrics(
                    date=metric_row['date'],
                    clicks=metric_row['clicks'],
                    leads=metric_row['leads'],
                    sales=metric_row['sales'],
                    revenue=metric_row['revenue'],
                    spend=metric_row['spend'],
                    refunds=metric_row['refunds']
                )
                source.daily_metrics.append(metric)
            
            campaign.sources.append(source)
        
        period.campaigns.append(campaign)
    
    return period
```

---

## 🐛 Отладка

### Включение отладки matplotlib

```python
import matplotlib
matplotlib.use('TkAgg')  # Для отображения графиков
```

### Проверка данных

```python
# Проверить период
print(f"Кампаний: {len(period.campaigns)}")
print(f"Выручка: {period.total_revenue}")

# Проверить кампанию
for campaign in period.campaigns:
    print(f"{campaign.name}: {len(campaign.sources)} источников")
    
    # Проверить источники
    for source in campaign.sources:
        print(f"  {source.name}: {len(source.daily_metrics)} дней данных")
```

---

## 📞 Поддержка

При возникновении проблем:
1. Проверьте версии зависимостей: `pip list`
2. Убедитесь, что все данные корректно заполнены
3. Проверьте логи ошибок

---

## 📄 Лицензия

Этот проект создан для использования в телеграм-боте сквозной аналитики.

---

## ✨ Особенности реализации

### Производительность
- Графики генерируются асинхронно
- Используется `matplotlib` с backend 'Agg' для работы без GUI
- Оптимизированная работа с большими объемами данных

### Масштабируемость
- Поддержка неограниченного количества кампаний
- Автоматическое ограничение отображения (топ-10, топ-15) для читаемости
- Пагинация для больших отчетов

### Гибкость
- Модульная архитектура
- Легко добавить новые типы графиков
- Настраиваемые пороги и KPI
- Поддержка различных социальных сетей

---

**Версия:** 1.0.0  
**Дата:** Декабрь 2025
