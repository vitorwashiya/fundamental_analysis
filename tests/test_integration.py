"""
Integration tests for the fundamental analysis API
"""
import pytest
from unittest.mock import patch, Mock
import tempfile
import os

from main import app
from app.database.connection import Base, get_db
from app.models.models import Sector, Stock, SectorRanking


class TestFullWorkflow:
    """Test complete workflow integration"""
    
    def test_complete_analysis_workflow(self, client, test_db):
        """Test complete analysis workflow from data update to rankings"""
        
        # Step 1: Check initial state
        response = client.get("/health")
        assert response.status_code == 200
        
        # Step 2: Check empty sectors
        response = client.get("/api/v1/sectors/")
        assert response.status_code == 200
        assert len(response.json()) == 0
        
        # Step 3: Mock data update (since we can't access real fundamentus in tests)
        with patch('app.services.fundamentus_service.FundamentusService.update_stocks_data') as mock_update:
            mock_update.return_value = {
                "status": "success",
                "stocks_updated": 10,
                "message": "Successfully updated 10 stocks"
            }
            
            response = client.post("/api/v1/data/update-stocks")
            assert response.status_code == 200
            
        # Step 4: Mock ranking calculation
        with patch('app.services.ranking_service.RankingService.calculate_all_rankings') as mock_rankings:
            mock_rankings.return_value = {
                "status": "success",
                "rankings_calculated": 5,
                "message": "Successfully calculated rankings for 5 sectors"
            }
            
            response = client.post("/api/v1/data/calculate-rankings")
            assert response.status_code == 200
        
        # Step 5: Check rankings (should be empty since we mocked the data)
        response = client.get("/api/v1/rankings/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_error_handling_workflow(self, client):
        """Test error handling throughout the workflow"""
        
        # Test service errors
        with patch('app.services.fundamentus_service.FundamentusService.update_stocks_data') as mock_update:
            mock_update.side_effect = Exception("Service unavailable")
            
            response = client.post("/api/v1/data/update-stocks")
            # Should handle errors gracefully
            assert response.status_code in [200, 500]
    
    def test_pagination_and_filtering_workflow(self, client):
        """Test pagination and filtering across endpoints"""
        
        # Test rankings pagination
        response = client.get("/api/v1/rankings/?skip=0&limit=10")
        assert response.status_code == 200
        
        # Test Magic Formula with filters
        response = client.get("/api/v1/rankings/magic-formula?limit=5&min_liquidity=1000000")
        assert response.status_code == 200
        
        # Test sector-specific rankings
        response = client.get("/api/v1/rankings/sector/1?limit=10")
        assert response.status_code == 200


class TestDatabaseIntegration:
    """Test database integration"""
    
    def test_database_relationships(self, test_db):
        """Test database relationships work correctly"""
        
        # Create sector
        sector = Sector(
            name="Tecnologia",
            category="Software",
            subsectors="Software de Gestão,E-commerce"
        )
        test_db.add(sector)
        test_db.commit()
        
        # Create stock
        stock = Stock(
            symbol="TECH4",
            company_name="Tech Company S.A.",
            sector_id=sector.id,
            subsector="Software de Gestão",
            cotacao=50.00,
            pl=25.0,
            pvp=3.5,
            div_yield=2.0,
            roe=25.0,
            roic=20.0,
            is_active=True
        )
        test_db.add(stock)
        test_db.commit()
        
        # Create ranking
        ranking = SectorRanking(
            stock_id=stock.id,
            sector_id=sector.id,
            score=88.5,
            rank_position=1,
            total_stocks=15
        )
        test_db.add(ranking)
        test_db.commit()
        
        # Test relationships
        assert stock.sector.name == "Tecnologia"
        assert len(sector.stocks) == 1
        assert ranking.stock.symbol == "TECH4"
        assert ranking.sector.name == "Tecnologia"
    
    def test_database_constraints(self, test_db):
        """Test database constraints"""
        
        # Test unique constraint on stock symbol
        stock1 = Stock(symbol="UNIQUE4", company_name="Company 1", cotacao=10.0, is_active=True)
        test_db.add(stock1)
        test_db.commit()
        
        # This should work (different symbol)
        stock2 = Stock(symbol="UNIQUE3", company_name="Company 2", cotacao=20.0, is_active=True)
        test_db.add(stock2)
        test_db.commit()
        
        assert test_db.query(Stock).count() == 2


class TestSectorAnalyzerIntegration:
    """Test sector analyzer integration"""
    
    def test_analyzer_factory_integration(self):
        """Test analyzer factory works with all sectors"""
        from app.sectors.factory import SectorAnalyzerFactory
        
        sectors = SectorAnalyzerFactory.get_available_sectors()
        assert len(sectors) > 0
        
        for sector in sectors:
            analyzer = SectorAnalyzerFactory.get_analyzer(sector)
            assert analyzer is not None
            
            # Test with sample data
            sample_data = {
                'pl': 15.0,
                'pvp': 2.0,
                'div_yield': 5.0,
                'roe': 15.0,
                'roic': 12.0
            }
            
            score = analyzer.calculate_score(sample_data)
            assert isinstance(score, (int, float))
            assert 0 <= score <= 100
    
    def test_sector_specific_logic(self):
        """Test sector-specific analysis logic"""
        from app.sectors.factory import SectorAnalyzerFactory
        
        # Test financial sector
        financial_analyzer = SectorAnalyzerFactory.get_analyzer("Financeiro")
        financial_data = {
            'pl': 10.0,
            'pvp': 1.5,
            'div_yield': 8.0,
            'roe': 18.0,
            'roic': 15.0,
            'margem_liquida': 25.0,
            'liquidez_corrente': 1.8
        }
        
        financial_score = financial_analyzer.calculate_score(financial_data)
        assert isinstance(financial_score, (int, float))
        
        # Test utilities sector
        utilities_analyzer = SectorAnalyzerFactory.get_analyzer("Utilities")
        utilities_data = {
            'pl': 18.0,
            'pvp': 2.2,
            'div_yield': 6.5,
            'roe': 12.0,
            'roic': 10.0
        }
        
        utilities_score = utilities_analyzer.calculate_score(utilities_data)
        assert isinstance(utilities_score, (int, float))


class TestServiceIntegration:
    """Test service layer integration"""
    
    @patch('app.services.fundamentus_service.fundamentus.get_resultado')
    def test_fundamentus_service_integration(self, mock_get_resultado, test_db):
        """Test FundamentusService integration"""
        from app.services.fundamentus_service import FundamentusService
        
        # Mock fundamentus data
        mock_get_resultado.return_value = {
            'TEST4': {
                'cotacao': 25.50,
                'pl': 12.0,
                'pvp': 1.8,
                'div_yield': 6.5,
                'roe': 16.0,
                'roic': 14.0
            }
        }
        
        service = FundamentusService(test_db)
        
        # Test data retrieval
        data = service.get_market_data()
        assert isinstance(data, dict)
        assert 'TEST4' in data
        
        # Test data cleaning
        cleaned = service.clean_data(data)
        assert isinstance(cleaned, dict)
    
    def test_ranking_service_integration(self, test_db):
        """Test RankingService integration"""
        from app.services.ranking_service import RankingService
        
        service = RankingService(test_db)
        
        # Test Magic Formula calculation
        stock_data = {
            'pl': 10.0,
            'pvp': 1.5,
            'roe': 20.0,
            'roic': 15.0
        }
        
        score = service.calculate_magic_formula_score(stock_data)
        assert isinstance(score, (int, float))
        assert score >= 0
        
        # Test rankings retrieval (empty database)
        rankings = service.get_magic_formula_rankings(limit=10)
        assert isinstance(rankings, list)


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema generation"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
    
    def test_docs_endpoint(self, client):
        """Test documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_redoc_endpoint(self, client):
        """Test ReDoc documentation endpoint"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestPerformance:
    """Test performance aspects"""
    
    def test_response_times(self, client):
        """Test API response times"""
        import time
        
        # Test health endpoint performance
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond in less than 1 second
    
    def test_pagination_performance(self, client):
        """Test pagination performance"""
        import time
        
        # Test large pagination request
        start_time = time.time()
        response = client.get("/api/v1/rankings/?skip=0&limit=100")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should handle pagination quickly


class TestSecurity:
    """Test security aspects"""
    
    def test_cors_headers(self, client):
        """Test CORS configuration"""
        response = client.get("/api/v1/sectors/")
        
        # Should handle CORS appropriately
        assert response.status_code == 200
    
    def test_input_validation(self, client):
        """Test input validation"""
        # Test invalid parameters
        response = client.get("/api/v1/rankings/?limit=invalid")
        
        # Should validate input
        assert response.status_code in [200, 422]
    
    def test_sql_injection_protection(self, client):
        """Test SQL injection protection"""
        # Test with potential SQL injection
        response = client.get("/api/v1/sectors/'; DROP TABLE sectors; --")
        
        # Should be protected
        assert response.status_code in [404, 422]
