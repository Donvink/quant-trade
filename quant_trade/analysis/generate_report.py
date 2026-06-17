#!/usr/bin/env python3
"""Generate backtest report with equity curve (vs SPY), monthly returns, and summary stats."""

import sys
from pathlib import Path

def setup_path():
    scripts_dir = Path(__file__).parent.parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

setup_path()

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import yfinance as yf

from analysis.backtest import backtest
from core.stock_pool import get_sp500_symbols
from core.config import LOG_DIR, PROJECT_ROOT

ASSETS_DIR = PROJECT_ROOT / "assets"
ASSETS_DIR.mkdir(exist_ok=True)


def calculate_monthly_returns(nav_series):
    monthly = nav_series.resample('ME').last()
    return monthly.pct_change().dropna() * 100


def calculate_drawdown(nav_series):
    running_max = nav_series.expanding().max()
    return (nav_series - running_max) / running_max * 100


def plot_equity_curve(nav_series, spy_series, drawdown_series, start_date, end_date):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                    gridspec_kw={'height_ratios': [3, 1]})

    # — Equity curve —
    ax1.plot(nav_series.index, nav_series.values, label='Strategy', color='#1f77b4', linewidth=1.5)
    if spy_series is not None:
        ax1.plot(spy_series.index, spy_series.values, label='SPY (buy & hold)',
                 color='#ff7f0e', linewidth=1.5, linestyle='--', alpha=0.8)
    ax1.axhline(y=100_000, color='gray', linestyle=':', alpha=0.5, label='Initial Capital')
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e3:.0f}K'))
    ax1.set_ylabel('Portfolio Value')
    ax1.set_title(f'Equity Curve vs SPY  ({start_date} → {end_date})', fontsize=13)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # — Drawdown —
    ax2.fill_between(drawdown_series.index, drawdown_series.values, 0, color='red', alpha=0.25)
    ax2.plot(drawdown_series.index, drawdown_series.values, color='red', linewidth=0.8)
    ax2.set_ylabel('Drawdown (%)')
    ax2.set_xlabel('Date')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    out = ASSETS_DIR / 'equity_curve.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")


def plot_monthly_returns(monthly_returns):
    fig, ax = plt.subplots(figsize=(14, 5))
    colors = ['#2ca02c' if x > 0 else '#d62728' for x in monthly_returns.values]
    ax.bar(monthly_returns.index.strftime('%Y-%m'), monthly_returns.values, color=colors, width=0.7)
    ax.axhline(y=0, color='black', linewidth=0.8)
    ax.set_ylabel('Monthly Return (%)')
    ax.set_title('Monthly Returns', fontsize=13)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    out = ASSETS_DIR / 'monthly_returns.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', default='2024-04-01')
    parser.add_argument('--end',   default='2026-03-31')
    parser.add_argument('--capital', type=float, default=100_000)
    args = parser.parse_args()

    start_date = args.start
    end_date   = args.end
    initial_capital = args.capital

    print("Running backtest…")
    symbols = get_sp500_symbols()
    trades_df, final_value, daily_nav = backtest(
        stock_pool=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        return_daily_nav=True,
    )

    # Build NAV series on business-day index
    bdays = pd.bdate_range(start=start_date, end=end_date)
    nav_len = min(len(daily_nav), len(bdays))
    nav_series = pd.Series(daily_nav[:nav_len], index=bdays[:nav_len])

    # Download SPY and normalise to same initial capital
    print("Downloading SPY…")
    spy_raw = yf.download('SPY', start=start_date, end=end_date,
                          auto_adjust=True, progress=False)['Close'].squeeze()
    spy_series = spy_raw / spy_raw.iloc[0] * initial_capital
    spy_series = spy_series.reindex(nav_series.index, method='ffill')

    drawdown_series = calculate_drawdown(nav_series)
    monthly_returns = calculate_monthly_returns(nav_series)

    # ── Summary ────────────────────────────────────────────────────────────────
    total_return   = (final_value - initial_capital) / initial_capital * 100
    daily_ret      = nav_series.pct_change().dropna()
    sharpe         = daily_ret.mean() / daily_ret.std() * (252 ** 0.5) if daily_ret.std() else 0
    max_dd         = drawdown_series.min()
    n_years        = len(nav_series) / 252
    cagr           = ((final_value / initial_capital) ** (1 / n_years) - 1) * 100

    spy_final      = spy_series.iloc[-1]
    spy_return     = (spy_final - initial_capital) / initial_capital * 100

    print("\n" + "=" * 60)
    print("BACKTEST REPORT")
    print("=" * 60)
    print(f"Period          : {start_date} → {end_date}")
    print(f"Initial Capital : ${initial_capital:,.0f}")
    print(f"Final Value     : ${final_value:,.0f}")
    print(f"Total Return    : {total_return:.2f}%  (SPY: {spy_return:.2f}%)")
    print(f"CAGR            : {cagr:.2f}%")
    print(f"Sharpe Ratio    : {sharpe:.2f}")
    print(f"Max Drawdown    : {max_dd:.2f}%")
    if not trades_df.empty:
        win_rate = (trades_df['pnl_pct'] > 0).mean() * 100
        avg_win  = trades_df[trades_df['pnl_pct'] > 0]['pnl_pct'].mean()
        avg_loss = trades_df[trades_df['pnl_pct'] < 0]['pnl_pct'].mean()
        print(f"Win Rate        : {win_rate:.2f}%")
        print(f"Avg Win         : +{avg_win:.2f}%")
        print(f"Avg Loss        : {avg_loss:.2f}%")
        print(f"Trades          : {len(trades_df)}")
    print("=" * 60)

    # ── Charts ─────────────────────────────────────────────────────────────────
    plot_equity_curve(nav_series, spy_series, drawdown_series, start_date, end_date)
    plot_monthly_returns(monthly_returns)

    # Save trades
    trades_out = ASSETS_DIR / 'trades.csv'
    trades_df.to_csv(trades_out, index=False)
    print(f"Saved: {trades_out}")


if __name__ == "__main__":
    main()
