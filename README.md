# 🦞 Quant-Trade

A quantitative trading system for US stocks based on RPS (Relative Price Strength) multi-factor selection. Supports backtesting, paper trading, and live trading with Interactive Brokers, featuring comprehensive position management and risk control.

[中文版](./README-zh.md) | [Documentation](./skills/quant-trade/SKILL.md)

## ✨ Features

- **RPS Screening**: Based on 20/60/120-day relative strength ranking
- **Multi-factor Scoring**: Combines volume and fundamentals (optional)
- **Dynamic Exit**: Stop loss, trailing stop, MACD death cross, take profit, time stop
- **Position Management**: Equal weight + max positions + daily purchase limit
- **Backtesting Engine**: Full historical backtesting with performance analytics
- **Live Trading**: Interactive Brokers API integration (paper/live)
- **Data Management**: Local SQLite database with full download and daily incremental updates

## 📊 Backtest Results (2024-04-01 to 2026-03-31)

| Metric | Strategy | SPY (Benchmark) |
|--------|----------|-----------------|
| Initial Capital | $100,000 | $100,000 |
| Final Capital | $203,900 | ~$129,000 |
| Total Return | **103.90%** | ~29% |
| Annualized Return | **41.05%** | ~14% |
| Sharpe Ratio | **1.67** | ~0.9 |
| Max Drawdown | -20.55% | ~-19% |
| Win Rate | 48.75% | — |
| Avg Profit | +10.64% | — |
| Avg Loss | -6.08% | — |

> SPY figures are approximate. Run `python -c "import yfinance as yf; spy = yf.download('SPY', '2024-04-01', '2026-03-31'); print(round((spy['Close'].iloc[-1].item()/spy['Close'].iloc[0].item()-1)*100, 2), '%')"` for exact numbers.

### Equity Curve

![Equity Curve](assets/equity_curve.png)

### Monthly Returns

![Monthly Returns](assets/monthly_returns.png)

### Trade Records

[Download Trades CSV](assets/trades.csv)

## 📁 Directory Structure

```
quant-trade/
├── README.md
├── README-zh.md
├── LICENSE
├── requirements.txt
├── assets/                       # Images
│   ├── equity_curve.png
│   └── monthly_returns.png
├── data/                         # Data storage
│   └── quant_trade/
│       ├── db/
│       │   └── market_data.db
│       ├── logs/
│       ├── cache/
│       └── backtest/
├── tests/                        # Test scripts
│   ├── test_all.py
│   ├── test_ibapi.py
│   └── test_ibsync.py
└── skills/
    └── quant-trade/
        ├── SKILL.md
        ├── SKILL-zh.md
        ├── config.yaml
        ├── config.example.yaml
        ├── hooks/
        ├── references/
        └── scripts/
            ├── main.py
            ├── core/
            │   ├── config.py
            │   ├── data_manager.py
            │   ├── stock_pool.py
            │   ├── rps_calculator.py
            │   └── factors.py
            ├── trading/
            │   ├── ibkr_client.py
            │   ├── risk_checker.py
            │   └── stop_loss_monitor.py
            ├── analysis/
            │   ├── screener.py
            │   ├── backtest.py
            │   ├── generate_report.py
            │   └── optimize.py
            └── utils/
                ├── update_fundamentals.py
                └── update_fundamentals_history.py
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
git clone https://github.com/Donvink/quant-trade.git
cd quant-trade

conda create -n quant-trade python=3.10 -y
conda activate quant-trade

pip install -r requirements.txt
```

### 2. Configuration

Edit `skills/quant-trade/config.yaml`:

```yaml
risk:
  stop_loss_pct: -10
  take_profit_pct: 30
  trailing_stop_pct: 10
  max_hold_days: 10
  min_hold_days: 3
  use_macd_sell: false

screener:
  rps_threshold: 95
  rps_periods: [20, 60, 120]
  max_buy: 3
  max_own: 5
  use_fundamentals: false

ibkr:
  host: "127.0.0.1"  # WSL2 users: use the Windows host IP (e.g. 172.29.80.1)
  port: 7497          # paper trading port; live trading uses 7496
  client_id: 1
  timeout: 30

data_source: "yfinance"
commission: 0.001
```

### 3. Download Historical Data

```bash
# From project root
python run.py --step update

# Or from the scripts directory
cd skills/quant-trade/scripts && python main.py --step update
```

### 4. Run Backtest

```bash
python run.py --step backtest
```

### 5. Paper Trading

1. Start IBKR TWS/IB Gateway and log in to paper account
2. Run trading:

```bash
# Dry run (no actual orders)
python run.py --step trade --dry-run

# Live paper trading
python run.py --step trade
```

### 6. Daily Automation

Set up cron job (runs after market close):

```bash
crontab -e
# Add the following line (runs at 04:30 Monday-Friday, after US market close)
# Replace /path/to/conda with your actual conda installation path
30 4 * * 1-5 /path/to/conda/envs/quant-trade/bin/python /path/to/quant-trade/skills/quant-trade/scripts/main.py --step all >> /path/to/quant-trade/logs/daily.log 2>&1
```

> **Note**: `conda activate` does not work in cron. Use the full path to the Python executable instead. Find it with: `conda activate quant-trade && which python`

## 📖 Command Reference

| Command | Description |
|---------|-------------|
| `python run.py --step all` | Full workflow (update + screen + trade + monitor) |
| `python run.py --step update` | Update data only |
| `python run.py --step screen` | Run screener only |
| `python run.py --step trade` | Execute trades only |
| `python run.py --step monitor` | Run stop-loss monitoring only |
| `python run.py --step backtest` | Run backtest |
| `--dry-run` | Simulation mode, no actual orders |
| `--force-refresh` | Force refresh data |

## 🔧 Position Management Logic

- **Target Position**: Target position size per stock = Net Asset Value / `max_own`
- **Daily Purchases**: Maximum `max_buy` new stocks (not currently held)
- **Capital Allocation**: Proportional allocation when cash is insufficient
- **Exit Mechanisms**: Stop loss / take profit / time stop / MACD death cross

## 📈 Backtest Report

Running backtest outputs:
- Total return, annualized return, Sharpe ratio
- Max drawdown, win rate, avg profit/loss
- Monthly returns table
- Equity curve chart
- Drawdown curve chart

## ⚠️ Important Notes

1. **Paper trading first**: Always test with paper trading before live trading
2. **Data quality**: yfinance is free but may have delays or missing data
3. **Risk control**: Past performance doesn't guarantee future results
4. **Network requirements**: Daily updates require stable internet connection

## 📚 Dependencies

- Python 3.10+
- pandas, numpy, requests, yfinance
- ib_insync (IBKR API)
- pandas_ta (technical indicators)
- matplotlib (charts)
- tqdm (progress bar)

## 🤝 Contributing

Issues and Pull Requests are welcome.

## 📄 License

MIT License

## 🎯 Roadmap

- [ ] Support A-shares / Hong Kong stocks
- [ ] Add more technical indicators
- [ ] Machine learning selection models
- [ ] Web visualization dashboard

