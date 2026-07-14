# RSI 70 Momentum Strategy - NIFTY SMALL CAP 250

## Strategy Overview

This is a momentum-based trading strategy that invests in stocks from the NIFTY SMALL CAP 250 index when they exhibit overbought conditions (RSI > 70).

### Strategy Rules

- **Entry Signal**: RSI > 70 (Overbought condition - momentum continuation)
- **Exit Signal**: RSI < 70 (Mean reversion or momentum loss)
- **Stock Universe**: NIFTY SMALL CAP 250
- **Rebalancing**: Quarterly (Every 3 months)
- **Position Sizing**: Equal weight across all active positions
- **Backtest Period**: 2025 Calendar Year (Jan 1 - Dec 31, 2025)

## Rationale

The strategy is based on the momentum continuation principle:
- When RSI crosses above 70, it indicates strong upward momentum
- Instead of mean-reverting, this strategy assumes the momentum continues
- Exit when momentum weakens (RSI drops below 70)
- Quarterly rebalancing captures new momentum plays and resets positions

## Files

1. **nifty_smallcap_250_rsi_strategy.py** - Main strategy implementation
2. **requirements.txt** - Python dependencies
3. **rsi_70_backtest_results.csv** - Output file with trade results
4. **README.md** - This file

## Installation

```bash
pip install -r requirements.txt
```

## Running the Strategy

```bash
python nifty_smallcap_250_rsi_strategy.py
```

## Output

The strategy generates:
- Console output with quarterly breakdowns
- Performance metrics (win rate, average returns, best/worst trades)
- CSV file with detailed trade-by-trade results
- List of all entries and exits with P&L

## Key Metrics

- **Total Trades**: Number of completed trades
- **Win Rate**: Percentage of profitable trades
- **Average Return**: Mean return per trade
- **Best/Worst Trade**: Maximum and minimum returns
- **Avg Win/Loss**: Average return for winning and losing trades

## Strategy Performance Expectations

- Small cap stocks can be volatile
- RSI momentum continuation can be profitable during strong trends
- Quarterly rebalancing helps capture new momentum plays
- Equal weighting diversifies risk across positions

## Notes

- Data is fetched from Yahoo Finance (NSE tickers with .NS suffix)
- RSI calculated with 14-day period (standard setting)
- Strategy assumes no slippage or transaction costs in backtest
- NIFTY SMALL CAP 250 constituents are approximately 30 stocks for this backtest

## Customization

You can modify:
- RSI threshold (currently 70)
- Number of stocks analyzed
- Rebalancing frequency
- Position sizing method
- Date range for backtest

Edit the `RSI70Strategy` class parameters or modify the `main()` function.
