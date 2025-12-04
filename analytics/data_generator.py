"""
Sample Data Generator

Generates realistic test data for marketing analytics.
Used for testing and demonstration purposes.
"""

import random
from datetime import date, timedelta
from typing import List, Optional

from .models import (
    Campaign,
    Source,
    SocialNetwork,
    DailyMetrics,
    AnalyticsPeriod,
    KPISettings,
)


class SampleDataGenerator:
    """
    Generates realistic sample data for marketing analytics testing.
    """
    
    # Sample campaign names
    CAMPAIGN_NAMES = [
        "BLACKFRIDAY_2025",
        "NEWYEAR_2025",
        "SUMMER_SALE",
        "AUTUMN_PROMO",
        "SPRING_LAUNCH",
        "WEBINAR_LEAD",
        "PRODUCT_LAUNCH",
        "BRAND_AWARENESS",
        "RETARGETING_Q4",
        "INFLUENCER_COLLAB",
    ]
    
    # Sample source names by social network
    SOURCE_NAMES = {
        SocialNetwork.INSTAGRAM: [
            "petrova", "blog_main", "reels_viral", "stories_promo",
            "influencer_1", "influencer_2", "direct_ads", "feed_carousel"
        ],
        SocialNetwork.TELEGRAM: [
            "channel_main", "channel_news", "ads_post", "blog_author",
            "tg_ads", "community_post", "forward_viral"
        ],
        SocialNetwork.YOUTUBE: [
            "blogger_review", "preroll_ads", "channel_integration",
            "shorts_promo", "main_video", "collab_channel"
        ],
        SocialNetwork.VK: [
            "group_main", "target_ads", "community_post", "clips_viral",
            "market_promo"
        ],
        SocialNetwork.FACEBOOK: [
            "page_main", "fb_ads", "marketplace", "group_post"
        ],
        SocialNetwork.TIKTOK: [
            "viral_dance", "product_demo", "influencer_tt", "branded_effect"
        ],
    }
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize generator with optional seed for reproducibility.
        """
        if seed is not None:
            random.seed(seed)
    
    def generate_daily_metrics(
        self,
        start_date: date,
        num_days: int,
        base_clicks: int = 100,
        click_variance: float = 0.3,
        cr_cl: float = 0.10,  # Click to Lead conversion rate
        cr_ls: float = 0.15,  # Lead to Sale conversion rate
        avg_revenue_per_sale: float = 10000,
        cpc: float = 30,  # Cost per click
        seasonality: bool = True,
        launch_spike_day: Optional[int] = None,
        decline_after_day: Optional[int] = None
    ) -> List[DailyMetrics]:
        """
        Generate realistic daily metrics for a source.
        
        Args:
            start_date: Start date for metrics
            num_days: Number of days to generate
            base_clicks: Average daily clicks
            click_variance: Variance in clicks (0-1)
            cr_cl: Conversion rate from click to lead
            cr_ls: Conversion rate from lead to sale
            avg_revenue_per_sale: Average revenue per sale
            cpc: Cost per click
            seasonality: Apply day-of-week seasonality
            launch_spike_day: Day number for launch spike
            decline_after_day: Day number after which performance declines
        """
        metrics = []
        
        for day_num in range(num_days):
            current_date = start_date + timedelta(days=day_num)
            
            # Base clicks with variance
            clicks = int(base_clicks * (1 + random.uniform(-click_variance, click_variance)))
            
            # Apply seasonality (weekends have lower traffic)
            if seasonality:
                day_of_week = current_date.weekday()
                if day_of_week == 5:  # Saturday
                    clicks = int(clicks * 0.7)
                elif day_of_week == 6:  # Sunday
                    clicks = int(clicks * 0.6)
                elif day_of_week == 0:  # Monday
                    clicks = int(clicks * 1.1)
            
            # Apply launch spike
            if launch_spike_day is not None and day_num == launch_spike_day:
                clicks = int(clicks * 3)
            elif launch_spike_day is not None and launch_spike_day < day_num < launch_spike_day + 3:
                clicks = int(clicks * 2)
            
            # Apply decline
            if decline_after_day is not None and day_num > decline_after_day:
                decline_factor = 0.95 ** (day_num - decline_after_day)
                clicks = int(clicks * decline_factor)
            
            # Ensure minimum clicks
            clicks = max(1, clicks)
            
            # Calculate leads and sales with variance
            actual_cr_cl = cr_cl * (1 + random.uniform(-0.2, 0.2))
            actual_cr_ls = cr_ls * (1 + random.uniform(-0.2, 0.2))
            
            leads = max(0, int(clicks * actual_cr_cl + random.gauss(0, 1)))
            sales = max(0, int(leads * actual_cr_ls + random.gauss(0, 0.5)))
            
            # Calculate revenue
            revenue = sales * avg_revenue_per_sale * (1 + random.uniform(-0.1, 0.2))
            
            # Calculate spend
            actual_cpc = cpc * (1 + random.uniform(-0.1, 0.1))
            spend = clicks * actual_cpc
            
            # Random refunds (2% of sales)
            refunds = random.randint(0, max(1, sales // 10))
            refund_amount = refunds * avg_revenue_per_sale * 0.8
            
            metrics.append(DailyMetrics(
                date=current_date,
                clicks=clicks,
                leads=leads,
                sales=sales,
                revenue=revenue,
                spend=spend,
                refunds=refunds,
                refund_amount=refund_amount
            ))
        
        return metrics
    
    def generate_source(
        self,
        campaign_id: str,
        social_network: SocialNetwork,
        start_date: date,
        num_days: int,
        performance_tier: str = "average",  # "top", "average", "poor"
        ad_start_delay: int = 0
    ) -> Source:
        """
        Generate a source with realistic metrics.
        
        Args:
            campaign_id: Parent campaign ID
            social_network: Social network type
            start_date: Start date
            num_days: Number of days
            performance_tier: Performance tier
            ad_start_delay: Days delay before advertising starts
        """
        # Select name
        names = self.SOURCE_NAMES.get(social_network, ["source"])
        name = random.choice(names)
        
        # Set parameters based on tier
        if performance_tier == "top":
            base_clicks = random.randint(150, 300)
            cr_cl = random.uniform(0.12, 0.18)
            cr_ls = random.uniform(0.20, 0.35)
            cpc = random.uniform(20, 40)
            avg_revenue = random.uniform(12000, 25000)
        elif performance_tier == "poor":
            base_clicks = random.randint(30, 80)
            cr_cl = random.uniform(0.03, 0.08)
            cr_ls = random.uniform(0.05, 0.12)
            cpc = random.uniform(40, 80)
            avg_revenue = random.uniform(5000, 10000)
        else:  # average
            base_clicks = random.randint(80, 150)
            cr_cl = random.uniform(0.08, 0.12)
            cr_ls = random.uniform(0.12, 0.20)
            cpc = random.uniform(25, 50)
            avg_revenue = random.uniform(8000, 15000)
        
        # Generate metrics starting from ad_start_delay
        actual_start = start_date + timedelta(days=ad_start_delay)
        actual_days = max(1, num_days - ad_start_delay)
        
        # Random launch spike and decline
        launch_spike = random.randint(0, 3) if random.random() > 0.5 else None
        decline = random.randint(int(actual_days * 0.6), int(actual_days * 0.9)) if random.random() > 0.7 else None
        
        metrics = self.generate_daily_metrics(
            start_date=actual_start,
            num_days=actual_days,
            base_clicks=base_clicks,
            cr_cl=cr_cl,
            cr_ls=cr_ls,
            avg_revenue_per_sale=avg_revenue,
            cpc=cpc,
            launch_spike_day=launch_spike,
            decline_after_day=decline
        )
        
        return Source(
            rid=str(random.randint(100000, 999999)),
            name=name,
            campaign_id=campaign_id,
            social_network=social_network,
            created_at=start_date,
            ad_start_date=actual_start if ad_start_delay > 0 else None,
            daily_metrics=metrics,
            kpi=KPISettings(
                romi_positive=random.choice([1000, 1200, 1500]),
                romi_negative=random.choice([500, 700, 800])
            )
        )
    
    def generate_campaign(
        self,
        name: Optional[str] = None,
        start_date: Optional[date] = None,
        num_days: int = 30,
        num_sources: int = 5,
        social_networks: Optional[List[SocialNetwork]] = None
    ) -> Campaign:
        """
        Generate a complete campaign with sources.
        
        Args:
            name: Campaign name (random if not provided)
            start_date: Start date (30 days ago if not provided)
            num_days: Number of days of data
            num_sources: Number of sources to generate
            social_networks: List of social networks to use
        """
        if name is None:
            name = random.choice(self.CAMPAIGN_NAMES)
        
        if start_date is None:
            start_date = date.today() - timedelta(days=num_days)
        
        if social_networks is None:
            social_networks = list(SocialNetwork)[:6]  # Exclude OTHER
        
        campaign_id = str(random.randint(1000, 9999))
        
        # Generate sources with different performance tiers
        sources = []
        tiers = ["top"] * max(1, num_sources // 5) + \
                ["average"] * (num_sources - num_sources // 5 - num_sources // 4) + \
                ["poor"] * max(1, num_sources // 4)
        
        random.shuffle(tiers)
        
        for i in range(num_sources):
            sn = random.choice(social_networks)
            tier = tiers[i] if i < len(tiers) else "average"
            
            # Some sources start later
            delay = random.randint(0, num_days // 4) if random.random() > 0.6 else 0
            
            source = self.generate_source(
                campaign_id=campaign_id,
                social_network=sn,
                start_date=start_date,
                num_days=num_days,
                performance_tier=tier,
                ad_start_delay=delay
            )
            sources.append(source)
        
        return Campaign(
            id=campaign_id,
            name=name,
            created_at=start_date,
            sources=sources,
            kpi=KPISettings(
                romi_positive=1200,
                romi_negative=700,
                cpl_positive=300,
                cpl_negative=600
            )
        )
    
    def generate_analytics_period(
        self,
        start_date: Optional[date] = None,
        num_days: int = 30,
        num_campaigns: int = 3,
        sources_per_campaign: int = 5
    ) -> AnalyticsPeriod:
        """
        Generate a complete analytics period with multiple campaigns.
        
        Args:
            start_date: Period start date
            num_days: Number of days
            num_campaigns: Number of campaigns
            sources_per_campaign: Sources per campaign
        """
        if start_date is None:
            start_date = date.today() - timedelta(days=num_days)
        
        end_date = start_date + timedelta(days=num_days - 1)
        
        campaigns = []
        used_names = set()
        
        for _ in range(num_campaigns):
            # Get unique name
            name = random.choice(self.CAMPAIGN_NAMES)
            while name in used_names:
                name = random.choice(self.CAMPAIGN_NAMES)
            used_names.add(name)
            
            campaign = self.generate_campaign(
                name=name,
                start_date=start_date,
                num_days=num_days,
                num_sources=sources_per_campaign
            )
            campaigns.append(campaign)
        
        return AnalyticsPeriod(
            start_date=start_date,
            end_date=end_date,
            campaigns=campaigns
        )
    
    def generate_large_dataset(
        self,
        start_date: Optional[date] = None,
        num_days: int = 90,
        num_campaigns: int = 10,
        sources_per_campaign: int = 8
    ) -> AnalyticsPeriod:
        """
        Generate a large dataset for stress testing.
        """
        return self.generate_analytics_period(
            start_date=start_date,
            num_days=num_days,
            num_campaigns=num_campaigns,
            sources_per_campaign=sources_per_campaign
        )


def create_demo_data() -> AnalyticsPeriod:
    """
    Create demo data for quick testing.
    Returns an AnalyticsPeriod with 3 campaigns over 30 days.
    """
    generator = SampleDataGenerator(seed=42)  # Reproducible
    return generator.generate_analytics_period(
        num_days=30,
        num_campaigns=3,
        sources_per_campaign=5
    )
