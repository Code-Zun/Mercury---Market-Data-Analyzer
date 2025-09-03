import csv
import os
import logging
from datetime import datetime
from src.common.models import Tick

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('csv_feed')

class CSVDataFeed:
    """
    Data feed that reads historical data from CSV files for backtesting
    Expected CSV format:
    date,open,high,low,close,volume
    2025-08-29,245.23,245.46,241.72,243.49,2967558
    """
    
    def __init__(self, csv_files=None):
        """
        Initialize the CSV data feed
        
        Args:
            csv_files: Dict mapping symbol to CSV file path
                       e.g. {'IBM': 'data/IBM.csv'}
        """
        self.csv_files = csv_files or {}
        
    def read_csv_data(self, symbol, file_path):
        """
        Read historical data from a CSV file
        
        Args:
            symbol: Stock symbol (e.g., 'IBM')
            file_path: Path to the CSV file
            
        Returns:
            List of Tick objects
        """
        ticks = []
        
        if not os.path.exists(file_path):
            logger.error(f"CSV file not found: {file_path}")
            return ticks
            
        try:
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        # Parse the date
                        date_obj = datetime.strptime(row['date'], "%Y-%m-%d")
                        timestamp = int(date_obj.timestamp())
                        
                        # Create a tick object
                        tick = Tick(
                            symbol=symbol,
                            price=float(row['close']),  # Use closing price as the main price
                            timestamp=timestamp,
                            open_price=float(row['open']),
                            high_price=float(row['high']),
                            low_price=float(row['low']),
                            volume=int(row['volume'])
                        )
                        
                        ticks.append(tick)
                        
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Error processing row {row}: {str(e)}")
                        continue
                        
            # Sort by timestamp (ascending)
            ticks.sort(key=lambda x: x.timestamp)
            return ticks
            
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {str(e)}")
            return ticks
            
    def fetch_data(self):
        """
        Fetch and process data from all configured CSV files
        
        Returns:
            Dictionary of symbol -> list of Tick objects
        """
        all_ticks = {}
        
        for symbol, file_path in self.csv_files.items():
            ticks = self.read_csv_data(symbol, file_path)
            
            if not ticks:
                logger.warning(f"No ticks extracted for {symbol} from {file_path}")
                continue
                
            logger.info(f"Processed {len(ticks)} ticks for {symbol} from {file_path}")
            all_ticks[symbol] = ticks
            
        return all_ticks