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

