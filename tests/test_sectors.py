"""
Tests for sector analyzers
"""
import pytest
from unittest.mock import Mock

from app.sectors.base import BaseSectorAnalyzer
from app.sectors.financeiro import FinanceiroAnalyzer
from app.sectors.utilities import UtilitiesAnalyzer
from app.sectors.consumo_ciclico import ConsumoCiclicoAnalyzer
from app.sectors.factory import SectorAnalyzerFactory


class TestBaseSectorAnalyzer:
    """Test base sector analyzer"""
    
    def test_abstract_methods(self):
        """Test that base analyzer cannot be instantiated"""
        with pytest.raises(TypeError):
            BaseSectorAnalyzer()


class TestFinanceiroAnalyzer:
    """Test financial sector analyzer"""
    
    def setup_method(self):
        """Setup test"""
        self.analyzer = FinanceiroAnalyzer()
    
    def test_calculate_score_complete_data(self):
        """Test score calculation with complete data"""
        stock_data = {
            'pl': 8.0,
            'pvp': 1.2,
            'div_yield': 10.0,
            'roe': 20.0,
            'roic': 15.0,
            'margem_liquida': 25.0,
            'liquidez_corrente': 1.5
        }
        
        score = self.analyzer.calculate_score(stock_data)
        
        assert isinstance(score, (int, float))
        assert score >= 0
        assert score <= 100
    
    def test_calculate_score_missing_data(self):
        """Test score calculation with missing data"""
        stock_data = {
            'pl': 8.0,
            'pvp': 1.2,
            # Missing other fields
        }
        
        score = self.analyzer.calculate_score(stock_data)
        
        # Should handle missing data gracefully
        assert isinstance(score, (int, float))
        assert score >= 0
    
    def test_calculate_score_invalid_data(self):
        """Test score calculation with invalid data"""
        stock_data = {
            'pl': -5.0,  # Invalid P/L
            'pvp': 0.0,  # Invalid P/VP
            'div_yield': None,  # None value
        }
        
        score = self.analyzer.calculate_score(stock_data)
        
        # Should handle invalid data
        assert isinstance(score, (int, float))
        assert score >= 0
    
    def test_financial_specific_indicators(self):
        """Test financial sector specific indicators"""
        stock_data = {
            'pl': 12.0,
            'pvp': 1.5,
            'div_yield': 8.0,
            'roe': 15.0,
            'roic': 12.0,
            'margem_liquida': 20.0,
            'liquidez_corrente': 1.8
        }
        
        score = self.analyzer.calculate_score(stock_data)
        
        # Financial sector should weight these indicators appropriately
        assert score > 0


class TestUtilitiesAnalyzer:
    """Test utilities sector analyzer"""
    
    def setup_method(self):
        """Setup test"""
        self.analyzer = UtilitiesAnalyzer()
    
    def test_utilities_scoring(self):
        """Test utilities sector scoring"""
        stock_data = {
            'pl': 15.0,
            'pvp': 2.0,
            'div_yield': 6.0,
            'roe': 12.0,
            'roic': 10.0,
            'receita_liquida': 1000000,
            'divida_liquida': 500000
        }
        
        score = self.analyzer.calculate_score(stock_data)
        
        assert isinstance(score, (int, float))
        assert score >= 0
        assert score <= 100
    
    def test_utilities_dividend_focus(self):
        """Test utilities sector dividend focus"""
        high_dividend_stock = {
            'pl': 18.0,
            'pvp': 2.2,
            'div_yield': 8.0,  # High dividend yield
            'roe': 10.0,
            'roic': 8.0
        }
        
        low_dividend_stock = {
            'pl': 18.0,
            'pvp': 2.2,
            'div_yield': 2.0,  # Low dividend yield
            'roe': 10.0,
            'roic': 8.0
        }
        
        high_score = self.analyzer.calculate_score(high_dividend_stock)
        low_score = self.analyzer.calculate_score(low_dividend_stock)
        
        # Utilities should favor higher dividend yields
        assert high_score > low_score


class TestConsumoCiclicoAnalyzer:
    """Test cyclical consumer sector analyzer"""
    
    def setup_method(self):
        """Setup test"""
        self.analyzer = ConsumoCiclicoAnalyzer()
    
    def test_growth_focus(self):
        """Test cyclical consumer growth focus"""
        stock_data = {
            'pl': 20.0,
            'pvp': 3.0,
            'roe': 25.0,  # High ROE
            'roic': 20.0,  # High ROIC
            'crescimento_receita': 15.0,  # High growth
            'margem_liquida': 8.0
        }
        
        score = self.analyzer.calculate_score(stock_data)
        
        assert isinstance(score, (int, float))
        assert score >= 0


class TestSectorAnalyzerFactory:
    """Test sector analyzer factory"""
    
    def test_get_analyzer_financeiro(self):
        """Test getting financial analyzer"""
        analyzer = SectorAnalyzerFactory.get_analyzer("Financeiro")
        assert isinstance(analyzer, FinanceiroAnalyzer)
    
    def test_get_analyzer_utilities(self):
        """Test getting utilities analyzer"""
        analyzer = SectorAnalyzerFactory.get_analyzer("Utilities")
        assert isinstance(analyzer, UtilitiesAnalyzer)
    
    def test_get_analyzer_consumo_ciclico(self):
        """Test getting cyclical consumer analyzer"""
        analyzer = SectorAnalyzerFactory.get_analyzer("Consumo Cíclico")
        assert isinstance(analyzer, ConsumoCiclicoAnalyzer)
    
    def test_get_analyzer_unknown_sector(self):
        """Test getting analyzer for unknown sector"""
        analyzer = SectorAnalyzerFactory.get_analyzer("Unknown Sector")
        
        # Should return a default analyzer or handle gracefully
        assert analyzer is not None
    
    def test_get_available_sectors(self):
        """Test getting list of available sectors"""
        sectors = SectorAnalyzerFactory.get_available_sectors()
        
        assert isinstance(sectors, list)
        assert len(sectors) > 0
        assert "Financeiro" in sectors
        assert "Utilities" in sectors
    
    def test_case_insensitive_lookup(self):
        """Test case insensitive sector lookup"""
        analyzer1 = SectorAnalyzerFactory.get_analyzer("financeiro")
        analyzer2 = SectorAnalyzerFactory.get_analyzer("FINANCEIRO")
        analyzer3 = SectorAnalyzerFactory.get_analyzer("Financeiro")
        
        assert type(analyzer1) == type(analyzer2) == type(analyzer3)


class TestAnalyzerConsistency:
    """Test consistency across analyzers"""
    
    def test_all_analyzers_return_valid_scores(self):
        """Test that all analyzers return valid scores"""
        test_data = {
            'pl': 15.0,
            'pvp': 2.0,
            'div_yield': 5.0,
            'roe': 15.0,
            'roic': 12.0,
            'margem_liquida': 10.0
        }
        
        sectors = SectorAnalyzerFactory.get_available_sectors()
        
        for sector in sectors:
            analyzer = SectorAnalyzerFactory.get_analyzer(sector)
            score = analyzer.calculate_score(test_data)
            
            assert isinstance(score, (int, float))
            assert score >= 0
            assert score <= 100
    
    def test_empty_data_handling(self):
        """Test that all analyzers handle empty data"""
        empty_data = {}
        
        sectors = SectorAnalyzerFactory.get_available_sectors()
        
        for sector in sectors:
            analyzer = SectorAnalyzerFactory.get_analyzer(sector)
            score = analyzer.calculate_score(empty_data)
            
            # Should handle empty data without crashing
            assert isinstance(score, (int, float))
            assert score >= 0
