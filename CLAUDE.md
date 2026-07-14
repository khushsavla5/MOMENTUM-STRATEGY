# MOMENTUM-STRATEGY Repository

## Project Overview

A momentum-based trading strategy implementation for the NIFTY SMALL CAP 250 index. The strategy enters positions when RSI exceeds 70 (overbought/momentum signal) and exits when RSI drops below 70. Portfolio is rebalanced quarterly.

## Technology Stack

- **Language**: Python 3.7+
- **Data Source**: Yahoo Finance (yfinance)
- **Technical Analysis**: TA library (RSI calculation)
- **Data Processing**: Pandas, NumPy

## Project Structure

```
MOMENTUM-STRATEGY/
├── README.md                                # Strategy documentation
├── CLAUDE.md                                # This file
├── requirements.txt                         # Python dependencies
├── config.py                                # Configuration parameters
├── nifty_smallcap_250_rsi_strategy.py      # Main strategy implementation
├── portfolio.py                             # Portfolio tracking classes
├── run_strategy.py                          # Entry point script
└── .gitignore                              # Git ignore rules
```

## Key Files

### nifty_smallcap_250_rsi_strategy.py
Main strategy class `RSI70Strategy` that:
- Fetches historical OHLC data for stocks
- Calculates RSI indicator (14-period)
- Implements entry/exit logic
- Manages quarterly rebalancing
- Generates performance reports

### portfolio.py
Portfolio management classes:
- `Position`: Individual stock position tracking
- `Portfolio`: Portfolio-level aggregation and metrics

### config.py
Configuration dictionary including:
- Strategy parameters (dates, RSI threshold)
- NIFTY SMALL CAP 250 constituents
- Portfolio settings
- Risk management parameters
- Output configuration

### run_strategy.py
Executable script that:
- Initializes the strategy
- Runs the backtest
- Generates reports
- Saves results to CSV

## Usage

### Installation
```bash
pip install -r requirements.txt
```

### Running the Strategy
```bash
python run_strategy.py
```

### Or Direct Import
```python
from nifty_smallcap_250_rsi_strategy import RSI70Strategy

strategy = RSI70Strategy(
    start_date='2025-01-01',
    end_date='2025-12-31',
    rsi_threshold=70
)
strategy.fetch_data()
strategy.backtest()
strategy.generate_report()
```

## Strategy Logic

### Entry
- Monitor RSI of each stock in NIFTY SMALL CAP 250
- At quarterly rebalance dates, identify stocks with RSI > 70
- Allocate equal weight to all entry candidates
- Record entry date, price, and RSI

### Exit
- Track RSI daily for all open positions
- Exit when RSI drops below 70
- Record exit date, price, and RSI
- Calculate P&L for closed position

### Rebalancing
Quarterly dates:
- Q1: 2025-01-01 to 2025-03-31
- Q2: 2025-04-01 to 2025-06-30
- Q3: 2025-07-01 to 2025-09-30
- Q4: 2025-10-01 to 2025-12-31

At end of each quarter:
- Close any remaining open positions
- Identify new entry candidates for next quarter
- Rebalance portfolio with equal weighting

## Output

The script generates:
1. **Console Output**
   - Data fetching progress
   - Quarterly breakdown with entry counts
   - Comprehensive performance metrics
   - Top 10 winning trades
   - All trades table

2. **CSV Files**
   - `rsi_70_backtest_results.csv`: Trade-level details

## Performance Metrics

- **Total Trades**: Number of completed trades
- **Winning/Losing Trades**: Count and win rate
- **Average Return**: Mean return per trade (%)
- **Best/Worst Trade**: Max and min returns
- **Avg Win/Loss**: Average return for profitable and losing trades
- **Total P&L**: Absolute profit/loss in rupees

## Customization Options

Edit `config.py` to modify:
- `RSI_THRESHOLD`: Entry signal level (currently 70)
- `NIFTY_SMALLCAP_250`: List of stock symbols
- `PORTFOLIO_CONFIG`: Initial capital, position sizing
- `RISK_CONFIG`: Stop loss, take profit levels
- `OUTPUT_CONFIG`: Output file names

Or pass parameters to `RSI70Strategy`:
```python
strategy = RSI70Strategy(
    start_date='2025-01-01',
    end_date='2025-12-31',
    rsi_threshold=70
)
```

## Data Requirements

- Internet connection for fetching data from Yahoo Finance
- 14+ trading days of data per stock for RSI calculation
- NSE stock tickers must include `.NS` suffix (e.g., 'RELIANCE.NS')

## Assumptions & Limitations

1. **No Transaction Costs**: Backtest assumes no slippage or fees
2. **Perfect Entry/Exit**: Assumes execution at exact RSI levels
3. **No Capital Constraints**: Can allocate capital to all entry signals
4. **Historical Data**: Strategy is backward-looking and not guaranteed future performance
5. **Survivorship Bias**: Only tests constituents available on Yahoo Finance

## Future Enhancements

- [ ] Add transaction cost modeling
- [ ] Implement walk-forward analysis
- [ ] Add position sizing based on volatility
- [ ] Calculate Sharpe ratio and other risk metrics
- [ ] Add Monte Carlo analysis
- [ ] Integrate real-time data for live trading
- [ ] Add stop-loss and take-profit levels
- [ ] Fetch real NIFTY SMALL CAP 250 constituents from NSE

## Notes for Developers

- Ensure all dependencies in `requirements.txt` are installed
- Use Python 3.7 or higher
- Yahoo Finance data may have gaps for low-volume stocks
- RSI uses 14-period default (configurable in code)
- Strategy assumes market hours data availability
