#!/usr/bin/env python3
"""
Generate realistic NIFTY SMALL CAP 250 data for 2025 backtest
Creates data with realistic RSI patterns and market behavior
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_nifty_smallcap_data(symbol, start_date='2025-01-01', end_date='2025-12-31', trend=None):
    """Generate realistic NIFTY SMALL CAP 250 stock data with RSI patterns"""
    np.random.seed(hash(symbol) % 2**32)

    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    date_range = date_range[date_range.weekday < 5]  # Trading days only
    n_days = len(date_range)

    # Starting price: typical NIFTY SMALL CAP stock
    start_price = np.random.uniform(200, 2000)

    # Create trend component - some stocks trending up, some down, some sideways
    if trend is None:
        trend = np.random.choice(['up', 'down', 'sideways'], p=[0.4, 0.3, 0.3])

    if trend == 'up':
        trend_component = np.linspace(0, 0.15, n_days)  # 15% uptrend
    elif trend == 'down':
        trend_component = np.linspace(0, -0.12, n_days)  # 12% downtrend
    else:
        trend_component = np.sin(np.linspace(0, 4*np.pi, n_days)) * 0.05  # Sideways

    # Daily returns with trend and volatility
    volatility = np.random.uniform(0.015, 0.035)
    returns = trend_component + np.random.normal(0.0003, volatility, n_days)
    prices = start_price * np.exp(np.cumsum(returns))

    # Create OHLC data
    data = {
        'Date': date_range,
        'Open': prices * (1 + np.random.uniform(-0.01, 0.01, n_days)),
        'High': prices * (1 + np.random.uniform(0.005, 0.03, n_days)),
        'Low': prices * (1 + np.random.uniform(-0.03, -0.005, n_days)),
        'Close': prices,
        'Volume': np.random.uniform(100000, 10000000, n_days)
    }

    df = pd.DataFrame(data)
    df = df.set_index('Date')
    return df


def calculate_rsi(data, period=14):
    """Calculate RSI with proper handling"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


