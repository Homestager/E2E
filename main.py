#!/usr/bin/env python3
"""
Marketing Analytics Report Generator

Main entry point for generating PNG reports for Telegram bot.

Usage:
    python main.py                     # Generate demo reports
    python main.py --graph1            # Generate only Graph 1
    python main.py --graph2 1234       # Generate Graph 2 for campaign 1234
    python main.py --output ./reports  # Custom output directory
"""

import argparse
import os
import sys
from datetime import date, timedelta

from analytics import (
    AnalyticsPeriod,
    Campaign,
    SampleDataGenerator,
    CrossAnalyticsReport,
    CampaignAnalyticsReport,
)
from analytics.bot_integration import MarketingAnalyticsBot
from analytics.data_generator import create_demo_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate marketing analytics PNG reports for Telegram bot"
    )
    
    parser.add_argument(
        "--graph1", "-1",
        action="store_true",
        help="Generate Graph 1 (Cross Analytics)"
    )
    
    parser.add_argument(
        "--graph2", "-2",
        type=str,
        default=None,
        help="Generate Graph 2 for specific campaign ID"
    )
    
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Generate all reports (Graph 1 + Graph 2 for each campaign)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./output",
        help="Output directory for PNG files"
    )
    
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=30,
        help="Number of days for sample data"
    )
    
    parser.add_argument(
        "--campaigns", "-c",
        type=int,
        default=3,
        help="Number of campaigns for sample data"
    )
    
    parser.add_argument(
        "--sources", "-s",
        type=int,
        default=5,
        help="Number of sources per campaign for sample data"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible data generation"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use demo data (quick test)"
    )
    
    parser.add_argument(
        "--list-campaigns",
        action="store_true",
        help="List available campaigns"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary text for bot"
    )
    
    parser.add_argument(
        "--alerts",
        action="store_true",
        help="Print current alerts"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Generate or load data
    print("🔄 Generating sample data...")
    
    if args.demo:
        period = create_demo_data()
    else:
        generator = SampleDataGenerator(seed=args.seed)
        period = generator.generate_analytics_period(
            num_days=args.days,
            num_campaigns=args.campaigns,
            sources_per_campaign=args.sources
        )
    
    print(f"✅ Generated {len(period.campaigns)} campaigns with data from "
          f"{period.start_date} to {period.end_date}")
    
    # Initialize bot integration
    bot = MarketingAnalyticsBot(period, output_dir=args.output)
    
    # Handle different modes
    if args.list_campaigns:
        print("\n📋 Available campaigns:")
        for campaign in period.campaigns:
            print(f"  • {campaign.name} (ID: {campaign.id}) - "
                  f"ROMI: {campaign.overall_romi:.0f}%")
        return
    
    if args.summary:
        print("\n" + bot.get_cross_analytics_summary())
        return
    
    if args.alerts:
        print("\n" + bot.get_alerts_text())
        print("\n" + bot.get_comparison_text("week"))
        print("\n" + bot.get_comparison_text("month"))
        return
    
    # Generate reports
    generated = []
    
    if args.graph1 or args.all or (not args.graph1 and not args.graph2):
        print("\n📊 Generating Graph 1 (Cross Analytics)...")
        try:
            bot.generate_graph1(save_file=True)
            output_path = os.path.join(args.output, "graph1_cross_analytics.png")
            generated.append(("Graph 1 - Cross Analytics", output_path))
            print(f"  ✅ Saved to: {output_path}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    if args.graph2:
        campaign_id = args.graph2
        print(f"\n📊 Generating Graph 2 for campaign {campaign_id}...")
        try:
            result = bot.generate_graph2(campaign_id, save_file=True)
            if result:
                output_path = os.path.join(args.output, f"graph2_campaign_{campaign_id}.png")
                generated.append((f"Graph 2 - Campaign {campaign_id}", output_path))
                print(f"  ✅ Saved to: {output_path}")
            else:
                print(f"  ❌ Campaign {campaign_id} not found")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    if args.all:
        for campaign in period.campaigns:
            print(f"\n📊 Generating Graph 2 for campaign {campaign.name} ({campaign.id})...")
            try:
                bot.generate_graph2(campaign.id, save_file=True)
                output_path = os.path.join(args.output, f"graph2_campaign_{campaign.id}.png")
                generated.append((f"Graph 2 - {campaign.name}", output_path))
                print(f"  ✅ Saved to: {output_path}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    # Summary
    if generated:
        print(f"\n{'='*60}")
        print(f"✅ Generated {len(generated)} report(s):")
        for name, path in generated:
            size = os.path.getsize(path) / 1024
            print(f"  • {name}: {path} ({size:.1f} KB)")
        print(f"{'='*60}")
    else:
        print("\n⚠️ No reports generated. Use --help for usage.")


if __name__ == "__main__":
    main()
