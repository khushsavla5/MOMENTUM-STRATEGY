"""
Configuration file for RSI 70 Strategy
"""

# Strategy Parameters
STRATEGY_CONFIG = {
    'start_date': '2025-01-01',
    'end_date': '2025-12-31',
    'rsi_threshold': 70,
    'rsi_period': 14,
    'rebalance_frequency': 'quarterly',  # quarterly, monthly, etc.
}

# NIFTY SMALL CAP 250 Constituents (sample)
# In production, fetch from NSE website
NIFTY_SMALLCAP_250 = [
    'ATLASSTEEL.NS', 'BAGEL.NS', 'BASF.NS', 'BEML.NS', 'CRAFTSMAN.NS',
    'DEEPAKINDS.NS', 'EXIDEIND.NS', 'FIEM.NS', 'FIEMAC.NS', 'FLUOROCHEM.NS',
    'GLANRES.NS', 'GREENPOWER.NS', 'HCLTECH.NS', 'HEIDELBERG.NS', 'HINDPETRO.NS',
    'INDHOTEL.NS', 'INFRATEL.NS', 'IPCALAB.NS', 'ITESOFT.NS', 'JAMNEETEXP.NS',
    'JKPAPER.NS', 'KANSAINER.NS', 'KARURVYSYA.NS', 'KTKBANK.NS', 'LUMAXTECH.NS',
    'MARINE.NS', 'MARIMMT.NS', 'MARKSANS.NS', 'MCLGROUP.NS', 'MEDPLUS.NS',
    'MINDTREE.NS', 'MOIL.NS', 'MRF.NS', 'MRPL.NS', 'MSPL.NS',
    'NATIONALUM.NS', 'NAVNEETGG.NS', 'NDTV.NS', 'NEWTECH.NS', 'NHPC.NS',
]

# Portfolio Parameters
PORTFOLIO_CONFIG = {
    'initial_capital': 1000000,  # ₹10 lakhs
    'position_sizing': 'equal_weight',  # equal_weight or risk_based
    'max_positions': None,  # None for all, or set max
    'rebalance_slippage_pct': 0.1,  # 0.1% slippage on entries
    'transaction_cost_pct': 0.0,  # Trading costs
}

# Risk Management
RISK_CONFIG = {
    'stop_loss_pct': None,  # Hard stop loss as % of entry
    'take_profit_pct': None,  # Hard profit target
    'max_loss_per_trade_pct': None,  # Max loss per position
}

# Output
OUTPUT_CONFIG = {
    'results_file': 'rsi_70_backtest_results.csv',
    'trades_file': 'trades_detail.csv',
    'equity_curve_file': 'equity_curve.csv',
    'verbose': True,  # Print detailed logs
}
