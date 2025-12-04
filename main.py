"""
Основной скрипт для генерации графиков сквозной аналитики
"""
import json
import sys
import numpy as np
from datetime import datetime, timedelta
from graph_generators.graph1_generator import Graph1Generator
from graph_generators.graph2_generator import Graph2Generator


def generate_sample_data():
    """Генерация примерных данных для тестирования"""
    period_start = datetime.now() - timedelta(days=30)
    period_end = datetime.now()
    
    campaigns = [
        {
            'campaign_id': 1,
            'campaign_name': 'BLACKFRIDAY_2025',
            'revenue': 1230000,
            'spend': 240000,
            'leads': 1304,
            'sales': 225,
            'clicks': 10500
        },
        {
            'campaign_id': 2,
            'campaign_name': 'NEW_YEAR_2026',
            'revenue': 890000,
            'spend': 180000,
            'leads': 980,
            'sales': 156,
            'clicks': 8200
        },
        {
            'campaign_id': 3,
            'campaign_name': 'SPRING_SALE',
            'revenue': 2100000,
            'spend': 450000,
            'leads': 1500,
            'sales': 380,
            'clicks': 12500
        }
    ]
    
    sources = []
    social_networks = ['Instagram', 'Telegram', 'YouTube', 'VK']
    
    for campaign in campaigns:
        for i, social in enumerate(social_networks):
            source = {
                'source_id': len(sources) + 1,
                'source_name': f'{social}_source_{i+1}',
                'campaign_id': campaign['campaign_id'],
                'social_network': social,
                'revenue': campaign['revenue'] * (0.2 + i * 0.1),
                'spend': campaign['spend'] * (0.2 + i * 0.1),
                'leads': int(campaign['leads'] * (0.2 + i * 0.1)),
                'sales': int(campaign['sales'] * (0.2 + i * 0.1)),
                'clicks': int(campaign['clicks'] * (0.2 + i * 0.1))
            }
            sources.append(source)
    
    transactions = []
    current_date = period_start
    while current_date <= period_end:
        for campaign in campaigns:
            for _ in range(np.random.randint(5, 20)):
                transactions.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'campaign_id': campaign['campaign_id'],
                    'source_id': np.random.randint(1, len(sources) + 1),
                    'revenue': np.random.randint(5000, 50000),
                    'social_network': np.random.choice(social_networks)
                })
        current_date += timedelta(days=1)
    
    return {
        'period_start': period_start.strftime('%Y-%m-%d'),
        'period_end': period_end.strftime('%Y-%m-%d'),
        'campaign_name': 'ОБЩАЯ',
        'campaigns': campaigns,
        'sources': sources,
        'transactions': transactions
    }


def main():
    """Основная функция"""
    # Загрузка данных (можно из файла или БД)
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("Генерация примерных данных...")
        data = generate_sample_data()
    
    # Генерация Графика 1 - Сквозная аналитика
    print("Генерация Графика 1: Сквозная аналитика по всем кампаниям...")
    graph1_gen = Graph1Generator(data)
    output1 = graph1_gen.generate('graph1_analytics.png')
    print(f"График 1 сохранен: {output1}")
    
    # Генерация Графика 2 - Аналитика по кампании
    if data.get('campaigns'):
        campaign_id = data['campaigns'][0]['campaign_id']
        print(f"Генерация Графика 2: Аналитика по кампании {campaign_id}...")
        
        kpi = {
            'romi_positive': 1200,
            'romi_negative': 700,
            'cpl_positive': None,
            'cpl_negative': None
        }
        
        graph2_gen = Graph2Generator(data, campaign_id)
        output2 = graph2_gen.generate(f'graph2_campaign_{campaign_id}_analytics.png', kpi)
        print(f"График 2 сохранен: {output2}")
    
    print("\nГенерация завершена!")


if __name__ == '__main__':
    main()
