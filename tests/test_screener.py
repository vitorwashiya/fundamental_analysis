"""
Tests for the fundamental analysis screener.
"""
import unittest
from src.fundamental_screener import FundamentalScreener, Sector, ScreeningCriteria
from src.fundamental_screener.data_provider import MockDataProvider


class TestFundamentalScreener(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.screener = FundamentalScreener(use_mock_data=True)
        self.mock_provider = MockDataProvider()
    
    def test_initialization(self):
        """Test screener initialization."""
        self.assertIsNotNone(self.screener)
        self.assertIsInstance(self.screener.data_provider, MockDataProvider)
    
    def test_mock_data_provider(self):
        """Test mock data provider."""
        stocks = self.mock_provider.get_stock_data()
        self.assertEqual(len(stocks), 5)
        
        # Test specific stock
        itub_stocks = self.mock_provider.get_stock_data("ITUB4")
        self.assertEqual(len(itub_stocks), 1)
        self.assertEqual(itub_stocks[0].symbol, "ITUB4")
    
    def test_sector_screening(self):
        """Test sector-specific screening."""
        # Test banking sector
        bank_results = self.screener.screen_sector(Sector.FINANCEIROS)
        self.assertGreater(len(bank_results), 0)
        
        # All results should be from banking sector
        for result in bank_results:
            self.assertEqual(result.stock.sector, Sector.FINANCEIROS)
    
    def test_top_opportunities(self):
        """Test getting top opportunities."""
        top_results = self.screener.get_top_opportunities(max_results=3)
        self.assertLessEqual(len(top_results), 3)
        
        # Results should be sorted by score (descending)
        if len(top_results) > 1:
            for i in range(len(top_results) - 1):
                self.assertGreaterEqual(top_results[i].score, top_results[i + 1].score)
    
    def test_custom_criteria(self):
        """Test custom screening criteria."""
        # Strict criteria that should filter out most stocks
        strict_criteria = ScreeningCriteria(
            pl_max=8.0,
            roe_min=0.22
        )
        
        results = self.screener.get_top_opportunities(
            max_results=10, 
            additional_criteria=strict_criteria
        )
        
        # Should have fewer results due to strict criteria
        for result in results:
            stock = result.stock
            if stock.pl:
                self.assertLessEqual(stock.pl, 8.0)
            if stock.roe:
                self.assertGreaterEqual(stock.roe, 0.22)
    
    def test_specific_stock_analysis(self):
        """Test analysis of specific stock."""
        result = self.screener.analyze_specific_stock("ITUB4")
        self.assertIsNotNone(result)
        self.assertEqual(result.stock.symbol, "ITUB4")
        self.assertGreater(result.score, 0)
        
        # Test non-existent stock
        result = self.screener.analyze_specific_stock("INVALID")
        self.assertIsNone(result)
    
    def test_screening_criteria_merge(self):
        """Test that criteria merging works correctly."""
        # Get banking screener
        bank_screener = self.screener.sector_screeners[Sector.FINANCEIROS]
        
        # Test with additional criteria
        additional = ScreeningCriteria(pl_max=6.0, roe_min=0.20)
        
        results = bank_screener.screen_stocks(additional)
        
        # Should apply the more restrictive criteria
        for result in results:
            stock = result.stock
            if stock.pl:
                self.assertLessEqual(stock.pl, 6.0)  # More restrictive than bank default
            if stock.roe:
                self.assertGreaterEqual(stock.roe, 0.20)  # More restrictive than bank default


if __name__ == '__main__':
    unittest.main()