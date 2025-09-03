from dataclasses import dataclass
from typing import Dict, List, Optional, Any

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
    data: Optional[Dict[str, Any]] = None

@dataclass
class Order:
    """Represents a trading order"""
    id: str
    timestamp: int
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: int
    price: Optional[float] = None
    
@dataclass
class Execution:
    """Represents an executed order"""
    order_id: str
    timestamp: int
    symbol: str
    side: str
    quantity: int
    price: float
    pnl: float = 0.0

@dataclass
class Portfolio:
    """Represents a trading portfolio"""
    cash: float
    holdings: Dict[str, int]  # symbol -> quantity
    trade_history: Optional[List[Execution]] = None
    
    def __post_init__(self):
        if self.trade_history is None:
            self.trade_history = []

