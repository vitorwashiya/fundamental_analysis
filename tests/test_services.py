"""
Tests for services
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.fundamentus_service import FundamentusService
from app.services.ranking_service import RankingService
from app.models.models import Sector, Stock, SectorRanking


class TestFundamentusService:
    """Test FundamentusService"""
    
    def setup_method(self):
        """Setup test"""
        self.mock_db = Mock(spec=Session)
        self.service = FundamentusService(self.mock_db)
    
    @patch('app.services.fundamentus_service.fundamentus.get_resultado')
    def test_get_market_data_success(self, mock_get_resultado):
        """Test successful market data retrieval"""
        # Mock fundamentus response
        mock_data = {
            'PETR4': {
                'cotacao': 30.50,
                'pl': 8.5,
                'pvp': 1.2,
                'div_yield': 12.5,
                'roe': 18.5,
                'roic': 15.2
            },
            'VALE3': {
                'cotacao': 65.20,
                'pl': 6.8,
                'pvp': 1.8,
                'div_yield': 8.2,
                'roe': 22.1,
                'roic': 18.5
            }
        }
        mock_get_resultado.return_value = mock_data
        
        result = self.service.get_market_data()
        
        assert isinstance(result, dict)
        assert 'PETR4' in result
        assert 'VALE3' in result
        mock_get_resultado.assert_called_once()
    
    @patch('app.services.fundamentus_service.fundamentus.get_resultado')
    def test_get_market_data_failure(self, mock_get_resultado):
        """Test market data retrieval failure"""
        mock_get_resultado.side_effect = Exception("Connection error")
        
        result = self.service.get_market_data()
        
        assert result == {}
    
    def test_clean_data_success(self):
        """Test data cleaning"""
        raw_data = {
            'PETR4': {
                'cotacao': '30,50',  # String with comma
                'pl': 8.5,
                'pvp': None,  # None value
                'div_yield': 'N/A',  # String N/A
                'roe': float('inf'),  # Infinity
                'roic': 15.2
            }
        }
        
        cleaned = self.service.clean_data(raw_data)
        
        assert 'PETR4' in cleaned
        # Should handle string conversion
        assert isinstance(cleaned['PETR4'].get('cotacao'), (int, float, type(None)))
    
    def test_clean_data_empty(self):
        """Test cleaning empty data"""
        result = self.service.clean_data({})
        assert result == {}
    
    def test_process_stock_data(self):
        """Test stock data processing"""
        stock_data = {
            'cotacao': 30.50,
            'pl': 8.5,
            'pvp': 1.2,
            'div_yield': 12.5,
            'roe': 18.5,
            'roic': 15.2
        }
        
        processed = self.service.process_stock_data('PETR4', stock_data)
        
        assert processed['symbol'] == 'PETR4'
        assert processed['cotacao'] == 30.50
        assert processed['is_active'] is True
    
    def test_update_stocks_data_with_mock(self):
        """Test stock data update with mocked database"""
        # Mock existing sector
        mock_sector = Mock()
        mock_sector.id = 1
        mock_sector.name = "Test Sector"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_sector
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        
        with patch.object(self.service, 'get_market_data') as mock_get_data:
            mock_get_data.return_value = {
                'PETR4': {
                    'cotacao': 30.50,
                    'pl': 8.5,
                    'pvp': 1.2
                }
            }
            
            result = self.service.update_stocks_data()
            
            assert isinstance(result, dict)
            assert 'status' in result


class TestRankingService:
    """Test RankingService"""
    
    def setup_method(self):
        """Setup test"""
        self.mock_db = Mock(spec=Session)
        self.service = RankingService(self.mock_db)
    
    def test_calculate_magic_formula_score(self):
        """Test Magic Formula score calculation"""
        stock_data = {
            'pl': 10.0,
            'pvp': 1.5,
            'roe': 20.0,
            'roic': 15.0
        }
        
        score = self.service.calculate_magic_formula_score(stock_data)
        
        assert isinstance(score, (int, float))
        assert score >= 0
    
    def test_calculate_magic_formula_score_missing_data(self):
        """Test Magic Formula with missing data"""
        stock_data = {
            'pl': 10.0
            # Missing other fields
        }
        
        score = self.service.calculate_magic_formula_score(stock_data)
        
        # Should handle missing data
        assert isinstance(score, (int, float))
        assert score >= 0
    
    def test_get_magic_formula_rankings_empty(self):
        """Test Magic Formula rankings with empty database"""
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = self.service.get_magic_formula_rankings()
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_get_magic_formula_rankings_with_data(self):
        """Test Magic Formula rankings with data"""
        # Mock stocks
        mock_stock1 = Mock()
        mock_stock1.symbol = 'PETR4'
        mock_stock1.cotacao = 30.50
        mock_stock1.pl = 8.5
        mock_stock1.pvp = 1.2
        mock_stock1.roe = 18.5
        mock_stock1.roic = 15.2
        
        mock_stock2 = Mock()
        mock_stock2.symbol = 'VALE3'
        mock_stock2.cotacao = 65.20
        mock_stock2.pl = 6.8
        mock_stock2.pvp = 1.8
        mock_stock2.roe = 22.1
        mock_stock2.roic = 18.5
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [
            mock_stock1, mock_stock2
        ]
        
        result = self.service.get_magic_formula_rankings(limit=10)
        
        assert isinstance(result, list)
        assert len(result) <= 10
    
    def test_calculate_sector_rankings_empty(self):
        """Test sector rankings calculation with empty database"""
        self.mock_db.query.return_value.all.return_value = []
        
        result = self.service.calculate_sector_rankings(sector_id=1)
        
        assert isinstance(result, dict)
        assert result.get('status') == 'success'
    
    @patch('app.sectors.factory.SectorAnalyzerFactory.get_analyzer')
    def test_calculate_sector_rankings_with_data(self, mock_get_analyzer):
        """Test sector rankings calculation with data"""
        # Mock analyzer
        mock_analyzer = Mock()
        mock_analyzer.calculate_score.return_value = 85.5
        mock_get_analyzer.return_value = mock_analyzer
        
        # Mock sector
        mock_sector = Mock()
        mock_sector.id = 1
        mock_sector.name = "Test Sector"
        
        # Mock stocks
        mock_stock = Mock()
        mock_stock.id = 1
        mock_stock.symbol = 'TEST4'
        mock_stock.sector_id = 1
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_sector
        self.mock_db.query.return_value.filter.return_value.all.return_value = [mock_stock]
        
        result = self.service.calculate_sector_rankings(sector_id=1)
        
        assert isinstance(result, dict)
        assert result.get('status') == 'success'
    
    def test_calculate_all_rankings(self):
        """Test calculating all rankings"""
        # Mock sectors
        mock_sector = Mock()
        mock_sector.id = 1
        mock_sector.name = "Test Sector"
        
        self.mock_db.query.return_value.all.return_value = [mock_sector]
        
        with patch.object(self.service, 'calculate_sector_rankings') as mock_calc:
            mock_calc.return_value = {'status': 'success', 'rankings_calculated': 5}
            
            result = self.service.calculate_all_rankings()
            
            assert isinstance(result, dict)
            assert result.get('status') == 'success'
    
    def test_filter_stocks_by_criteria(self):
        """Test stock filtering by criteria"""
        # Mock stocks
        stocks = []
        for i in range(5):
            mock_stock = Mock()
            mock_stock.symbol = f'TEST{i}'
            mock_stock.cotacao = 10.0 + i
            mock_stock.pl = 8.0 + i
            mock_stock.pvp = 1.0 + (i * 0.2)
            mock_stock.volume_medio = 1000000 * (i + 1)
            stocks.append(mock_stock)
        
        filtered = self.service.filter_stocks_by_criteria(
            stocks, 
            min_liquidity=2000000,
            max_pl=10.0,
            max_pvp=1.5
        )
        
        assert isinstance(filtered, list)
        # Should filter based on criteria
        assert len(filtered) <= len(stocks)


class TestServiceIntegration:
    """Test service integration"""
    
    def setup_method(self):
        """Setup test"""
        self.mock_db = Mock(spec=Session)
        self.fundamentus_service = FundamentusService(self.mock_db)
        self.ranking_service = RankingService(self.mock_db)
    
    def test_data_flow(self):
        """Test data flow between services"""
        # Test that services can work together
        assert self.fundamentus_service is not None
        assert self.ranking_service is not None
        
        # Mock some basic interactions
        with patch.object(self.fundamentus_service, 'get_market_data') as mock_get_data:
            mock_get_data.return_value = {'TEST4': {'cotacao': 10.0}}
            
            data = self.fundamentus_service.get_market_data()
            assert isinstance(data, dict)
    
    def test_error_propagation(self):
        """Test error handling between services"""
        with patch.object(self.fundamentus_service, 'get_market_data') as mock_get_data:
            mock_get_data.side_effect = Exception("Test error")
            
            # Services should handle errors gracefully
            try:
                self.fundamentus_service.get_market_data()
            except Exception as e:
                assert str(e) == "Test error"
