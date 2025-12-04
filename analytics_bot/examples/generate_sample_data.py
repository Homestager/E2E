"""
Генератор тестовых данных для демонстрации системы аналитики
"""

from datetime import datetime, timedelta
import random
from ..models.data_models import (
    Campaign, Source, DailyMetrics, AnalyticsPeriod, SocialNetwork
)


def generate_sample_period(days: int = 30, num_campaigns: int = 3) -> AnalyticsPeriod:
    """Сгенерировать тестовый период с данными"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    period = AnalyticsPeriod(
        start_date=start_date,
        end_date=end_date,
        campaigns=[]
    )
    
    campaign_names = [
        "BLACKFRIDAY_2025",
        "NEW_YEAR_PROMO",
        "SPRING_SALE",
        "SUMMER_BLAST",
        "BACK_TO_SCHOOL"
    ]
    
    for i in range(num_campaigns):
        campaign = generate_sample_campaign(
            campaign_id=1000 + i,
            name=campaign_names[i % len(campaign_names)],
            start_date=start_date,
            days=days
        )
        period.campaigns.append(campaign)
    
    return period


def generate_sample_campaign(campaign_id: int, name: str, 
                            start_date: datetime, days: int = 30) -> Campaign:
    """Сгенерировать тестовую кампанию"""
    
    campaign = Campaign(
        campaign_id=campaign_id,
        name=name,
        created_date=start_date,
        sources=[],
        kpi_romi_positive=1200.0,
        kpi_romi_negative=700.0,
        kpi_cpl_positive=200.0,
        kpi_cpl_negative=500.0
    )
    
    # Генерируем источники для разных соцсетей
    socials = [SocialNetwork.INSTAGRAM, SocialNetwork.TELEGRAM, 
              SocialNetwork.YOUTUBE, SocialNetwork.VK]
    
    source_templates = [
        "blogger_",
        "ads_",
        "influencer_",
        "partner_",
        "channel_"
    ]
    
    num_sources = random.randint(5, 12)
    
    for i in range(num_sources):
        social = random.choice(socials)
        template = random.choice(source_templates)
        source_name = f"{template}{social.value}_{i+1}"
        
        # Дата старта источника может быть в середине периода
        days_offset = random.randint(0, days // 2)
        source_start = start_date + timedelta(days=days_offset)
        
        source = generate_sample_source(
            rid=700000 + campaign_id * 100 + i,
            name=source_name,
            social_network=social,
            campaign_id=campaign_id,
            start_date=source_start,
            days=days - days_offset
        )
        
        campaign.sources.append(source)
    
    return campaign


def generate_sample_source(rid: int, name: str, social_network: SocialNetwork,
                          campaign_id: int, start_date: datetime, days: int) -> Source:
    """Сгенерировать тестовый источник"""
    
    source = Source(
        rid=rid,
        name=name,
        social_network=social_network,
        campaign_id=campaign_id,
        start_date=start_date,
        daily_metrics=[]
    )
    
    # Базовые параметры для генерации метрик
    base_clicks = random.randint(50, 500)
    base_spend = random.randint(5000, 50000)
    quality_factor = random.uniform(0.5, 2.0)  # Фактор качества источника
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # Добавляем сезонность (выходные могут иметь другие показатели)
        weekday_multiplier = 1.0
        if current_date.weekday() >= 5:  # Суббота, воскресенье
            weekday_multiplier = random.uniform(0.7, 1.3)
        
        # Добавляем тренд (рост или падение со временем)
        trend_multiplier = 1.0 + (day / days) * random.uniform(-0.3, 0.3)
        
        # Случайный шум
        noise = random.uniform(0.8, 1.2)
        
        clicks = int(base_clicks * weekday_multiplier * trend_multiplier * noise)
        spend = base_spend * weekday_multiplier * trend_multiplier * noise
        
        # Конверсии зависят от качества источника
        cr_cl = random.uniform(0.05, 0.20) * quality_factor  # 5-20%
        cr_ls = random.uniform(0.10, 0.30) * quality_factor  # 10-30%
        
        leads = int(clicks * cr_cl)
        sales = int(leads * cr_ls)
        
        # Выручка зависит от количества продаж
        avg_check = random.uniform(15000, 50000)  # Средний чек
        revenue = sales * avg_check
        
        # Возвраты (редко)
        refunds = random.randint(0, max(1, sales // 20))
        
        metric = DailyMetrics(
            date=current_date,
            clicks=clicks,
            leads=leads,
            sales=sales,
            revenue=revenue,
            spend=spend,
            refunds=refunds
        )
        
        source.daily_metrics.append(metric)
    
    return source


def create_demo_data() -> AnalyticsPeriod:
    """Создать демонстрационные данные для тестирования"""
    
    print("Генерация демонстрационных данных...")
    
    # Генерируем период в 45 дней с 4 кампаниями
    period = generate_sample_period(days=45, num_campaigns=4)
    
    print(f"Сгенерировано:")
    print(f"  - Период: {period.start_date.date()} — {period.end_date.date()}")
    print(f"  - Кампаний: {len(period.campaigns)}")
    
    total_sources = sum(len(c.sources) for c in period.campaigns)
    print(f"  - Источников: {total_sources}")
    
    print(f"\nМетрики периода:")
    print(f"  - Выручка: {period.total_revenue:,.0f} ₽")
    print(f"  - Расходы: {period.total_spend:,.0f} ₽")
    print(f"  - ROMI: {period.avg_romi:.1f}%")
    print(f"  - Лиды: {period.total_leads}")
    print(f"  - Продажи: {period.total_sales}")
    print(f"  - CPL: {period.avg_cpl:.0f} ₽")
    
    return period


if __name__ == "__main__":
    # Тестовый запуск
    demo_period = create_demo_data()
    
    print("\nДанные успешно сгенерированы!")
    print(f"\nПример кампании:")
    if demo_period.campaigns:
        c = demo_period.campaigns[0]
        print(f"  Название: {c.name}")
        print(f"  ID: {c.campaign_id}")
        print(f"  Источников: {len(c.sources)}")
        print(f"  Выручка: {c.total_revenue:,.0f} ₽")
        print(f"  ROMI: {c.avg_romi:.1f}%")
