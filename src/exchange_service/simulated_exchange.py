import logging
from src.common.models import Portfolio, Order, Execution
from typing import Optional, Dict

logger = logging.getLogger('simulated_exchange')

class SimulatedExchange: 
    " All orders immediately at current market price"
    def __init__(self, portfolio: Optional[Portfolio]) -> None:
        self.portfolio = portfolio or Portfolio(cash=10000.0)
        self.latest_prices : Dict[str, float] = {} #stock -> price

    def update_market_price(self, symbol : str, price : float) -> None: 
        self.latest_prices[symbol] = price

    def execute_order(self, order: Order) -> Optional[Execution]: 
        symbol = order.symbol

        if symbol not in self.latest_prices: 
            logger.error(f"Can't execute order: no price available for {symbol}")
            return None
    
        current_price = self.latest_prices[symbol]

        if order.side == 'SELL': 
            if symbol not in self.portfolio.holdings or self.portfolio.holdings[symbol] <= order.quantity:
                logger.error(f"Cannot execute SELL order: insufficient shares of {symbol}")
                return None
        
        if order.side == 'BUY': 
            cost = current_price * order.quantity
            if self.portfolio.cash < cost: 
                logger.error("Cannot execut BUY order: insufficient cash")
                return None
            
        #successful order, create execution recordd and publish to redis

        execution = Execution(
            order_id= order.id, 
            symbol=order.symbol, 
            side=order.side, 
            quantity=order.quantity,
            price=current_price
        )

        #update portfolio
        # Update portfolio
        try:
            self.portfolio.update_after_execution(execution)
            logger.info(f"Executed {order.side} order for {order.quantity} shares of {symbol} at ${current_price:.2f}")
            return execution
        except ValueError as e:
            logger.error(f"Failed to update portfolio: {e}")
            return None