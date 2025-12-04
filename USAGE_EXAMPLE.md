# Примеры использования системы аналитики

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск демонстрации

```bash
python3 test_analytics.py
```

Результат:
- `./analytics_bot/output/chart1_analytics_*.png` - График 1 (сквозная аналитика)
- `./analytics_bot/output/chart2_campaign_*.png` - Графики 2 (по каждой кампании)
- `./analytics_bot/output/text_report_*.txt` - Текстовый отчет с алертами
- `./analytics_bot/output/campaign_card_*.txt` - Карточки кампаний

## Интеграция с телеграм-ботом

### Пример 1: Отправка сквозной аналитики

```python
import telebot
from analytics_bot.main import AnalyticsReportGenerator
from your_database import load_period_from_db

bot = telebot.TeleBot("YOUR_TOKEN")
generator = AnalyticsReportGenerator()

@bot.message_handler(commands=['analytics'])
def send_analytics(message):
    """Отправить сквозную аналитику"""
    
    # Получить данные за последние 30 дней
    period = load_period_from_db(days=30)
    
    # Сгенерировать график
    chart_path = generator.generate_chart1(period)
    
    # Отправить график
    with open(chart_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo,
                      caption="📊 Сквозная аналитика за 30 дней")
    
    # Отправить текстовый отчет
    text_path = generator.generate_text_report(period)
    with open(text_path, 'r', encoding='utf-8') as f:
        bot.send_message(message.chat.id, f.read())

bot.polling()
```

### Пример 2: Карточка кампании с графиком

```python
@bot.message_handler(commands=['campaign'])
def send_campaign(message):
    """Отправить детальную информацию по кампании"""
    
    # Извлечь ID кампании из команды: /campaign 1000
    try:
        campaign_id = int(message.text.split()[1])
    except:
        bot.reply_to(message, "Используйте: /campaign <ID>")
        return
    
    # Загрузить кампанию из БД
    campaign = load_campaign_from_db(campaign_id)
    
    if not campaign:
        bot.reply_to(message, "❌ Кампания не найдена")
        return
    
    # Сгенерировать график
    chart_path = generator.generate_chart2(campaign)
    
    # Отправить график
    with open(chart_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    
    # Отправить карточку
    card_path = generator.generate_campaign_card(campaign)
    with open(card_path, 'r', encoding='utf-8') as f:
        card_text = f.read()
        
        # Разбить на части если текст слишком длинный
        max_len = 4096
        for i in range(0, len(card_text), max_len):
            bot.send_message(message.chat.id, card_text[i:i+max_len])
```

### Пример 3: Список кампаний с кнопками

```python
from telebot import types

@bot.message_handler(commands=['campaigns'])
def list_campaigns(message):
    """Показать список кампаний"""
    
    period = load_period_from_db(days=90)
    
    # Создать клавиатуру с кнопками
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for campaign in period.campaigns:
        # Форматировать строку кампании
        text = f"🎯 {campaign.name} | ROMI: {campaign.avg_romi:.0f}%"
        
        # Добавить кнопку
        button = types.InlineKeyboardButton(
            text=text,
            callback_data=f"campaign_{campaign.campaign_id}"
        )
        markup.add(button)
    
    bot.send_message(message.chat.id, 
                    "📋 Ваши кампании:",
                    reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('campaign_'))
def handle_campaign_button(call):
    """Обработать нажатие на кампанию"""
    
    campaign_id = int(call.data.split('_')[1])
    campaign = load_campaign_from_db(campaign_id)
    
    # Отправить график
    chart_path = generator.generate_chart2(campaign)
    with open(chart_path, 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo)
    
    bot.answer_callback_query(call.id)
```

## Работа с данными из базы данных

### Пример функции загрузки данных

```python
from datetime import datetime, timedelta
from analytics_bot.models.data_models import (
    AnalyticsPeriod, Campaign, Source, DailyMetrics, SocialNetwork
)

def load_period_from_db(days=30):
    """Загрузить период из БД"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    period = AnalyticsPeriod(
        start_date=start_date,
        end_date=end_date,
        campaigns=[]
    )
    
    # Загрузить кампании из БД
    # Замените на ваш SQL запрос
    campaigns = db.execute("""
        SELECT id, name, created_date, 
               kpi_romi_positive, kpi_romi_negative,
               kpi_cpl_positive, kpi_cpl_negative
        FROM campaigns
        WHERE created_date >= ?
    """, (start_date,))
    
    for camp_row in campaigns:
        campaign = Campaign(
            campaign_id=camp_row['id'],
            name=camp_row['name'],
            created_date=camp_row['created_date'],
            sources=[],
            kpi_romi_positive=camp_row['kpi_romi_positive'],
            kpi_romi_negative=camp_row['kpi_romi_negative'],
            kpi_cpl_positive=camp_row['kpi_cpl_positive'],
            kpi_cpl_negative=camp_row['kpi_cpl_negative']
        )
        
        # Загрузить источники
        sources = db.execute("""
            SELECT rid, name, social_network, start_date
            FROM sources
            WHERE campaign_id = ?
        """, (campaign.campaign_id,))
        
        for src_row in sources:
            source = Source(
                rid=src_row['rid'],
                name=src_row['name'],
                social_network=SocialNetwork(src_row['social_network']),
                campaign_id=campaign.campaign_id,
                start_date=src_row['start_date'],
                daily_metrics=[]
            )
            
            # Загрузить метрики по дням
            metrics = db.execute("""
                SELECT date, clicks, leads, sales, revenue, spend, refunds
                FROM daily_metrics
                WHERE rid = ? AND date BETWEEN ? AND ?
                ORDER BY date
            """, (source.rid, start_date, end_date))
            
            for metric_row in metrics:
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

## Расписание автоматических отчетов

```python
import schedule
import time

