import logging
from collections import deque
from typing import Tuple

logger = logging.getLogger('sma_calculator')

class SMACalculator: 
    "Simple MA calc using deque algo for O(1) --> runnign window"

    def __init__(self, short_window: int = 50, long_window: int = 100): 
        self.short_window = short_window
        self.long_window = long_window

        self.short_prices = deque(maxlen = short_window)
        self.long_prices = deque(maxlen = long_window)

        self.short_sum = 0.0
        self.long_sum = 0.0

        #store last SMAs for crossover detecion
        self.prev_short_sma = None
        self.prev_long_sma = None

    def update(self, price: float) -> Tuple[float, float]: 
        # update SMA with new price when it comes from channel
        # returns tuple of (short_sma, long_sma)
        
        self.prev_short_sma = self.get_short_sma()
        self.prev_long_sma = self.get_long_sma()

        #update short window
        if len(self.short_prices) == self.short_window: 
            self.short_sum -= self.short_prices[0]

        self.short_prices.append(price)
        self.short_sum += price

        if len(self.long_prices) == self.long_window: 
            self.long_sum -= self.long_prices[0]

        self.long_prices.append(price)
        self.long_sum += price
        
        return self.get_short_sma(), self.get_long_sma()
        
    def get_short_sma(self) -> float:
        if not self.short_prices:
            return 0.0
        return self.short_sum / len(self.short_prices)
        
    def get_long_sma(self) -> float:
        if not self.long_prices:
            return 0.0
        return self.long_sum / len(self.long_prices)
    
    def detect_crossover(self) -> str:
        """
        Returns:
            'BUY' for golden cross (short crosses above long)
            'SELL' for death cross (short crosses below long)
            '' for no crossover
        """
        if self.prev_short_sma is None or self.prev_long_sma is None:
            return ''
            
        current_short_sma = self.get_short_sma()
        current_long_sma = self.get_long_sma()


        # Golden cross - short crosses above long
        if (self.prev_short_sma <= self.prev_long_sma and 
            current_short_sma > current_long_sma):
            return 'BUY'
            
        # Death cross - short crosses below long
        elif (self.prev_short_sma >= self.prev_long_sma and 
              current_short_sma < current_long_sma):
            return 'SELL'
            
        # No crossover
        return ''

