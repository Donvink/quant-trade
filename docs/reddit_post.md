# r/algotrading Post

## Title

Open-source RPS momentum screener: 355% vs SPY 48% backtest (2024–2026) — IBKR-connected, full code shared

---

## Body

Built this over the past few months and figured it was worth sharing. It's a pure momentum system based on Relative Price Strength (RPS) — nothing exotic, but the implementation has a few details that I think make it more robust than a naive buy-the-top approach.

**Strategy overview**

Universe: large-cap US stocks (market cap > $5B), ~2,000 names.

Entry: rank every stock by 20/60/120-day RPS (percentile vs the universe). Only stocks in the top 15% on all three windows qualify. Secondary filter on volume. Equal-weight sizing, max 5 open positions, max 3 new buys per day.

Exit (in priority order):
1. Hard stop loss: -10%
2. Trailing stop from peak: -10%
3. MACD death cross (12/26/9) after minimum 3-day hold
4. Take profit: +30%
5. Time stop: 25 days

**Backtest results (2024-04-01 → 2026-06-16)**

| Metric | Strategy | SPY |
|--------|----------|-----|
| Total Return | **355.33%** | 48.08% |
| CAGR | **93.87%** | ~22% |
| Sharpe Ratio | **1.97** | ~0.9 |
| Max Drawdown | -34.23% | ~-19% |
| Win Rate | 53.07% | — |
| Avg Win | +14.53% | — |
| Avg Loss | -7.29% | — |

[Equity curve and monthly returns charts in the repo]

**Honest caveats**

- The 2024–2026 period was mostly a bull market. Momentum strategies tend to shine here and get punished hard in choppy or mean-reverting regimes.
- No slippage modeling. With max 5 positions and large-cap names, real-world impact should be minimal, but it's still not accounted for.
- Max drawdown of -34% is real — there was a brutal Q1 2025 drawdown period. This is not a low-volatility strategy.
- The first 6 months (April–September 2024) barely moved — the strategy needs momentum to exist before it does anything.

**Live trading**

The system connects to Interactive Brokers via `ib_insync`. Paper trading → live is a one-line config change. Running daily via cron after market close.

**Tech stack**

Python, yfinance for data, SQLite for local storage, pandas_ta for indicators, IBKR API for execution.

**Repo**

github.com/Donvink/quant-trade — MIT license, PRs welcome.

Happy to answer questions on the exit logic, the RPS calculation, or anything else. And yes, I know 2 years is a short backtest window — working on extending it.

---

*Not financial advice. Past performance doesn't guarantee future results. Always paper trade before going live.*
