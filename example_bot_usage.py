#!/usr/bin/env python3
"""
Example Telegram Bot Integration

This file demonstrates how to integrate the analytics reports
into a Telegram bot using python-telegram-bot or aiogram.

The actual bot code depends on your framework, but this shows
the general pattern for handling commands and generating reports.
"""

from datetime import date
from typing import Optional

# Import the analytics module
from analytics import AnalyticsPeriod, Campaign, Source, SocialNetwork
from analytics.bot_integration import MarketingAnalyticsBot
from analytics.data_generator import SampleDataGenerator


def get_analytics_period_from_database() -> AnalyticsPeriod:
    """
    Replace this with your actual database query.
    Should return an AnalyticsPeriod with your real data.
    """
    # For demo purposes, generate sample data
    generator = SampleDataGenerator(seed=42)
    return generator.generate_analytics_period(
        num_days=30,
        num_campaigns=5,
        sources_per_campaign=6
    )


# Example handler implementations for Telegram bot
class TelegramBotHandlers:
    """
    Example handlers for Telegram bot commands.
    """
    
    def __init__(self):
        # Initialize with data
        self.period = get_analytics_period_from_database()
        self.bot = MarketingAnalyticsBot(self.period)
    
    async def handle_cross_analytics_button(self, update, context):
        """
        Handler for "СКВОЗНАЯ АНАЛИТИКА" button under profile.
        Sends Graph 1 PNG.
        """
        # Send "generating..." message
        message = await update.message.reply_text("📊 Генерирую отчет...")
        
        try:
            # Generate Graph 1
            png_bytes = self.bot.generate_graph1(save_file=False)
            
            # Send the PNG
            await update.message.reply_photo(
                photo=png_bytes,
                caption="📊 Сквозная аналитика\n\n" + 
                        self.bot.get_cross_analytics_summary()
            )
            
        except Exception as e:
            await message.edit_text(f"❌ Ошибка: {e}")
    
    async def handle_campaigns_button(self, update, context):
        """
        Handler for "КАМПАНИИ" button.
        Shows list of campaigns with summary cards.
        """
        campaigns = self.bot.get_campaign_list()
        
        # Build message with campaign list
        text = "📋 **Список кампаний:**\n\n"
        
        for camp in campaigns:
            text += camp["summary"] + "\n\n"
        
        await update.message.reply_text(
            text,
            parse_mode="Markdown"
        )
    
    async def handle_campaign_card_command(self, update, context):
        """
        Handler for /campaign_{id} command.
        Shows detailed campaign card.
        """
        # Extract campaign_id from command
        command = update.message.text
        campaign_id = command.split("_")[-1]
        
        card = self.bot.get_campaign_card(campaign_id)
        
        if card:
            await update.message.reply_text(card)
        else:
            await update.message.reply_text(f"❌ Кампания {campaign_id} не найдена")
    
    async def handle_analytics_source_command(self, update, context):
        """
        Handler for /analytics_source_{id} command.
        Generates and sends Graph 2 for specific campaign.
        """
        command = update.message.text
        campaign_id = command.split("_")[-1]
        
        message = await update.message.reply_text("📊 Генерирую отчет по кампании...")
        
        try:
            png_bytes = self.bot.generate_graph2(campaign_id, save_file=False)
            
            if png_bytes:
                await update.message.reply_photo(
                    photo=png_bytes,
                    caption=f"📊 Аналитика кампании {campaign_id}"
                )
            else:
                await message.edit_text(f"❌ Кампания {campaign_id} не найдена")
                
        except Exception as e:
            await message.edit_text(f"❌ Ошибка: {e}")
    
    async def handle_rid_command(self, update, context):
        """
        Handler for /rid_{rid_id} command.
        Shows source/RID card.
        """
        command = update.message.text
        rid = command.split("_")[-1]
        
        card = self.bot.get_source_card(rid)
        
        if card:
            await update.message.reply_text(card)
        else:
            await update.message.reply_text(f"❌ Источник {rid} не найден")
    
    async def handle_kpi_command(self, update, context):
        """
        Handler for /kpi_positive_{id} and /kpi_negative_{id} commands.
        Sets KPI for campaign.
        """
        command = update.message.text
        parts = command.split("_")
        
        if len(parts) < 3:
            await update.message.reply_text("❌ Неверный формат команды")
            return
        
        kpi_type = parts[1]  # "positive" or "negative"
        campaign_id = parts[2]
        
        # Get value from next message or same message
        try:
            value = float(parts[3]) if len(parts) > 3 else None
        except ValueError:
            await update.message.reply_text("❌ Укажите числовое значение")
            return
        
        if value is None:
            await update.message.reply_text(
                f"💡 Укажите значение ROMI {kpi_type}:\n"
                f"/kpi_{kpi_type}_{campaign_id} ЧИСЛО"
            )
            return
        
        if kpi_type == "positive":
            success = self.bot.set_campaign_kpi(campaign_id, romi_positive=value)
        else:
            success = self.bot.set_campaign_kpi(campaign_id, romi_negative=value)
        
        if success:
            await update.message.reply_text(f"✅ KPI установлен: ROMI {kpi_type} = {value}%")
        else:
            await update.message.reply_text(f"❌ Кампания {campaign_id} не найдена")
    
    async def handle_alerts_command(self, update, context):
        """
        Handler for /alerts command.
        Shows current alerts.
        """
        alerts_text = self.bot.get_alerts_text()
        comparison_week = self.bot.get_comparison_text("week")
        comparison_month = self.bot.get_comparison_text("month")
        
        text = f"{alerts_text}\n\n{comparison_week}\n\n{comparison_month}"
        
        await update.message.reply_text(text)


