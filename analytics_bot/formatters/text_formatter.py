"""
Форматтеры текстовых данных для карточек и отчетов
"""

from typing import List, Dict
from datetime import datetime
from ..models.data_models import Campaign, Source, AnalyticsPeriod, SocialNetwork
from ..anomalies.detector import Alert


class TextFormatter:
    """Форматтер текстовых данных"""
    
    @staticmethod
    def format_number(value: float, decimals: int = 0) -> str:
        """Форматировать число с разделителями тысяч"""
        if decimals == 0:
            return f"{int(value):,}".replace(",", " ")
        else:
            return f"{value:,.{decimals}f}".replace(",", " ")
    
    @staticmethod
    def format_money(value: float, currency: str = "₽") -> str:
        """Форматировать деньги"""
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M {currency}"
        elif value >= 1_000:
            return f"{TextFormatter.format_number(value)} {currency}"
        else:
            return f"{value:.0f} {currency}"
    
    @staticmethod
    def format_percent(value: float) -> str:
        """Форматировать процент"""
        return f"{value:.0f}%"
    
    @staticmethod
    def format_campaign_list_item(campaign: Campaign) -> str:
        """Форматировать элемент списка кампаний"""
        lines = []
        lines.append(f"🎯 {campaign.name}")
        lines.append(f"ID: {campaign.campaign_id}")
        lines.append(f"Создана: {campaign.created_date.strftime('%Y-%m-%d')}")
        lines.append(f"Lead: {campaign.total_leads} | Sale: {campaign.total_sales} | Revenue: {TextFormatter.format_money(campaign.total_revenue)}")
        lines.append(f"ROMI: {TextFormatter.format_percent(campaign.avg_romi)} | CPL: {campaign.avg_cpl:.0f} руб | CR C→S: {TextFormatter.format_percent(campaign.cr_c_s)}")
        return "\n".join(lines)
    
    @staticmethod
    def format_campaign_card(campaign: Campaign) -> str:
        """Форматировать карточку кампании"""
        lines = []
        lines.append(f"📊 Кампания: {campaign.name}")
        lines.append(f"ID: {campaign.campaign_id}")
        lines.append(f"Создана: {campaign.created_date.strftime('%Y-%m-%d')}")
        lines.append("")
        
        lines.append("💰 Итоги:")
        lines.append(f"Выручка: {TextFormatter.format_money(campaign.total_revenue)}")
        lines.append(f"Расходы: {TextFormatter.format_money(campaign.total_spend)}")
        lines.append(f"ROMI: {TextFormatter.format_percent(campaign.avg_romi)}")
        lines.append(f"CPL: {campaign.avg_cpl:.0f} ₽")
        lines.append("")
        
        # Топ источники
        top_sources = campaign.get_top_sources(3, by="romi")
        if top_sources:
            lines.append("🔥 Топ источники:")
            for source in top_sources[:3]:
                lines.append(f"{source.name} — ROMI {TextFormatter.format_percent(source.avg_romi)}")
            lines.append("")
        
        # Худшие источники
        worst_sources = campaign.get_worst_sources(3, by="romi")
        if worst_sources and worst_sources[0].avg_romi < 0:
            lines.append("⚠️ Хуже всех:")
            for source in worst_sources[:3]:
                if source.avg_romi < 100:  # Показываем только плохие
                    lines.append(f"{source.name} — ROMI {TextFormatter.format_percent(source.avg_romi)}")
            lines.append("")
        
        lines.append("📈 Конверсии:")
        lines.append(f"CR(C→L): {TextFormatter.format_percent(campaign.cr_c_l)}")
        lines.append(f"CR(L→S): {TextFormatter.format_percent(campaign.cr_l_s)}")
        lines.append(f"CR(C→S): {TextFormatter.format_percent(campaign.cr_c_s)}")
        lines.append("")
        
        # Соцсети
        socials: Dict[SocialNetwork, Dict] = {}
        for source in campaign.sources:
            if source.social_network not in socials:
                socials[source.social_network] = {
                    'revenue': 0,
                    'spend': 0,
                    'leads': 0
                }
            socials[source.social_network]['revenue'] += source.total_revenue
            socials[source.social_network]['spend'] += source.total_spend
            socials[source.social_network]['leads'] += source.total_leads
        
        if socials:
            lines.append("📂 Соцсети:")
            for social, data in socials.items():
                romi = ((data['revenue'] - data['spend']) / data['spend'] * 100) if data['spend'] > 0 else 0
                cpl = data['spend'] / data['leads'] if data['leads'] > 0 else 0
                lines.append(f"{social.value} — ROMI {TextFormatter.format_percent(romi)} | CPL {cpl:.0f} ₽")
            lines.append("")
        
        # Распределение бюджета
        total_spend = campaign.total_spend
        if total_spend > 0 and socials:
            lines.append("💸 Распределение бюджета:")
            for social, data in sorted(socials.items(), key=lambda x: x[1]['spend'], reverse=True):
                percent = (data['spend'] / total_spend) * 100
                lines.append(f"{social.value} — {percent:.0f}%")
            lines.append("")
        
        lines.append("----------------------------------")
        lines.append("")
        lines.append("📁 Графики:")
        lines.append(f"1. Сквозная по кампании (график2): /analytics_source_{campaign.campaign_id}")
        lines.append(f"2. CSV кампании: /analytics_file_{campaign.campaign_id}")
        lines.append("")
        lines.append("----------------------------------")
        lines.append("")
        
        lines.append("🎯 KPI:")
        lines.append(f"ROMI positive: {campaign.kpi_romi_positive if campaign.kpi_romi_positive else 'не задан (1200% по умолчанию)'}")
        lines.append(f"ROMI negative: {campaign.kpi_romi_negative if campaign.kpi_romi_negative else 'не задан (700% по умолчанию)'}")
        lines.append(f"CPL positive: {campaign.kpi_cpl_positive if campaign.kpi_cpl_positive else 'не задан'}")
        lines.append(f"CPL negative: {campaign.kpi_cpl_negative if campaign.kpi_cpl_negative else 'не задан'}")
        lines.append("")
        
        lines.append("💡 Задать KPI:")
        lines.append(f"/kpi_positive_{campaign.campaign_id} число")
        lines.append(f"/kpi_negative_{campaign.campaign_id} число")
        lines.append(f"/cpl_positive_{campaign.campaign_id} число")
        lines.append(f"/cpl_negative_{campaign.campaign_id} число")
        lines.append("")
        lines.append("----------------------------------")
        lines.append("")
        
        lines.append("📌 Экспресс-аналитика по источникам:")
        for source in campaign.sources[:5]:
            lines.append(f"{source.name} (RID {source.rid}) — ROMI {TextFormatter.format_percent(source.avg_romi)}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_header(campaign: Campaign) -> str:
        """Форматировать шапку отчета"""
        lines = []
        lines.append("=" * 74)
        lines.append(f"{'ИТОГИ КАМПАНИИ':^74}")
        lines.append(f"{campaign.name} (ID: {campaign.campaign_id})".center(74))
        lines.append("=" * 74)
        
        # Первая строка метрик
        line1_left = f"Выручка: {TextFormatter.format_money(campaign.total_revenue)}"
        line1_right = f"ROMI: {TextFormatter.format_percent(campaign.avg_romi)}"
        lines.append(f"| {line1_left:<35}| {line1_right:<35}|")
        
        # Вторая строка метрик
        line2_left = f"Расходы: {TextFormatter.format_money(campaign.total_spend)}"
        line2_right = f"CPL: {campaign.avg_cpl:.0f} RUB"
        lines.append(f"| {line2_left:<35}| {line2_right:<35}|")
        
        # Третья строка метрик
        line3_left = f"Лиды: {TextFormatter.format_number(campaign.total_leads)}"
        line3_right = f"LTV: {campaign.avg_ltv:.0f} RUB"
        lines.append(f"| {line3_left:<35}| {line3_right:<35}|")
        
        # Четвертая строка метрик
        line4_left = f"Продажи: {TextFormatter.format_number(campaign.total_sales)}"
        line4_right = f"Клики: {TextFormatter.format_number(campaign.total_clicks)}"
        lines.append(f"| {line4_left:<35}| {line4_right:<35}|")
        
        lines.append("=" * 74)
        
        # Конверсии
        cr_line = f"CR(C->L): {TextFormatter.format_percent(campaign.cr_c_l):<8} | CR(L->S): {TextFormatter.format_percent(campaign.cr_l_s):<8} | CR(C->S): {TextFormatter.format_percent(campaign.cr_c_s):<8}"
        lines.append(f"|{cr_line:^72}|")
        lines.append("=" * 74)
        
        return "\n".join(lines)
    
    @staticmethod
    def format_alerts(alerts: List[Alert]) -> str:
        """Форматировать список алертов"""
        if not alerts:
            return "🧠 Всё стабильно. Аномалий не обнаружено."
        
        lines = []
        lines.append("⚠️ Алерты (автоматические сигналы)\n")
        
        # Группируем по severity
        critical = [a for a in alerts if a.severity == "critical"]
        warnings = [a for a in alerts if a.severity == "warning"]
        info = [a for a in alerts if a.severity == "info"]
        
        for alert in critical + warnings + info:
            lines.append(f"{alert.emoji} {alert.message}")
        
        return "\n".join(lines)
