import os
import time
import logging
from datetime import datetime
import requests
from dotenv import load_dotenv
from src.common.models import Tick

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('live_feed')

load_dotenv()

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'

class AlphaVantageDataFeed:
    def __init__(self, symbols=None, api_key=None):
        """
        Initialize the Alpha Vantage data feed
        
        Args:
            symbols: List of stock symbols to track
            api_key: Alpha Vantage API key
        """
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise ValueError("Alpha Vantage API key is required")
            
        self.symbols = symbols or ['IBM']
        self.backoff_time = 5  
        self.max_backoff = 60  

    def get_daily_data(self, symbol):
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact',  # Get the latest 100 data points
            'apikey': self.api_key
        }

        try:
            logger.info(f"Fetching data for {symbol}")
            response = requests.get(BASE_URL, params=params)
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = self.backoff_time
                logger.warning(f"Rate limited. Waiting for {wait_time} seconds before retrying.")
                time.sleep(wait_time)
                self.backoff_time = min(self.backoff_time * 2, self.max_backoff)
                return None
                
            # Reset backoff time if successful
            self.backoff_time = 1
            
            if response.status_code != 200:
                logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                return None
                
            data = response.json()
            
            # Validate the response structure
            if "Error Message" in data:
                logger.error(f"API returned an error: {data['Error Message']}")
                return None
                
            if "Time Series (Daily)" not in data:
                logger.error(f"Unexpected response format: {data}")
                return None
                
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
        
    def process_daily_data(self, data, symbol):
        """
        Process the daily data from Alpha Vantage and convert to our internal format
        
        Args:
            data: Raw data from Alpha Vantage API
            symbol: Stock symbol
            
        Returns:
            List of Tick objects
        """
        ticks = []
        
        if not data or "Time Series (Daily)" not in data:
            return ticks
            
        time_series = data["Time Series (Daily)"]
        
        for date_str, values in time_series.items():
            # Convert date string to timestamp
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            timestamp = int(date_obj.timestamp())
            
            try:
                open_price = float(values["1. open"])
                high_price = float(values["2. high"])
                low_price = float(values["3. low"])
                close_price = float(values["4. close"])
                volume = int(values["5. volume"])

                # Create a tick object
                tick = Tick(
                    symbol=symbol,
                    price=close_price,  # Use closing price as the main price
                    timestamp=timestamp,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    volume=volume
                )
                
                ticks.append(tick)
                
            except (KeyError, ValueError) as e:
                logger.warning(f"Error processing data point for {date_str}: {str(e)}")
                continue
                
        # Sort by timestamp (ascending)
        ticks.sort(key=lambda x: x.timestamp)
        return ticks
    
    def fetch_data(self):
        all_ticks = {}
        
        for symbol in self.symbols:
            data = self.get_daily_data(symbol)
            if not data:
                logger.warning(f"No data available for {symbol}")
                continue
                
            ticks = self.process_daily_data(data, symbol)
            
            if not ticks:
                logger.warning(f"No ticks extracted for {symbol}")
                continue
                
            logger.info(f"Processed {len(ticks)} ticks for {symbol}")
            all_ticks[symbol] = ticks
            
        return all_ticks