class NiftySmallCapRSI70Strategy:
    """RSI 70 Strategy for NIFTY SMALL CAP 250 with realistic data"""

    def __init__(self, start_date='2025-01-01', end_date='2025-12-31', rsi_threshold=70, num_stocks=50):
        self.start_date = start_date
        self.end_date = end_date
        self.rsi_threshold = rsi_threshold
        self.num_stocks = num_stocks
        self.stocks = [f'NIFTYSC_{i:03d}' for i in range(1, num_stocks + 1)]
        self.data = {}
        self.trades = []
        self.positions = {}

    def fetch_data(self):
        """Generate realistic NIFTY SMALL CAP data"""
        print(f"\nGenerating realistic data for {len(self.stocks)} NIFTY SMALL CAP stocks...")
        print(f"Period: {self.start_date} to {self.end_date}\n")

        for i, symbol in enumerate(self.stocks):
            trend = np.random.choice(['up', 'down', 'sideways'], p=[0.35, 0.35, 0.30])
            df = generate_nifty_smallcap_data(symbol, self.start_date, self.end_date, trend=trend)
            df['RSI'] = calculate_rsi(df['Close'], period=14)
            self.data[symbol] = df

            if (i + 1) % 10 == 0:
                print(f"Generated data for {i + 1}/{len(self.stocks)} stocks...")

        print(f"\n✓ Successfully generated data for {len(self.data)} stocks\n")

    def _get_quarterly_dates(self):
        """Get quarterly rebalance dates for 2025"""
        return [
            ('2025-01-02', '2025-03-31'),
            ('2025-04-01', '2025-06-30'),
            ('2025-07-01', '2025-09-30'),
            ('2025-10-01', '2025-12-31')
        ]

    def backtest(self):
        """Run backtest with quarterly rebalancing"""
        quarterly_dates = self._get_quarterly_dates()

        for quarter_idx, (quarter_start, quarter_end) in enumerate(quarterly_dates):
            print(f"\n{'='*70}")
            print(f"QUARTER {quarter_idx + 1}: {quarter_start} to {quarter_end}")
            print(f"{'='*70}")

            # Find entry points at quarter start
            entry_candidates = self._find_entry_points(quarter_start)

            if entry_candidates:
                print(f"Entry Candidates (RSI > {self.rsi_threshold}): {len(entry_candidates)} stocks")
                print(f"Allocation: Equal weight ({100/len(entry_candidates):.1f}% each)")

                weight = 1.0 / len(entry_candidates)

                # Create positions
                positions_created = 0
                for symbol in entry_candidates:
                    if symbol in self.data:
                        entry_price = self._get_price_at_date(symbol, quarter_start)
                        entry_rsi = self._get_rsi_at_date(symbol, quarter_start)
                        if entry_price and pd.notna(entry_rsi):
                            self.positions[symbol] = {
                                'entry_date': quarter_start,
                                'entry_price': entry_price,
                                'entry_rsi': entry_rsi,
                                'weight': weight,
                                'exit_date': None,
                                'exit_price': None,
                                'exit_rsi': None,
                                'status': 'open'
                            }
                            positions_created += 1

                print(f"Positions Created: {positions_created}")

                # Track exits during quarter
                self._track_exits(quarter_start, quarter_end)

            else:
                print(f"Entry Candidates: 0 stocks with RSI > {self.rsi_threshold}")

            # Close remaining open positions at quarter end
            positions_closed = self._close_quarter_positions(quarter_end)
            print(f"Positions Closed at Quarter End: {positions_closed}")

    def _find_entry_points(self, start_date):
        """Find all stocks with RSI > 70 at start date"""
        entry_candidates = []
        start_dt = pd.to_datetime(start_date)

        for symbol, df in self.data.items():
            df_filtered = df[df.index <= start_dt]
            if len(df_filtered) > 0:
                latest_rsi = df_filtered['RSI'].iloc[-1]
                if pd.notna(latest_rsi) and latest_rsi > self.rsi_threshold:
                    entry_candidates.append(symbol)

        return entry_candidates

    def _get_price_at_date(self, symbol, date_str):
        """Get closing price at specific date"""
        date = pd.to_datetime(date_str)
        df = self.data[symbol]
        df_on_date = df[df.index <= date]
        if len(df_on_date) > 0:
            return df_on_date['Close'].iloc[-1]
        return None

    def _get_rsi_at_date(self, symbol, date_str):
        """Get RSI at specific date"""
        date = pd.to_datetime(date_str)
        df = self.data[symbol]
        df_on_date = df[df.index <= date]
        if len(df_on_date) > 0:
            return df_on_date['RSI'].iloc[-1]
        return None

    def _track_exits(self, quarter_start, quarter_end):
        """Track RSI < 70 exit signals during quarter"""
        start_dt = pd.to_datetime(quarter_start)
        end_dt = pd.to_datetime(quarter_end)

        for symbol, position in list(self.positions.items()):
            if position['status'] == 'open' and symbol in self.data:
                df = self.data[symbol]
                df_quarter = df[(df.index > start_dt) & (df.index <= end_dt)]

                for date, row in df_quarter.iterrows():
                    rsi_value = row['RSI']

                    if pd.notna(rsi_value) and rsi_value < self.rsi_threshold:
                        position['exit_date'] = str(date.date())
                        position['exit_price'] = row['Close']
                        position['exit_rsi'] = rsi_value
                        position['status'] = 'closed'
                        self._record_trade(symbol, position)
                        break

    def _close_quarter_positions(self, quarter_end):
        """Close all remaining open positions at quarter end"""
        closed_count = 0
        for symbol, position in list(self.positions.items()):
            if position['status'] == 'open':
                exit_price = self._get_price_at_date(symbol, quarter_end)
                exit_rsi = self._get_rsi_at_date(symbol, quarter_end)
                if exit_price:
                    position['exit_date'] = quarter_end
                    position['exit_price'] = exit_price
                    position['exit_rsi'] = exit_rsi
                    position['status'] = 'closed'
                    self._record_trade(symbol, position)
                    closed_count += 1
        return closed_count

    def _record_trade(self, symbol, position):
        """Record completed trade"""
        entry_price = position['entry_price']
        exit_price = position['exit_price']

        if entry_price and exit_price:
            pnl = exit_price - entry_price
            pnl_pct = (pnl / entry_price) * 100 if entry_price > 0 else 0
            days_held = (pd.to_datetime(position['exit_date']) - pd.to_datetime(position['entry_date'])).days

            self.trades.append({
                'symbol': symbol,
                'entry_date': position['entry_date'],
                'entry_price': round(entry_price, 2),
                'entry_rsi': round(position['entry_rsi'], 2) if pd.notna(position['entry_rsi']) else None,
                'exit_date': position['exit_date'],
                'exit_price': round(exit_price, 2),
                'exit_rsi': round(position['exit_rsi'], 2) if pd.notna(position['exit_rsi']) else None,
                'pnl': round(pnl, 2),
                'pnl_pct': round(pnl_pct, 2),
                'days_held': days_held
            })

    def generate_report(self):
        """Generate comprehensive performance report"""
        print("\n\n" + "="*100)
        print("NIFTY SMALL CAP 250 - RSI 70 MOMENTUM STRATEGY - BACKTEST RESULTS")
        print("="*100)
        print(f"Period: {self.start_date} to {self.end_date}")
        print(f"Universe: {len(self.data)} Stocks")
        print(f"Entry Signal: RSI > {self.rsi_threshold}")
        print(f"Exit Signal: RSI < {self.rsi_threshold}")
        print(f"Rebalance Frequency: Quarterly")
        print("="*100)
        print(f"\nTotal Trades Executed: {len(self.trades)}\n")

        if self.trades:
            trades_df = pd.DataFrame(self.trades)

            # Classification
            winning_trades = trades_df[trades_df['pnl'] > 0]
            losing_trades = trades_df[trades_df['pnl'] < 0]
            breakeven_trades = trades_df[trades_df['pnl'] == 0]

            print(f"{'TRADE STATISTICS':-^100}")
            print(f"Winning Trades:     {len(winning_trades):>4} ({len(winning_trades)/len(trades_df)*100:>5.1f}%)")
            print(f"Losing Trades:      {len(losing_trades):>4} ({len(losing_trades)/len(trades_df)*100:>5.1f}%)")
            print(f"Breakeven Trades:   {len(breakeven_trades):>4} ({len(breakeven_trades)/len(trades_df)*100:>5.1f}%)")

            # Performance metrics
            total_pnl = trades_df['pnl'].sum()
            total_pnl_pct = trades_df['pnl_pct'].sum()
            avg_pnl_pct = trades_df['pnl_pct'].mean()
            max_pnl_pct = trades_df['pnl_pct'].max()
            min_pnl_pct = trades_df['pnl_pct'].min()
            avg_hold_days = trades_df['days_held'].mean()

            print(f"\n{'PERFORMANCE METRICS':-^100}")
            print(f"Total P&L (₹):              {total_pnl:>15,.2f}")
            print(f"Total Return (%):           {total_pnl_pct:>15.2f}%")
            print(f"Average Return/Trade (%):  {avg_pnl_pct:>15.2f}%")
            print(f"Best Trade (%):             {max_pnl_pct:>15.2f}%")
            print(f"Worst Trade (%):            {min_pnl_pct:>15.2f}%")
            print(f"Average Hold Days:          {avg_hold_days:>15.1f}")
            print(f"Win Rate (%):               {len(winning_trades)/len(trades_df)*100:>15.1f}%")

            if len(winning_trades) > 0:
                avg_win = winning_trades['pnl_pct'].mean()
                max_win = winning_trades['pnl_pct'].max()
                total_win = winning_trades['pnl'].sum()
                print(f"\n{'WINNING TRADES':-^100}")
                print(f"Count:                      {len(winning_trades):>15}")
                print(f"Average Win (%):            {avg_win:>15.2f}%")
                print(f"Best Win (%):               {max_win:>15.2f}%")
                print(f"Total Win (₹):              {total_win:>15,.2f}")

            if len(losing_trades) > 0:
                avg_loss = losing_trades['pnl_pct'].mean()
                max_loss = losing_trades['pnl_pct'].min()
                total_loss = losing_trades['pnl'].sum()
                print(f"\n{'LOSING TRADES':-^100}")
                print(f"Count:                      {len(losing_trades):>15}")
                print(f"Average Loss (%):           {avg_loss:>15.2f}%")
                print(f"Worst Loss (%):             {max_loss:>15.2f}%")
                print(f"Total Loss (₹):             {total_loss:>15,.2f}")

            if len(winning_trades) > 0 and len(losing_trades) > 0:
                profit_factor = winning_trades['pnl'].sum() / abs(losing_trades['pnl'].sum())
                print(f"Profit Factor:              {profit_factor:>15.2f}")

            # Top trades
            print(f"\n{'TOP 20 WINNING TRADES':-^100}")
            top_trades = trades_df.nlargest(20, 'pnl_pct')[
                ['symbol', 'entry_date', 'entry_price', 'entry_rsi', 'exit_date', 'exit_price', 'exit_rsi', 'pnl_pct', 'days_held']
            ].copy()
            print(top_trades.to_string(index=False))

            # Bottom trades
            print(f"\n{'BOTTOM 20 LOSING TRADES':-^100}")
            bottom_trades = trades_df.nsmallest(20, 'pnl_pct')[
                ['symbol', 'entry_date', 'entry_price', 'entry_rsi', 'exit_date', 'exit_price', 'exit_rsi', 'pnl_pct', 'days_held']
            ].copy()
            print(bottom_trades.to_string(index=False))

            # All trades summary
            print(f"\n{'ALL TRADES SUMMARY':-^100}")
            all_trades = trades_df[
                ['symbol', 'entry_date', 'entry_price', 'entry_rsi', 'exit_date', 'exit_price', 'exit_rsi', 'pnl_pct', 'days_held']
            ].copy()
            print(f"Total Records: {len(all_trades)}")
            print(all_trades.to_string(index=False))

        else:
            print("No trades executed during backtest period.")

        print("\n" + "="*100)

    def save_results(self, filename='rsi_70_backtest_results.csv'):
        """Save results to CSV"""
        if self.trades:
            trades_df = pd.DataFrame(self.trades)
            trades_df.to_csv(filename, index=False)
            print(f"\n✓ Results saved to: {filename}")
            return trades_df
        return None


def main():
    """Run the complete backtest"""
    print("\n" + "="*100)
    print("NIFTY SMALL CAP 250 - RSI 70 MOMENTUM STRATEGY BACKTEST")
    print("="*100)

    # Run backtest with 50 stocks (realistic subset of NIFTY SMALL CAP 250)
    strategy = NiftySmallCapRSI70Strategy(
        start_date='2025-01-01',
        end_date='2025-12-31',
        rsi_threshold=70,
        num_stocks=50
    )

    strategy.fetch_data()
    strategy.backtest()
    trades_df = strategy.generate_report()
    strategy.save_results('rsi_70_backtest_results.csv')

    return trades_df


if __name__ == '__main__':
    main()
