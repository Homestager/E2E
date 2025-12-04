"""
Пример использования генераторов графиков в боте
"""
import json
from graph_generators.graph1_generator import Graph1Generator
from graph_generators.graph2_generator import Graph2Generator


def generate_analytics_graphs(data: dict, campaign_id: int = None) -> dict:
    """
    Генерация графиков аналитики
    
    Args:
        data: Словарь с данными аналитики
        campaign_id: ID кампании для Графика 2 (опционально)
    
    Returns:
        Словарь с путями к сгенерированным файлам
    """
    results = {}
    
    # Генерация Графика 1 - Сквозная аналитика
    try:
        graph1_gen = Graph1Generator(data)
        output1 = graph1_gen.generate('graph1_analytics.png')
        results['graph1'] = output1
        print(f"✓ График 1 создан: {output1}")
    except Exception as e:
        print(f"✗ Ошибка при создании Графика 1: {e}")
        results['graph1'] = None
    
    # Генерация Графика 2 - Аналитика по кампании
    if campaign_id:
        try:
            kpi = data.get('kpi', {
                'romi_positive': 1200,
                'romi_negative': 700,
                'cpl_positive': None,
                'cpl_negative': None
            })
            
            graph2_gen = Graph2Generator(data, campaign_id)
            output2 = graph2_gen.generate(
                f'graph2_campaign_{campaign_id}_analytics.png', 
                kpi
            )
            results['graph2'] = output2
            print(f"✓ График 2 создан: {output2}")
        except Exception as e:
            print(f"✗ Ошибка при создании Графика 2: {e}")
            results['graph2'] = None
    
    return results


# Пример использования в боте
if __name__ == '__main__':
    # Пример данных из бота
    example_data = {
        'period_start': '2025-11-01',
        'period_end': '2025-11-30',
        'campaign_name': 'ОБЩАЯ',
        'campaigns': [
            {
                'campaign_id': 1932,
                'campaign_name': 'BLACKFRIDAY_2025',
                'revenue': 1230000,
                'spend': 240000,
                'leads': 1304,
                'sales': 225,
                'clicks': 10500
            }
        ],
        'sources': [
            {
                'source_id': 746233,
                'source_name': 'Instagram_petrova',
                'campaign_id': 1932,
                'social_network': 'Instagram',
                'revenue': 500000,
                'spend': 105000,
                'leads': 600,
                'sales': 100,
                'clicks': 4500
            }
        ],
        'transactions': [],
        'kpi': {
            'romi_positive': 1200,
            'romi_negative': 700,
            'cpl_positive': None,
            'cpl_negative': None
        }
    }
    
    # Генерация графиков
    results = generate_analytics_graphs(example_data, campaign_id=1932)
    
    print("\nРезультаты:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