def generate_daily_report():
    """Генерировать ежедневный отчет"""
    
    period = load_period_from_db(days=7)
    generator = AnalyticsReportGenerator()
    
    # Сгенерировать отчеты
    result = generator.generate_full_report(period)
    
    # Отправить отчеты администраторам
    admin_chat_ids = [123456789, 987654321]  # ID администраторов
    
    for admin_id in admin_chat_ids:
        # График 1
        with open(result['chart1'], 'rb') as photo:
            bot.send_photo(admin_id, photo,
                          caption="📊 Ежедневный отчет - Сквозная аналитика")
        
        # Текстовый отчет
        with open(result['text_report'], 'r', encoding='utf-8') as f:
            bot.send_message(admin_id, f.read())

# Запланировать отчет каждый день в 9:00
schedule.every().day.at("09:00").do(generate_daily_report)

# Запланировать еженедельный отчет по понедельникам
schedule.every().monday.at("10:00").do(lambda: generate_weekly_report())

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Пользовательские настройки

### Изменение KPI через бот

```python
@bot.message_handler(commands=['set_kpi'])
def set_kpi(message):
    """Установить KPI для кампании"""
    
    # /set_kpi 1000 romi_positive 1500
    try:
        parts = message.text.split()
        campaign_id = int(parts[1])
        kpi_type = parts[2]  # romi_positive, romi_negative, cpl_positive, cpl_negative
        value = float(parts[3])
    except:
        bot.reply_to(message, 
                    "Используйте: /set_kpi <campaign_id> <kpi_type> <value>\n"
                    "Пример: /set_kpi 1000 romi_positive 1500")
        return
    
    # Сохранить в БД
    db.execute(f"""
        UPDATE campaigns
        SET kpi_{kpi_type} = ?
        WHERE id = ?
    """, (value, campaign_id))
    
    bot.reply_to(message, f"✅ KPI обновлен: {kpi_type} = {value}")
```

## Экспорт данных

### CSV экспорт

```python
import csv

def export_campaign_to_csv(campaign, filepath):
    """Экспортировать кампанию в CSV"""
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Заголовки
        writer.writerow([
            'Источник', 'RID', 'Соцсеть', 'Выручка', 'Расходы', 
            'ROMI', 'Лиды', 'Продажи', 'CPL', 'CAC', 'CR(C→S)'
        ])
        
        # Данные
        for source in campaign.sources:
            writer.writerow([
                source.name,
                source.rid,
                source.social_network.value,
                source.total_revenue,
                source.total_spend,
                f"{source.avg_romi:.1f}%",
                source.total_leads,
                source.total_sales,
                source.avg_cpl,
                source.avg_cac,
                f"{(source.total_sales / source.total_clicks * 100):.2f}%" 
                    if source.total_clicks > 0 else "0%"
            ])

@bot.message_handler(commands=['export_csv'])
def export_csv(message):
    """Экспортировать данные кампании в CSV"""
    
    try:
        campaign_id = int(message.text.split()[1])
    except:
        bot.reply_to(message, "Используйте: /export_csv <campaign_id>")
        return
    
    campaign = load_campaign_from_db(campaign_id)
    
    filepath = f"./exports/campaign_{campaign_id}.csv"
    export_campaign_to_csv(campaign, filepath)
    
    with open(filepath, 'rb') as doc:
        bot.send_document(message.chat.id, doc,
                         caption=f"📊 CSV экспорт кампании {campaign.name}")
```

## Интеграция с webhook

```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/webhook/analytics', methods=['POST'])
def analytics_webhook():
    """Webhook для автоматической генерации отчетов"""
    
    data = request.json
    
    # Получить параметры
    campaign_id = data.get('campaign_id')
    chat_id = data.get('chat_id')
    
    # Загрузить кампанию
    campaign = load_campaign_from_db(campaign_id)
    
    # Сгенерировать отчет
    generator = AnalyticsReportGenerator()
    chart_path = generator.generate_chart2(campaign)
    
    # Отправить в телеграм
    with open(chart_path, 'rb') as photo:
        bot.send_photo(chat_id, photo)
    
    return json.dumps({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(port=5000)
```

## Мониторинг и алерты в реальном времени

```python
import asyncio

async def monitor_campaigns():
    """Мониторинг кампаний и отправка алертов"""
    
    from analytics_bot.anomalies.detector import AnomalyDetector
    
    detector = AnomalyDetector()
    
    while True:
        # Загрузить данные
        period = load_period_from_db(days=7)
        
        # Обнаружить аномалии
        alerts = detector.analyze_period(period)
        
        # Отправить критические алерты
        critical_alerts = [a for a in alerts if a.severity == 'critical']
        
        if critical_alerts:
            admin_chat_ids = [123456789]  # ID администраторов
            
            for admin_id in admin_chat_ids:
                message = "🚨 КРИТИЧЕСКИЕ АЛЕРТЫ:\n\n"
                for alert in critical_alerts:
                    message += f"{alert.emoji} {alert.message}\n"
                
                bot.send_message(admin_id, message)
        
        # Ждать 1 час
        await asyncio.sleep(3600)

# Запустить мониторинг
asyncio.run(monitor_campaigns())
```

---

## Тестирование

Запустите тесты:

```bash
python3 test_analytics.py
```

Проверьте созданные файлы:

```bash
ls -lh ./analytics_bot/output/
```

Просмотрите текстовый отчет:

```bash
cat ./analytics_bot/output/text_report_*.txt
```

---

Для получения дополнительной информации см. [README.md](README.md)