# Example of keyboard buttons layout
def get_main_keyboard():
    """
    Returns inline keyboard for main menu.
    """
    return [
        [{"text": "📊 Сквозная аналитика", "callback_data": "cross_analytics"}],
        [{"text": "📁 Кампании", "callback_data": "campaigns"}],
        [{"text": "⚠️ Алерты", "callback_data": "alerts"}],
    ]


def get_campaign_keyboard(campaigns):
    """
    Returns inline keyboard with campaign buttons.
    """
    buttons = []
    for camp in campaigns:
        buttons.append([{
            "text": f"🎯 {camp['name']} (ROMI {camp['romi']:.0f}%)",
            "callback_data": f"campaign_{camp['id']}"
        }])
    return buttons


# Demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("Marketing Analytics Bot - Example Usage")
    print("=" * 60)
    
    # Initialize with sample data
    period = get_analytics_period_from_database()
    bot = MarketingAnalyticsBot(period, output_dir="./output")
    
    # Print available campaigns
    print("\n📋 Available campaigns:")
    for camp in bot.get_campaign_list():
        print(f"  • {camp['name']} (ID: {camp['id']})")
        print(f"    ROMI: {camp['romi']:.0f}% | CPL: {camp['cpl']:.0f}₽ | Revenue: {camp['revenue']:,.0f}₽")
    
    # Print alerts
    print("\n" + bot.get_alerts_text())
    
    # Print period comparison
    print("\n" + bot.get_comparison_text("week"))
    
    # Print expert comments
    print("\n🧠 Expert comments:")
    for comment in bot.get_expert_comments()[:5]:
        print(f"  • {comment}")
    
    # Generate reports
    print("\n📊 Generating reports...")
    
    # Graph 1
    bot.generate_graph1(save_file=True)
    print("  ✅ Graph 1 saved to ./output/graph1_cross_analytics.png")
    
    # Graph 2 for first campaign
    first_campaign = period.campaigns[0]
    bot.generate_graph2(first_campaign.id, save_file=True)
    print(f"  ✅ Graph 2 saved to ./output/graph2_campaign_{first_campaign.id}.png")
    
    print("\n" + "=" * 60)
    print("Done! Check ./output directory for generated PNGs.")
    print("=" * 60)
