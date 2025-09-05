import unittest
from src.processing_service.sma_calculator import SMACalculator

class TestSMACalculator(unittest.TestCase):
    """Tests for the SMACalculator class"""
    
    def test_simple_sma_calculation(self):
        """Test basic SMA calculation with small window sizes"""
        # Create calculator with small window sizes for testing
        calc = SMACalculator(short_window=3, long_window=5)
        
        # Feed in prices one by one
        short_sma, long_sma = calc.update(10)
        self.assertEqual(short_sma, 10)  # 10/1
        self.assertEqual(long_sma, 10)   # 10/1
        
        short_sma, long_sma = calc.update(20)
        self.assertEqual(short_sma, 15)  # (10+20)/2
        self.assertEqual(long_sma, 15)   # (10+20)/2
        
        short_sma, long_sma = calc.update(30)
        self.assertEqual(short_sma, 20)  # (10+20+30)/3
        self.assertEqual(long_sma, 20)   # (10+20+30)/3
        
        # Now the short window is full, oldest value (10) gets dropped
        short_sma, long_sma = calc.update(40)
        self.assertEqual(short_sma, 30)  # (20+30+40)/3
        self.assertEqual(long_sma, 25)   # (10+20+30+40)/4
        
        short_sma, long_sma = calc.update(50)
        self.assertEqual(short_sma, 40)  # (30+40+50)/3
        self.assertEqual(long_sma, 30)   # (10+20+30+40+50)/5
        
        # Now both windows are full
        short_sma, long_sma = calc.update(60)
        self.assertEqual(short_sma, 50)  # (40+50+60)/3
        self.assertEqual(long_sma, 40)   # (20+30+40+50+60)/5
        
    def test_crossover_detection(self):
        """Test detection of golden and death crosses"""
        # Create calculator with small window sizes
        calc = SMACalculator(short_window=2, long_window=4)
        
        # No crossover initially (not enough data)
        calc.update(10)
        self.assertEqual(calc.detect_crossover(), '')
        
        # Setup for golden cross: short SMA will cross above long SMA
        calc.update(10)  # short_sma=10, long_sma=10
        self.assertEqual(calc.detect_crossover(), '')  # No crossover yet
        
        # When we feed this value, short SMA will rise above long SMA
        calc.update(20)  # short_sma=15, long_sma=13.33...
        self.assertEqual(calc.detect_crossover(), 'BUY')  # Golden cross detected
        
        # Setup for death cross: feed values to make short SMA cross below long SMA
        calc.update(5)   # short_sma=12.5, long_sma=11.25
        self.assertEqual(calc.detect_crossover(), '')  # No crossover yet
        
        calc.update(5)   # short_sma=5, long_sma=10
        self.assertEqual(calc.detect_crossover(), 'SELL')  # Death cross detected

if __name__ == "__main__":
    unittest.main()