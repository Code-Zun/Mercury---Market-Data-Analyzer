import unittest
from src.common.models import Order, Portfolio
from src.exchange_service.simulated_exchange import SimulatedExchange

class TestSimulatedExchange(unittest.TestCase):
    """Tests for the SimulatedExchange class"""
    
    def setUp(self):
        """Set up a fresh exchange and portfolio for each test"""
        self.portfolio = Portfolio(cash=10000.0)
        self.exchange = SimulatedExchange(portfolio=self.portfolio)
        
        # Set some market prices
        self.exchange.update_market_price("AAPL", 150.0)
        self.exchange.update_market_price("MSFT", 250.0)
        self.exchange.update_market_price("GOOG", 2000.0)
        
    def test_buy_order(self):
        """Test buying shares"""
        # Create a buy order for AAPL
        order = Order(symbol="AAPL", side="BUY", quantity=10)
        
        # Execute the order
        execution = self.exchange.execute_order(order)
        
        # Verify the execution
        self.assertIsNotNone(execution)

        # Type assertion for Pylance
        assert execution is not None

        self.assertEqual(execution.symbol, "AAPL")
        self.assertEqual(execution.side, "BUY")
        self.assertEqual(execution.quantity, 10)
        self.assertEqual(execution.price, 150.0)
        
        # Verify portfolio was updated correctly
        self.assertEqual(self.portfolio.cash, 8500.0)  # 10000 - (10 * 150)
        self.assertEqual(self.portfolio.holdings["AAPL"], 10)
        self.assertEqual(len(self.portfolio.trade_history), 1)
        
    def test_sell_order(self):
        """Test selling shares"""
        # First buy some shares
        buy_order = Order(symbol="MSFT", side="BUY", quantity=5)
        self.exchange.execute_order(buy_order)
        
        # Then sell some shares
        sell_order = Order(symbol="MSFT", side="SELL", quantity=3)
        execution = self.exchange.execute_order(sell_order)
        
        # Verify the execution
        self.assertIsNotNone(execution)

        # Type assertion for Pylance
        assert execution is not None
        
        self.assertEqual(execution.symbol, "MSFT")
        self.assertEqual(execution.side, "SELL")
        self.assertEqual(execution.quantity, 3)
        
        # Verify portfolio was updated correctly
        expected_cash = 10000 - (5 * 250) + (3 * 250)  # Initial - buy + sell
        self.assertEqual(self.portfolio.cash, expected_cash)
        self.assertEqual(self.portfolio.holdings["MSFT"], 2)  # 5 bought - 3 sold
        self.assertEqual(len(self.portfolio.trade_history), 2)
    
    def test_insufficient_cash(self):
        """Test buying with insufficient cash"""
        # Try to buy more than we can afford
        expensive_order = Order(symbol="GOOG", side="BUY", quantity=100)  # 100 * 2000 > 10000
        
        # Execute the order - should fail
        execution = self.exchange.execute_order(expensive_order)
        
        # Verify no execution occurred
        self.assertIsNone(execution)
        
        # Verify portfolio remains unchanged
        self.assertEqual(self.portfolio.cash, 10000.0)
        self.assertEqual(len(self.portfolio.holdings), 0)
        self.assertEqual(len(self.portfolio.trade_history), 0)
    
    def test_insufficient_shares(self):
        """Test selling with insufficient shares"""
        # Try to sell shares we don't have
        sell_order = Order(symbol="AAPL", side="SELL", quantity=10)
        
        # Execute the order - should fail
        execution = self.exchange.execute_order(sell_order)
        
        # Verify no execution occurred
        self.assertIsNone(execution)
        
        # Verify portfolio remains unchanged
        self.assertEqual(self.portfolio.cash, 10000.0)
        self.assertEqual(len(self.portfolio.holdings), 0)
        self.assertEqual(len(self.portfolio.trade_history), 0)
    
    def test_unknown_symbol(self):
        """Test order for a symbol with no price"""
        # Create order for a symbol we don't have a price for
        order = Order(symbol="UNKNOWN", side="BUY", quantity=10)
        
        # Execute the order - should fail
        execution = self.exchange.execute_order(order)
        
        # Verify no execution occurred
        self.assertIsNone(execution)

if __name__ == "__main__":
    unittest.main()