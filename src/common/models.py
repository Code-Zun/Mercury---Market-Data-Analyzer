from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid


@dataclass
class Tick:
    "Represents single price tick for symbol"
    symbol: str
    price: float
    timestamp: int
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[int] = None

@dataclass
class Signal:
    """Represents a trading signal"""
    symbol: str
    signal: str  # 'BUY' or 'SELL'
    timestamp: int
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Order:
    """Represents a trading order"""
    symbol : str
    side : str #either buy or sell
    quantity : int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    order_type : str = "MARKET" #default to market order
    price : Optional[float] = None # only for limit orders so make optional

    def __post_init__(self): 
        #validate all input fields
        if self.side not in ['BUY', 'SELL']:
            raise ValueError(f"Invalid order side: {self.side}. Must be 'BUY' or 'SELL'")
        
        # Validate quantity
        if self.quantity <= 0:
            raise ValueError(f"Invalid order quantity: {self.quantity}. Must be positive")
        
        # Validate order_type
        if self.order_type not in ['MARKET', 'LIMIT']:
            raise ValueError(f"Invalid order type: {self.order_type}. Must be 'MARKET' or 'LIMIT'")
        
        # Validate price for LIMIT orders
        if self.order_type == 'LIMIT' and self.price is None:
            raise ValueError("Limit orders must specify a price")
    
@dataclass
class Execution:
    """Represents an executed order"""
    order_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    pnl: float = 0.0

@dataclass
class Portfolio:
    """Represents a trading portfolio"""
    cash: float
    holdings: Dict[str, int] = field(default_factory=dict)  # symbol -> quantity
    trade_history: List[Execution] = field(default_factory=list)
    
    def update_after_execution(self, execution: Execution) -> None: 
        if execution.side == 'BUY': 
            cost = execution.price * execution.quantity
            self.cash -= cost

            if execution.symbol in self.holdings: 
                self.holdings[execution.symbol] += execution.quantity
            else: 
                self.holdings[execution.symbol] = execution.quantity

        elif execution.side == 'SELL': 
            proceeds = execution.price * execution.quantity
            self.cash += proceeds

            if execution.symbol in self.holdings: 
                self.holdings[execution.symbol] -= execution.quantity

                if self.holdings[execution.symbol] <= 0: 
                    del self.holdings[execution.symbol]
            else: 
                raise ValueError(f"Cannot sell {execution.symbol}: Not in Potfolio")
            
        self.trade_history.append(execution)

    def get_total_value(self, current_prices: Dict[str, float]) -> float:
         #current_prices is stock symbol, curr_price taken from Alpha
        
        missing = set(self.holdings) - set(current_prices)
        if missing:
            raise ValueError(f"Missing prices for: {', '.join(sorted(missing))}")

        holdings_value = sum(
            quantity * current_prices.get(symbol, 0)
            for symbol, quantity in self.holdings.items()
        )
        return self.cash + holdings_value