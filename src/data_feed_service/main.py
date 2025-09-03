import os
import json
import time
import logging
from datetime import datetime
import argparse
from dotenv import load_dotenv

from ..common.events import MARKET_DATA_CHANNEL
from ..common.redis_client import RedisClient
from .live_feed import AlphaVantageDataFeed
from .csv_feed import CSVDataFeed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_feed_service')

load_dotenv()

def publish_ticks_to_redis(ticks_dict, redis_client=None): 
    if not redis_client: 
        redis_client = RedisClient.get_instance()

    for symbol, ticks in ticks_dict.items(): 
        for tick in ticks: 
            tick_data = {
                'type': 'tick',
                'symbol': tick.symbol,
                'price': tick.price,
                'timestamp': tick.timestamp,
                'date': datetime.fromtimestamp(tick.timestamp).strftime('%Y-%m-%d'),
                'open': tick.open_price,
                'high': tick.high_price,
                'low': tick.low_price,
                'volume': tick.volume
            }

            message = json.dumps(tick_data)
            redis_client.publish(MARKET_DATA_CHANNEL, message)
            logger.debug(f"Published: {message}")

def print_ticks(ticks_dict):
    for symbol, ticks in ticks_dict.items():
        logger.info(f"Data for {symbol} ({len(ticks)} data points):")
        
        # Print the most recent 5 ticks
        for tick in ticks[-5:]:
            date_str = datetime.fromtimestamp(tick.timestamp).strftime('%Y-%m-%d')
            print(f"{date_str} | {tick.symbol} | Price: ${tick.price:.2f} | " 
                  f"Open: ${tick.open_price:.2f} | High: ${tick.high_price:.2f} | "
                  f"Low: ${tick.low_price:.2f} | Volume: {tick.volume}")

def main(): 
    parser = argparse.ArgumentParser(description="Market Data Feed Service")
    parser.add_argument('--mode', choices=['live', 'csv', 'both'], default='live', 
        help='Data source mode: live(Alpha Vantage), csv (for backtesting), or both')
    parser.add_argument('--publish', action='store_true', 
        help='Publish data to Redis (default is just print to console)')
    parser.add_argument('--symbols', type=str, default='IBM,AAPL,MSFT',
        help='Comma-separated list of stock symbols to fetch data for')
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(',')]
    all_ticks = {}

    if args.mode in ['live', 'both']: 
        logger.info("Fetching live data from Alpha Vantage")
        live_feed = AlphaVantageDataFeed(symbols=symbols)
        live_ticks = live_feed.fetch_data()
        all_ticks.update(live_ticks)

    # CSV data for backtesting
    if args.mode in ['csv', 'both']:
        logger.info("Reading data from CSV files...")
        csv_dir = os.getenv('CSV_DATA_DIR', 'data')
        csv_files = {symbol: f"{csv_dir}/{symbol}.csv" for symbol in symbols}
        csv_feed = CSVDataFeed(csv_files=csv_files)
        csv_ticks = csv_feed.fetch_data()
        all_ticks.update(csv_ticks)
    
    # Print the ticks to console
    print_ticks(all_ticks)
    
    # Publish to Redis if requested
    if args.publish:
        logger.info("Publishing data to Redis...")
        publish_ticks_to_redis(all_ticks)
        logger.info("Data published to Redis channel")
    
if __name__ == "__main__":
    main()

        

