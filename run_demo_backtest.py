#!/usr/bin/env python3
"""
Demo backtest with simulated data to show strategy performance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_simulated_stock_data(symbol, start_date='2025-01-01', end_date='2025-12-31'):
    """Generate realistic simulated OHLC data for a stock"""
    np.random.seed(hash(symbol) % 2**32)

    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    # Filter to trading days only (weekdays)
    date_range = date_range[date_range.weekday < 5]

    n_days = len(date_range)

    # Starting price between 500-5000
    start_price = np.random.uniform(500, 5000)

    # Generate price with random walk
    returns = np.random.normal(0.0005, 0.02, n_days)
    prices = start_price * np.exp(np.cumsum(returns))

    data = {
        'Date': date_range,
        'Open': prices * (1 + np.random.uniform(-0.01, 0.01, n_days)),
        'High': prices * (1 + np.random.uniform(0.005, 0.03, n_days)),
        'Low': prices * (1 + np.random.uniform(-0.03, -0.005, n_days)),
        'Close': prices,
        'Volume': np.random.uniform(100000, 5000000, n_days)
    }

    df = pd.DataFrame(data)
    df = df.set_index('Date')
    return df


def calculate_rsi(data, period=14):
    """Calculate RSI"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


class DemoRSI70Strategy:
    """Demo RSI 70 Strategy with simulated data"""

    def __init__(self, start_date='2025-01-01', end_date='2025-12-31', rsi_threshold=70):
        self.start_date = start_date
        self.end_date = end_date
        self.rsi_threshold = rsi_threshold
        self.stocks = [
            'STOCK_001', 'STOCK_002', 'STOCK_003', 'STOCK_004', 'STOCK_005',
            'STOCK_006', 'STOCK_007', 'STOCK_008', 'STOCK_009', 'STOCK_010',
            'STOCK_011', 'STOCK_012', 'STOCK_013', 'STOCK_014', 'STOCK_015',
            'STOCK_016', 'STOCK_017', 'STOCK_018', 'STOCK_019', 'STOCK_020'
        ]
        self.data = {}
        self.trades = []
        self.positions = {}

    def fetch_data(self):
        """Generate simulated data for all stocks"""
        print(f"Generating simulated data for {len(self.stocks)} stocks...")
        for symbol in self.stocks:
            df = generate_simulated_stock_data(symbol, self.start_date, self.end_date)
            df['RSI'] = calculate_rsi(df['Close'], period=14)
            self.data[symbol] = df
            print(f"✓ {symbol}: {len(df)} trading days")
        print()

    def _get_quarterly_dates(self):
        """Get quarterly rebalance dates"""
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
            print(f"\n{'='*60}")
            print(f"Quarter {quarter_idx + 1}: {quarter_start} to {quarter_end}")
            print(f"{'='*60}")

            # Find entry points at quarter start
            entry_candidates = self._find_entry_points(quarter_start)

            if entry_candidates:
                print(f"Entry candidates (RSI > {self.rsi_threshold}): {len(entry_candidates)}")

                # Equal weight portfolio
                weight = 1.0 / len(entry_candidates)

                for symbol in entry_candidates:
                    if symbol in self.data:
                        entry_price = self._get_price_at_date(symbol, quarter_start)
                        self.positions[symbol] = {
                            'entry_date': quarter_start,
                            'entry_price': entry_price,
                            'weight': weight,
                            'entry_rsi': self._get_rsi_at_date(symbol, quarter_start),
                            'exit_date': None,
                            'exit_price': None,
                            'status': 'open'
                        }

                # Track positions through quarter
                self._track_exits(quarter_start, quarter_end)
            else:
                print("No entry candidates found")

            # Close remaining positions at quarter end
            self._close_quarter_positions(quarter_end)

    def _find_entry_points(self, start_date):
        """Find stocks with RSI > 70"""
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
        """Get closing price at date"""
        date = pd.to_datetime(date_str)
        df = self.data[symbol]
        df_on_date = df[df.index <= date]
        if len(df_on_date) > 0:
            return df_on_date['Close'].iloc[-1]
        return None

    def _get_rsi_at_date(self, symbol, date_str):
        """Get RSI at date"""
        date = pd.to_datetime(date_str)
        df = self.data[symbol]
        df_on_date = df[df.index <= date]
        if len(df_on_date) > 0:
            return df_on_date['RSI'].iloc[-1]
        return None

    def _track_exits(self, quarter_start, quarter_end):
        """Track RSI < 70 exit signals"""
        start_dt = pd.to_datetime(quarter_start)
        end_dt = pd.to_datetime(quarter_end)

        for symbol, position in self.positions.items():
            if position['status'] == 'open' and symbol in self.data:
                df = self.data[symbol]
                df_quarter = df[(df.index > start_dt) & (df.index <= end_dt)]

                for date, row in df_quarter.iterrows():
                    rsi_value = row['RSI']
                    if pd.notna(rsi_value) and rsi_value < self.rsi_threshold:
                        position['exit_date'] = str(date.date())
                        position['exit_price'] = row['Close']
                        position['status'] = 'closed'
                        self._record_trade(symbol, position)
                        break

    def _close_quarter_positions(self, quarter_end):
        """Close remaining positions at quarter end"""
        for symbol, position in self.positions.items():
            if position['status'] == 'open':
                exit_price = self._get_price_at_date(symbol, quarter_end)
                if exit_price:
                    position['exit_date'] = quarter_end
                    position['exit_price'] = exit_price
                    position['status'] = 'closed'
                    self._record_trade(symbol, position)

    def _record_trade(self, symbol, position):
        """Record completed trade"""
        entry_price = position['entry_price']
        exit_price = position['exit_price']

        if entry_price and exit_price:
            pnl = exit_price - entry_price
            pnl_pct = (pnl / entry_price) * 100 if entry_price > 0 else 0

            self.trades.append({
                'symbol': symbol,
                'entry_date': position['entry_date'],
                'entry_price': entry_price,
                'entry_rsi': position['entry_rsi'],
                'exit_date': position['exit_date'],
                'exit_price': exit_price,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'days_held': (pd.to_datetime(position['exit_date']) - pd.to_datetime(position['entry_date'])).days
            })

    def generate_report(self):
        """Generate performance report"""
        print("\n" + "="*100)
        print("STRATEGY PERFORMANCE REPORT - RSI 70 MOMENTUM STRATEGY (SIMULATED DATA)")
        print("="*100)
        print(f"Period: {self.start_date} to {self.end_date}")
        print(f"Stocks Analyzed: {len(self.data)}")
        print(f"Total Trades: {len(self.trades)}")
        print()

        if self.trades:
            trades_df = pd.DataFrame(self.trades)

            # Winning and losing trades
            winning_trades = trades_df[trades_df['pnl'] > 0]
            losing_trades = trades_df[trades_df['pnl'] < 0]
            breakeven_trades = trades_df[trades_df['pnl'] == 0]

            print(f"Winning Trades: {len(winning_trades)}")
            print(f"Losing Trades: {len(losing_trades)}")
            print(f"Breakeven Trades: {len(breakeven_trades)}")

            # Performance metrics
            total_pnl = trades_df['pnl'].sum()
            avg_pnl_pct = trades_df['pnl_pct'].mean()
            max_pnl_pct = trades_df['pnl_pct'].max()
            min_pnl_pct = trades_df['pnl_pct'].min()
            avg_hold_days = trades_df['days_held'].mean()

            print(f"\nTotal P&L: ₹{total_pnl:,.2f}")
            print(f"Average Return per Trade: {avg_pnl_pct:.2f}%")
            print(f"Best Trade: {max_pnl_pct:.2f}%")
            print(f"Worst Trade: {min_pnl_pct:.2f}%")
            print(f"Average Hold Days: {avg_hold_days:.1f}")

            win_rate = (len(winning_trades) / len(trades_df)) * 100 if len(trades_df) > 0 else 0
            print(f"Win Rate: {win_rate:.1f}%")

            if len(winning_trades) > 0:
                avg_win = winning_trades['pnl_pct'].mean()
                max_win = winning_trades['pnl_pct'].max()
                print(f"Average Winning Trade: {avg_win:.2f}%")
                print(f"Best Win: {max_win:.2f}%")

            if len(losing_trades) > 0:
                avg_loss = losing_trades['pnl_pct'].mean()
                max_loss = losing_trades['pnl_pct'].min()
                print(f"Average Losing Trade: {avg_loss:.2f}%")
                print(f"Worst Loss: {max_loss:.2f}%")

            if len(winning_trades) > 0 and len(losing_trades) > 0:
                profit_factor = (winning_trades['pnl'].sum()) / abs(losing_trades['pnl'].sum())
                print(f"Profit Factor: {profit_factor:.2f}")

            print("\n" + "-"*100)
            print("TOP 10 WINNING TRADES")
            print("-"*100)
            top_trades = trades_df.nlargest(10, 'pnl_pct')[
                ['symbol', 'entry_date', 'entry_price', 'exit_date', 'exit_price', 'pnl_pct', 'days_held']
            ].copy()
            top_trades['pnl_pct'] = top_trades['pnl_pct'].apply(lambda x: f"{x:.2f}%")
            print(top_trades.to_string(index=False))

            print("\n" + "-"*100)
            print("BOTTOM 10 TRADES")
            print("-"*100)
            bottom_trades = trades_df.nsmallest(10, 'pnl_pct')[
                ['symbol', 'entry_date', 'entry_price', 'exit_date', 'exit_price', 'pnl_pct', 'days_held']
            ].copy()
            bottom_trades['pnl_pct'] = bottom_trades['pnl_pct'].apply(lambda x: f"{x:.2f}%")
            print(bottom_trades.to_string(index=False))

            print("\n" + "-"*100)
            print("ALL TRADES (Sample: First 20)")
            print("-"*100)
            sample_trades = trades_df[
                ['symbol', 'entry_date', 'entry_price', 'exit_date', 'exit_price', 'pnl_pct', 'days_held']
            ].head(20).copy()
            sample_trades['pnl_pct'] = sample_trades['pnl_pct'].apply(lambda x: f"{x:.2f}%")
            print(sample_trades.to_string(index=False))

        else:
            print("No trades executed.")

        print("\n" + "="*100)

    def save_results(self, filename='demo_backtest_results.csv'):
        """Save results to CSV"""
        if self.trades:
            trades_df = pd.DataFrame(self.trades)
            trades_df.to_csv(filename, index=False)
            print(f"Results saved to {filename}")


def main():
    """Run the demo backtest"""
    strategy = DemoRSI70Strategy(
        start_date='2025-01-01',
        end_date='2025-12-31',
        rsi_threshold=70
    )

    strategy.fetch_data()
    strategy.backtest()
    strategy.generate_report()
    strategy.save_results('demo_backtest_results.csv')


if __name__ == '__main__':
    main()
