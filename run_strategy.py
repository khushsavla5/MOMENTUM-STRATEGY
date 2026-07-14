#!/usr/bin/env python3
"""
Main entry point to run the RSI 70 Momentum Strategy
"""

import sys
import logging
from datetime import datetime
from nifty_smallcap_250_rsi_strategy import RSI70Strategy
from config import STRATEGY_CONFIG, OUTPUT_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_backtest():
    """Execute the full backtest"""

    print("\n" + "="*80)
    print("RSI 70 MOMENTUM STRATEGY BACKTEST")
    print("NIFTY SMALL CAP 250")
    print("="*80)
    print(f"Start Date: {STRATEGY_CONFIG['start_date']}")
    print(f"End Date: {STRATEGY_CONFIG['end_date']}")
    print(f"RSI Threshold: {STRATEGY_CONFIG['rsi_threshold']}")
    print(f"Rebalance Frequency: {STRATEGY_CONFIG['rebalance_frequency'].upper()}")
    print("="*80 + "\n")

    try:
        # Initialize strategy
        strategy = RSI70Strategy(
            start_date=STRATEGY_CONFIG['start_date'],
            end_date=STRATEGY_CONFIG['end_date'],
            rsi_threshold=STRATEGY_CONFIG['rsi_threshold']
        )

        # Fetch data
        logger.info("Fetching stock data...")
        strategy.fetch_data()

        if not strategy.data:
            logger.error("No data fetched. Exiting.")
            return False

        # Run backtest
        logger.info("Running backtest with quarterly rebalancing...")
        strategy.backtest()

        # Generate report
        logger.info("Generating performance report...")
        strategy.generate_report()

        # Save results
        logger.info(f"Saving results to {OUTPUT_CONFIG['results_file']}...")
        strategy.save_results(OUTPUT_CONFIG['results_file'])

        print("\n" + "="*80)
        print("BACKTEST COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"Results saved to: {OUTPUT_CONFIG['results_file']}")
        print("="*80 + "\n")

        return True

    except Exception as e:
        logger.error(f"Error during backtest: {str(e)}", exc_info=True)
        return False


if __name__ == '__main__':
    success = run_backtest()
    sys.exit(0 if success else 1)
