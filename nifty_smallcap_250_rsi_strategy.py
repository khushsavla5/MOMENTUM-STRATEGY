"""
RSI 70 Momentum Strategy for NIFTY SMALL CAP 250
Entry: When RSI > 70
Exit: When RSI < 70
Rebalance: Quarterly
Backtest Period: 2025 Calendar Year
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from ta.momentum import rsi
import warnings

warnings.filterwarnings('ignore')


class RSI70Strategy:
    """NIFTY SMALL CAP 250 RSI 70 Momentum Strategy"""

    def __init__(self, start_date='2025-01-01', end_date='2025-12-31', rsi_threshold=70):
        self.start_date = start_date
        self.end_date = end_date
        self.rsi_threshold = rsi_threshold
        self.data = {}
        self.positions = {}
        self.portfolio_history = []
        self.trades = []
        self.nifty_smallcap_250 = self._get_nifty_smallcap_250()

    def _get_nifty_smallcap_250(self):
        """Get NIFTY SMALL CAP 250 constituents"""
        # NIFTY SMALL CAP 250 top holdings (commonly traded)
        # In production, this would be fetched from NSE website
        nifty_smallcap_250 = [
            'ATLASSTEEL.NS', 'BAGEL.NS', 'BASF.NS', 'BEML.NS', 'CRAFTSMAN.NS',
            'DEEPAKINDS.NS', 'EXIDEIND.NS', 'FIEM.NS', 'FIEMAC.NS', 'FLUOROCHEM.NS',
            'GLANRES.NS', 'GREENPOWER.NS', 'HCLTECH.NS', 'HEIDELBERG.NS', 'HINDPETRO.NS',
            'INDHOTEL.NS', 'INFRATEL.NS', 'IPCALAB.NS', 'ITESOFT.NS', 'JAMNEETEXP.NS',
            'JKPAPER.NS', 'KANSAINER.NS', 'KARURVYSYA.NS', 'KTKBANK.NS', 'LUMAXTECH.NS',
            'MARINE.NS', 'MARIMMT.NS', 'MARKSANS.NS', 'MCLGROUP.NS', 'MEDPLUS.NS',
            'MINDTREE.NS', 'MOIL.NS', 'MRF.NS', 'MRPL.NS', 'MSPL.NS',
            'NATIONALUM.NS', 'NAVNEETGG.NS', 'NDTV.NS', 'NEWTECH.NS', 'NHPC.NS',
            'NLCINDIA.NS', 'NTPC.NS', 'OFSS.NS', 'ORIENTREF.NS', 'ORNAMECOM.NS',
            'PARAM.NS', 'PARADEEP.NS', 'PARTHASYS.NS', 'PEARLPOLY.NS', 'PHILIPS.NS',
            'PNBHOUSING.NS', 'POWERINDIA.NS', 'PRAYAGCEM.NS', 'PRICOLGROUP.NS', 'PRICOL.NS'
        ]
        return nifty_smallcap_250[:30]  # Start with first 30 for manageability

    def fetch_data(self):
        """Fetch historical data for all stocks"""
        print(f"Fetching data for {len(self.nifty_smallcap_250)} stocks...")

        for symbol in self.nifty_smallcap_250:
            try:
                df = yf.download(
                    symbol,
                    start=self.start_date,
                    end=self.end_date,
                    progress=False
                )

                if len(df) > 0:
                    df['RSI'] = rsi(df['Close'], window=14)
                    self.data[symbol] = df
                    print(f"✓ {symbol}: {len(df)} days")
                else:
                    print(f"✗ {symbol}: No data")

            except Exception as e:
                print(f"✗ {symbol}: Error - {str(e)[:50]}")

        print(f"\nSuccessfully fetched data for {len(self.data)} stocks\n")

    def _get_quarterly_dates(self):
        """Get quarterly rebalance dates for 2025"""
        return [
            ('2025-01-01', '2025-03-31'),
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
            entry_candidates = self._find_entry_points(quarter_start, quarter_end)

            if entry_candidates:
                print(f"Entry candidates (RSI > {self.rsi_threshold}): {len(entry_candidates)}")
                print(f"Symbols: {entry_candidates}")

                # Equal weight portfolio
                weight = 1.0 / len(entry_candidates) if entry_candidates else 0

                for symbol in entry_candidates:
                    if symbol in self.data:
                        self.positions[symbol] = {
                            'entry_date': quarter_start,
                            'entry_price': self._get_price_at_date(symbol, quarter_start),
                            'weight': weight,
                            'exit_date': None,
                            'exit_price': None,
                            'status': 'open'
                        }

                # Track positions through quarter
                self._track_exits(quarter_start, quarter_end)
            else:
                print("No entry candidates found")

            # End of quarter: close remaining positions
            self._close_quarter_positions(quarter_end)

    def _find_entry_points(self, start_date, end_date):
        """Find stocks with RSI > 70 at start of period"""
        entry_candidates = []
        start_dt = pd.to_datetime(start_date)

        for symbol, df in self.data.items():
            # Filter data up to start date
            df_filtered = df[df.index <= start_dt]

            if len(df_filtered) > 0:
                latest_rsi = df_filtered['RSI'].iloc[-1]

                if pd.notna(latest_rsi) and latest_rsi > self.rsi_threshold:
                    entry_candidates.append(symbol)

        return entry_candidates

    def _get_price_at_date(self, symbol, date_str):
        """Get closing price at specific date"""
        if symbol not in self.data:
            return None

        date = pd.to_datetime(date_str)
        df = self.data[symbol]
        df_on_date = df[df.index <= date]

        if len(df_on_date) > 0:
            return df_on_date['Close'].iloc[-1]
        return None

    def _track_exits(self, quarter_start, quarter_end):
        """Track RSI < 70 exit signals during quarter"""
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
        """Close all remaining open positions at quarter end"""
        end_dt = pd.to_datetime(quarter_end)

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
                'exit_date': position['exit_date'],
                'exit_price': exit_price,
                'pnl': pnl,
                'pnl_pct': pnl_pct
            })

    def generate_report(self):
        """Generate performance report"""
        print("\n" + "="*80)
        print("STRATEGY PERFORMANCE REPORT - RSI 70 MOMENTUM STRATEGY")
        print("="*80)
        print(f"Period: {self.start_date} to {self.end_date}")
        print(f"Stocks Analyzed: {len(self.data)}")
        print(f"Total Trades: {len(self.trades)}")

        if self.trades:
            trades_df = pd.DataFrame(self.trades)

            # Winning and losing trades
            winning_trades = trades_df[trades_df['pnl'] > 0]
            losing_trades = trades_df[trades_df['pnl'] < 0]

            print(f"\nWinning Trades: {len(winning_trades)}")
            print(f"Losing Trades: {len(losing_trades)}")

            # Performance metrics
            total_pnl = trades_df['pnl'].sum()
            avg_pnl_pct = trades_df['pnl_pct'].mean()
            max_pnl_pct = trades_df['pnl_pct'].max()
            min_pnl_pct = trades_df['pnl_pct'].min()

            print(f"\nTotal P&L: ₹{total_pnl:,.2f}")
            print(f"Average Return per Trade: {avg_pnl_pct:.2f}%")
            print(f"Best Trade: {max_pnl_pct:.2f}%")
            print(f"Worst Trade: {min_pnl_pct:.2f}%")

            win_rate = (len(winning_trades) / len(trades_df)) * 100 if len(trades_df) > 0 else 0
            print(f"Win Rate: {win_rate:.1f}%")

            if len(winning_trades) > 0:
                avg_win = winning_trades['pnl_pct'].mean()
                print(f"Average Winning Trade: {avg_win:.2f}%")

            if len(losing_trades) > 0:
                avg_loss = losing_trades['pnl_pct'].mean()
                print(f"Average Losing Trade: {avg_loss:.2f}%")

            print("\n" + "-"*80)
            print("TOP 10 TRADES")
            print("-"*80)
            top_trades = trades_df.nlargest(10, 'pnl_pct')[
                ['symbol', 'entry_date', 'entry_price', 'exit_date', 'exit_price', 'pnl_pct']
            ]
            print(top_trades.to_string(index=False))

            print("\n" + "-"*80)
            print("ALL TRADES")
            print("-"*80)
            print(trades_df[
                ['symbol', 'entry_date', 'entry_price', 'exit_date', 'exit_price', 'pnl_pct']
            ].sort_values('entry_date').to_string(index=False))
        else:
            print("\nNo trades executed.")

        print("\n" + "="*80)

    def save_results(self, filename='backtest_results.csv'):
        """Save results to CSV"""
        if self.trades:
            trades_df = pd.DataFrame(self.trades)
            trades_df.to_csv(filename, index=False)
            print(f"\nResults saved to {filename}")


def main():
    """Run the backtest"""
    strategy = RSI70Strategy(
        start_date='2025-01-01',
        end_date='2025-12-31',
        rsi_threshold=70
    )

    strategy.fetch_data()
    strategy.backtest()
    strategy.generate_report()
    strategy.save_results('rsi_70_backtest_results.csv')


if __name__ == '__main__':
    main()
