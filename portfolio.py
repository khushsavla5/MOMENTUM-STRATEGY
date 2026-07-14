"""
Portfolio management and tracking for RSI 70 Strategy
"""

import pandas as pd
import numpy as np
from datetime import datetime


class Position:
    """Represents a single stock position"""

    def __init__(self, symbol, entry_date, entry_price, quantity, weight=None):
        self.symbol = symbol
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.quantity = quantity
        self.weight = weight
        self.current_price = entry_price
        self.exit_date = None
        self.exit_price = None
        self.status = 'open'
        self.entry_rsi = None
        self.exit_rsi = None

    def get_unrealized_pnl(self):
        """Get unrealized P&L"""
        if self.status == 'open':
            return (self.current_price - self.entry_price) * self.quantity
        return 0

    def get_unrealized_pnl_pct(self):
        """Get unrealized P&L %"""
        if self.status == 'open' and self.entry_price > 0:
            return ((self.current_price - self.entry_price) / self.entry_price) * 100
        return 0

    def close(self, exit_date, exit_price, exit_rsi=None):
        """Close the position"""
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_rsi = exit_rsi
        self.status = 'closed'

    def get_realized_pnl(self):
        """Get realized P&L"""
        if self.status == 'closed':
            return (self.exit_price - self.entry_price) * self.quantity
        return 0

    def get_realized_pnl_pct(self):
        """Get realized P&L %"""
        if self.status == 'closed' and self.entry_price > 0:
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        return 0

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'entry_date': self.entry_date,
            'entry_price': self.entry_price,
            'entry_rsi': self.entry_rsi,
            'quantity': self.quantity,
            'exit_date': self.exit_date,
            'exit_price': self.exit_price,
            'exit_rsi': self.exit_rsi,
            'pnl': self.get_realized_pnl(),
            'pnl_pct': self.get_realized_pnl_pct(),
            'status': self.status
        }


class Portfolio:
    """Manages portfolio of positions"""

    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.closed_positions = []
        self.equity_curve = []
        self.date_log = []

    def add_position(self, symbol, entry_date, entry_price, quantity, weight=None, rsi=None):
        """Add a new position"""
        pos = Position(symbol, entry_date, entry_price, quantity, weight)
        pos.entry_rsi = rsi
        self.positions[symbol] = pos

    def close_position(self, symbol, exit_date, exit_price, exit_rsi=None):
        """Close an existing position"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            pos.close(exit_date, exit_price, exit_rsi)
            self.closed_positions.append(pos)
            del self.positions[symbol]

    def update_prices(self, price_data, date):
        """Update current prices for all positions"""
        for symbol in self.positions:
            if symbol in price_data:
                self.positions[symbol].current_price = price_data[symbol]

    def get_total_equity(self):
        """Get total portfolio equity"""
        unrealized = sum(pos.get_unrealized_pnl() for pos in self.positions.values())
        realized = sum(pos.get_realized_pnl() for pos in self.closed_positions)
        return self.initial_capital + unrealized + realized

    def get_total_return_pct(self):
        """Get total return %"""
        total_equity = self.get_total_equity()
        if self.initial_capital > 0:
            return ((total_equity - self.initial_capital) / self.initial_capital) * 100
        return 0

    def get_summary(self):
        """Get portfolio summary"""
        total_positions = len(self.positions) + len(self.closed_positions)
        open_positions = len(self.positions)
        closed_positions = len(self.closed_positions)

        total_pnl = sum(pos.get_realized_pnl() for pos in self.closed_positions)
        total_pnl_pct = sum(pos.get_realized_pnl_pct() for pos in self.closed_positions)

        winning_trades = sum(1 for pos in self.closed_positions if pos.get_realized_pnl() > 0)
        losing_trades = sum(1 for pos in self.closed_positions if pos.get_realized_pnl() < 0)

        return {
            'total_positions': total_positions,
            'open_positions': open_positions,
            'closed_positions': closed_positions,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'current_equity': self.get_total_equity(),
            'total_return_pct': self.get_total_return_pct()
        }

    def log_date_snapshot(self, date, notes=''):
        """Log equity snapshot for a date"""
        self.equity_curve.append({
            'date': date,
            'equity': self.get_total_equity(),
            'return_pct': self.get_total_return_pct(),
            'open_positions': len(self.positions),
            'notes': notes
        })

    def get_closed_trades_df(self):
        """Get closed trades as DataFrame"""
        trades_data = [pos.to_dict() for pos in self.closed_positions]
        return pd.DataFrame(trades_data)

    def get_equity_curve_df(self):
        """Get equity curve as DataFrame"""
        return pd.DataFrame(self.equity_curve)
