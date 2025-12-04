"""
Chart Utilities

Common styling and helper functions for chart generation.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from datetime import date
from io import BytesIO

from .models import SocialNetwork


# Color schemes
COLORS = {
    # Main palette
    "primary": "#2196F3",
    "secondary": "#FF9800",
    "success": "#4CAF50",
    "warning": "#FFC107",
    "danger": "#F44336",
    "info": "#00BCD4",
    
    # Chart colors (for multiple series)
    "series": [
        "#2196F3",  # Blue
        "#FF9800",  # Orange
        "#4CAF50",  # Green
        "#9C27B0",  # Purple
        "#F44336",  # Red
        "#00BCD4",  # Cyan
        "#FFEB3B",  # Yellow
        "#795548",  # Brown
        "#607D8B",  # Blue Grey
        "#E91E63",  # Pink
        "#3F51B5",  # Indigo
        "#009688",  # Teal
    ],
    
    # Social network colors
    "instagram": "#E4405F",
    "telegram": "#0088CC",
    "youtube": "#FF0000",
    "vk": "#4C75A3",
    "facebook": "#1877F2",
    "tiktok": "#000000",
    "twitter": "#1DA1F2",
    
    # Background colors
    "bg_light": "#FAFAFA",
    "bg_dark": "#212121",
    "grid": "#E0E0E0",
    
    # KPI lines
    "kpi_positive": "#4CAF50",
    "kpi_negative": "#F44336",
    
    # Heatmap colors
    "heatmap_low": "#BBDEFB",
    "heatmap_mid": "#64B5F6",
    "heatmap_high": "#1565C0",
}

# Social network color mapping
SOCIAL_NETWORK_COLORS = {
    SocialNetwork.INSTAGRAM: COLORS["instagram"],
    SocialNetwork.TELEGRAM: COLORS["telegram"],
    SocialNetwork.YOUTUBE: COLORS["youtube"],
    SocialNetwork.VK: COLORS["vk"],
    SocialNetwork.FACEBOOK: COLORS["facebook"],
    SocialNetwork.TIKTOK: COLORS["tiktok"],
    SocialNetwork.TWITTER: COLORS["twitter"],
    SocialNetwork.OTHER: COLORS["series"][7],
}


def setup_style():
    """Setup matplotlib style for all charts"""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': 10,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.facecolor': COLORS["bg_light"],
        'figure.facecolor': 'white',
        'axes.edgecolor': COLORS["grid"],
        'axes.linewidth': 1,
    })


def format_currency(value: float, currency: str = "₽") -> str:
    """Format value as currency"""
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M {currency}"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K {currency}"
    else:
        return f"{value:.0f} {currency}"


def format_number(value: float) -> str:
    """Format number with K/M suffixes"""
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return f"{value:.0f}"


def format_percent(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.1f}%"


def currency_formatter(x: float, pos: int) -> str:
    """Formatter for currency axis"""
    return format_currency(x)


def percent_formatter(x: float, pos: int) -> str:
    """Formatter for percentage axis"""
    return f"{x:.0f}%"


def create_figure(
    nrows: int = 1,
    ncols: int = 1,
    figsize: Tuple[int, int] = (14, 10),
    dpi: int = 150
) -> Tuple[Figure, Any]:
    """Create a new figure with subplots"""
    setup_style()
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, dpi=dpi)
    fig.set_facecolor('white')
    return fig, axes


def add_title_box(
    ax: Axes,
    title: str,
    subtitle: Optional[str] = None,
    fontsize: int = 16
):
    """Add a styled title box to the axes"""
    ax.set_title(title, fontsize=fontsize, fontweight='bold', pad=20)
    if subtitle:
        ax.text(
            0.5, 1.02, subtitle,
            transform=ax.transAxes,
            ha='center', va='bottom',
            fontsize=fontsize - 4,
            color='gray'
        )


def create_header_box(
    ax: Axes,
    title: str,
    campaign_id: str,
    metrics: Dict[str, str]
) -> None:
    """
    Create a header box with campaign summary metrics.
    
    Format:
    +==========================================================================+
    |                              ИТОГИ КАМПАНИИ                              |
    +==========================================================================+
    | Выручка:         5.9M ₽        |  ROMI:         155%                     |
    ...
    """
    ax.axis('off')
    
    # Title
    ax.text(
        0.5, 0.95, title,
        transform=ax.transAxes,
        ha='center', va='top',
        fontsize=18, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=COLORS["primary"], 
                  edgecolor='none', alpha=0.9),
        color='white'
    )
    
    ax.text(
        0.5, 0.85, f"ID: {campaign_id}",
        transform=ax.transAxes,
        ha='center', va='top',
        fontsize=10, color='gray'
    )
    
    # Metrics in two columns
    left_metrics = list(metrics.items())[:len(metrics)//2 + len(metrics)%2]
    right_metrics = list(metrics.items())[len(metrics)//2 + len(metrics)%2:]
    
    y_pos = 0.75
    for (lkey, lval), (rkey, rval) in zip(left_metrics, right_metrics):
        ax.text(
            0.15, y_pos, f"{lkey}:",
            transform=ax.transAxes, ha='left', va='top',
            fontsize=11, fontweight='bold'
        )
        ax.text(
            0.35, y_pos, lval,
            transform=ax.transAxes, ha='left', va='top',
            fontsize=11
        )
        ax.text(
            0.55, y_pos, f"{rkey}:",
            transform=ax.transAxes, ha='left', va='top',
            fontsize=11, fontweight='bold'
        )
        ax.text(
            0.75, y_pos, rval,
            transform=ax.transAxes, ha='left', va='top',
            fontsize=11
        )
        y_pos -= 0.12


def plot_timeline_with_bars(
    ax: Axes,
    dates: List[date],
    bar_values: List[float],
    line_data: Dict[str, List[float]],
    title: str,
    ylabel_bar: str = "Продажи",
    ylabel_line: str = "Выручка",
    line_alpha: float = 0.6,
    show_legend: bool = True,
    visible_series: Optional[List[str]] = None
) -> Axes:
    """
    Plot timeline with bars (total sales) and semi-transparent lines (by series).
    
    Args:
        ax: Matplotlib axes
        dates: List of dates
        bar_values: Values for background bars (e.g., total sales)
        line_data: Dict of series_name -> values for lines
        title: Chart title
        ylabel_bar: Label for bar y-axis
        ylabel_line: Label for line y-axis
        line_alpha: Alpha for line plots
        show_legend: Whether to show legend
        visible_series: Optional list of series to show (for toggle feature)
    """
    x = np.arange(len(dates))
    
    # Plot bars in background
    ax.bar(x, bar_values, alpha=0.3, color=COLORS["primary"], label=ylabel_bar, zorder=1)
    
    # Create secondary y-axis for lines
    ax2 = ax.twinx()
    
    # Plot lines
    colors = COLORS["series"]
    for i, (name, values) in enumerate(line_data.items()):
        if visible_series is not None and name not in visible_series:
            continue
        
        # Handle series that start mid-period (None values at start)
        valid_mask = [v is not None and not np.isnan(v) if isinstance(v, (int, float)) else v is not None for v in values]
        valid_x = [xi for xi, m in zip(x, valid_mask) if m]
        valid_values = [v for v, m in zip(values, valid_mask) if m]
        
        if valid_values:
            ax2.plot(
                valid_x, valid_values,
                linewidth=2,
                alpha=line_alpha,
                color=colors[i % len(colors)],
                label=name,
                marker='o',
                markersize=3,
                zorder=2
            )
            
            # Fill area under line
            ax2.fill_between(
                valid_x, 0, valid_values,
                alpha=0.1,
                color=colors[i % len(colors)]
            )
    
    # Format x-axis
    ax.set_xticks(x[::max(1, len(x)//10)])
    ax.set_xticklabels([d.strftime('%d.%m') for d in dates][::max(1, len(x)//10)], rotation=45)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel(ylabel_bar, fontsize=10)
    ax2.set_ylabel(ylabel_line, fontsize=10)
    
    # Format y-axis
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format_number(x)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format_currency(x)))
    
    if show_legend:
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)
    
    return ax2


def plot_pie_chart(
    ax: Axes,
    values: List[float],
    labels: List[str],
    title: str,
    colors: Optional[List[str]] = None,
    show_values: bool = True,
    currency: bool = False
) -> None:
    """
    Plot a pie chart with labels and percentages.
    """
    if not values or sum(values) == 0:
        ax.text(0.5, 0.5, "Нет данных", ha='center', va='center')
        ax.set_title(title)
        ax.axis('off')
        return
    
    if colors is None:
        colors = COLORS["series"][:len(values)]
    
    # Calculate percentages
    total = sum(values)
    
    def make_autopct(values):
        def autopct(pct):
            val = pct / 100 * total
            if currency:
                return f'{pct:.1f}%\n({format_currency(val)})'
            else:
                return f'{pct:.1f}%\n({format_number(val)})'
        return autopct
    
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=make_autopct(values) if show_values else '%1.1f%%',
        startangle=90,
        explode=[0.02] * len(values),
        shadow=False,
        textprops={'fontsize': 8}
    )
    
    # Style the percentage text
    for autotext in autotexts:
        autotext.set_fontsize(7)
        autotext.set_fontweight('bold')
    
    ax.set_title(title, fontsize=12, fontweight='bold')


def plot_horizontal_bar_chart(
    ax: Axes,
    values: List[float],
    labels: List[str],
    title: str,
    xlabel: str = "",
    colors: Optional[List[str]] = None,
    kpi_positive: Optional[float] = None,
    kpi_negative: Optional[float] = None,
    show_values: bool = True,
    value_format: str = "number"  # "number", "currency", "percent"
) -> None:
    """
    Plot horizontal bar chart with optional KPI lines.
    """
    if not values:
        ax.text(0.5, 0.5, "Нет данных", ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title)
        return
    
    y_pos = np.arange(len(labels))
    
    if colors is None:
        colors = [COLORS["primary"]] * len(values)
    elif isinstance(colors, str):
        colors = [colors] * len(values)
    
    bars = ax.barh(y_pos, values, color=colors, alpha=0.8, height=0.6)
    
    # Add KPI lines
    if kpi_positive is not None:
        ax.axvline(x=kpi_positive, color=COLORS["kpi_positive"], 
                   linestyle='--', linewidth=2, label=f'KPI+ ({kpi_positive:.0f})')
    
    if kpi_negative is not None:
        ax.axvline(x=kpi_negative, color=COLORS["kpi_negative"], 
                   linestyle='--', linewidth=2, label=f'KPI- ({kpi_negative:.0f})')
    
    # Add value labels on bars
    if show_values:
        for bar, val in zip(bars, values):
            if value_format == "currency":
                text = format_currency(val)
            elif value_format == "percent":
                text = format_percent(val)
            else:
                text = format_number(val)
            
            ax.text(
                bar.get_width() + max(values) * 0.02, bar.get_y() + bar.get_height() / 2,
                text, va='center', fontsize=9
            )
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel(xlabel)
    
    if kpi_positive is not None or kpi_negative is not None:
        ax.legend(loc='lower right', fontsize=8)
    
    ax.invert_yaxis()


def plot_vertical_bar_comparison(
    ax: Axes,
    labels: List[str],
    values1: List[float],
    values2: List[float],
    legend1: str = "ROMI",
    legend2: str = "Расход",
    title: str = "",
    kpi_positive: Optional[float] = None,
    kpi_negative: Optional[float] = None
) -> None:
    """
    Plot vertical bar chart with two series (e.g., ROMI and Spend).
    """
    x = np.arange(len(labels))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, values1, width, label=legend1, color=COLORS["primary"], alpha=0.8)
    
    # Create secondary axis for second series
    ax2 = ax.twinx()
    bars2 = ax2.bar(x + width/2, values2, width, label=legend2, color=COLORS["secondary"], alpha=0.8)
    
    # Add KPI lines for first axis
    if kpi_positive is not None:
        ax.axhline(y=kpi_positive, color=COLORS["kpi_positive"], 
                   linestyle='--', linewidth=2, alpha=0.7)
    if kpi_negative is not None:
        ax.axhline(y=kpi_negative, color=COLORS["kpi_negative"], 
                   linestyle='--', linewidth=2, alpha=0.7)
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylabel(legend1)
    ax2.set_ylabel(legend2)
    ax.set_title(title, fontsize=12, fontweight='bold')
    
    # Combined legend
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=8)
    
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format_currency(x)))


def plot_heatmap(
    ax: Axes,
    data: np.ndarray,
    row_labels: List[str],
    col_labels: List[str],
    title: str,
    fmt: str = ".0f",
    cmap: str = "Blues"
) -> None:
    """
    Plot a heatmap (e.g., for weekly sales pattern).
    """
    im = ax.imshow(data, cmap=cmap, aspect='auto')
    
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)
    
    # Rotate tick labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    
    # Add text annotations
    for i in range(len(row_labels)):
        for j in range(len(col_labels)):
            val = data[i, j]
            color = 'white' if val > data.max() * 0.6 else 'black'
            ax.text(j, i, format(val, fmt), ha='center', va='center', color=color, fontsize=8)
    
    ax.set_title(title, fontsize=12, fontweight='bold')
    
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax, shrink=0.8)


def plot_dynamic_comparison(
    ax: Axes,
    dates: List[date],
    series_data: Dict[str, List[float]],
    title: str,
    ylabel: str = "",
    average_value: Optional[float] = None,
    kpi_positive: Optional[float] = None,
    kpi_negative: Optional[float] = None,
    visible_series: Optional[List[str]] = None
) -> None:
    """
    Plot dynamic comparison chart with toggle capability.
    Shows multiple series over time with average line and KPI markers.
    """
    x = np.arange(len(dates))
    colors = COLORS["series"]
    
    for i, (name, values) in enumerate(series_data.items()):
        if visible_series is not None and name not in visible_series:
            continue
        
        valid_mask = [v is not None for v in values]
        valid_x = [xi for xi, m in zip(x, valid_mask) if m]
        valid_values = [v for v, m in zip(values, valid_mask) if m]
        
        if valid_values:
            ax.plot(
                valid_x, valid_values,
                linewidth=2, alpha=0.7,
                color=colors[i % len(colors)],
                label=name, marker='o', markersize=4
            )
    
    # Average line
    if average_value is not None:
        ax.axhline(y=average_value, color='gray', linestyle='-', 
                   linewidth=2, alpha=0.5, label=f'Среднее ({average_value:.1f})')
    
    # KPI lines
    if kpi_positive is not None:
        ax.axhline(y=kpi_positive, color=COLORS["kpi_positive"],
                   linestyle='--', linewidth=2, alpha=0.7, label=f'KPI+ ({kpi_positive:.0f})')
    
    if kpi_negative is not None:
        ax.axhline(y=kpi_negative, color=COLORS["kpi_negative"],
                   linestyle='--', linewidth=2, alpha=0.7, label=f'KPI- ({kpi_negative:.0f})')
    
    ax.set_xticks(x[::max(1, len(x)//10)])
    ax.set_xticklabels([d.strftime('%d.%m') for d in dates][::max(1, len(x)//10)], rotation=45)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=8, ncol=2)


def plot_funnel_comparison(
    ax: Axes,
    sources: List[str],
    cpc_values: List[float],
    cpl_values: List[float],
    cac_values: List[float],
    title: str = "Соответствие CPA → CPL → CAC по источникам"
) -> None:
    """
    Plot funnel comparison chart showing CPA vs CPL vs CAC relationships.
    Helps identify funnel issues.
    """
    x = np.arange(len(sources))
    width = 0.25
    
    bars1 = ax.bar(x - width, cpc_values, width, label='CPC (за клик)', 
                   color=COLORS["info"], alpha=0.8)
    bars2 = ax.bar(x, cpl_values, width, label='CPL (за лид)', 
                   color=COLORS["warning"], alpha=0.8)
    bars3 = ax.bar(x + width, cac_values, width, label='CAC (за клиента)', 
                   color=COLORS["danger"], alpha=0.8)
    
    ax.set_xticks(x)
    ax.set_xticklabels(sources, rotation=45, ha='right')
    ax.set_ylabel('Стоимость, ₽')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)
    
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format_currency(x)))


def plot_cr_funnel_comparison(
    ax: Axes,
    sources: List[str],
    cr_cl_values: List[float],
    cr_ls_values: List[float],
    cr_cs_values: List[float],
    title: str = "Конверсии воронки CR(C→L) → CR(L→S) → CR(C→S)"
) -> None:
    """
    Plot conversion rate comparison for funnel analysis.
    """
    x = np.arange(len(sources))
    width = 0.25
    
    bars1 = ax.bar(x - width, cr_cl_values, width, label='CR(C→L)', 
                   color=COLORS["success"], alpha=0.8)
    bars2 = ax.bar(x, cr_ls_values, width, label='CR(L→S)', 
                   color=COLORS["warning"], alpha=0.8)
    bars3 = ax.bar(x + width, cr_cs_values, width, label='CR(C→S)', 
                   color=COLORS["primary"], alpha=0.8)
    
    ax.set_xticks(x)
    ax.set_xticklabels(sources, rotation=45, ha='right')
    ax.set_ylabel('Конверсия, %')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)


def add_alert_box(
    ax: Axes,
    alerts_text: str,
    comparison_text: str
) -> None:
    """
    Add alert and comparison box below a chart.
    """
    ax.axis('off')
    
    # Alert section
    ax.text(
        0.02, 0.95, alerts_text,
        transform=ax.transAxes,
        ha='left', va='top',
        fontsize=9,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF3E0', 
                  edgecolor='#FF9800', alpha=0.9),
        family='monospace'
    )
    
    # Comparison section
    ax.text(
        0.52, 0.95, comparison_text,
        transform=ax.transAxes,
        ha='left', va='top',
        fontsize=9,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#E3F2FD', 
                  edgecolor='#2196F3', alpha=0.9),
        family='monospace'
    )


def create_legend_toggles(
    ax: Axes,
    series_names: List[str],
    colors: List[str],
    visible: List[bool]
) -> None:
    """
    Create visual toggle indicators for series visibility.
    """
    ax.axis('off')
    
    n_cols = min(4, len(series_names))
    n_rows = (len(series_names) + n_cols - 1) // n_cols
    
    for i, (name, color, is_visible) in enumerate(zip(series_names, colors, visible)):
        row = i // n_cols
        col = i % n_cols
        
        x = 0.05 + col * 0.24
        y = 0.9 - row * 0.3
        
        # Toggle indicator
        indicator = "●" if is_visible else "○"
        alpha = 1.0 if is_visible else 0.4
        
        ax.text(
            x, y, indicator,
            transform=ax.transAxes,
            ha='left', va='center',
            fontsize=14, color=color, alpha=alpha
        )
        ax.text(
            x + 0.03, y, name[:20],
            transform=ax.transAxes,
            ha='left', va='center',
            fontsize=9, alpha=alpha
        )


def save_figure(fig: Figure, filename: str, dpi: int = 150) -> str:
    """Save figure to file and return path"""
    fig.tight_layout()
    fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close(fig)
    return filename


def figure_to_bytes(fig: Figure, dpi: int = 150) -> bytes:
    """Convert figure to bytes for bot sending"""
    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()
