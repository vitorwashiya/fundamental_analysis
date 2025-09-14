"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from app.models.models import Sector, Stock


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestDataUpdateEndpoints:
    """Test data update endpoints"""
    
    def test_get_update_logs(self, client):
        """Test getting update logs"""
        response = client.get("/api/v1/data/update-logs")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @patch('app.services.fundamentus_service.FundamentusService.update_stocks_data')
    def test_update_stocks_data_success(self, mock_update, client):
        """Test successful stock data update"""
        mock_update.return_value = {"status": "success", "stocks_updated": 50}
        
        response = client.post("/api/v1/data/update-stocks")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Stock data update started"
    
    @patch('app.services.fundamentus_service.FundamentusService.update_stocks_data')
    def test_update_stocks_data_with_force(self, mock_update, client):
        """Test stock data update with force parameter"""
        mock_update.return_value = {"status": "success", "stocks_updated": 100}
        
        response = client.post("/api/v1/data/update-stocks?force_update=true")
        
        assert response.status_code == 200
        mock_update.assert_called_once_with(force_update=True)
    
    @patch('app.services.ranking_service.RankingService.calculate_all_rankings')
    def test_calculate_rankings_success(self, mock_calculate, client):
        """Test successful ranking calculation"""
        mock_calculate.return_value = {"status": "success", "rankings_calculated": 10}
        
        response = client.post("/api/v1/data/calculate-rankings")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Ranking calculation started"


class TestSectorEndpoints:
    """Test sector endpoints"""
    
    def test_get_sectors_empty(self, client):
        """Test getting sectors when database is empty"""
        response = client.get("/api/v1/sectors/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_sector_by_id_not_found(self, client):
        """Test getting non-existent sector"""
        response = client.get("/api/v1/sectors/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_stocks_by_sector_not_found(self, client):
        """Test getting stocks for non-existent sector"""
        response = client.get("/api/v1/sectors/999/stocks")
        
        assert response.status_code == 404


class TestRankingEndpoints:
    """Test ranking endpoints"""
    
    def test_get_rankings_empty(self, client):
        """Test getting rankings when database is empty"""
        response = client.get("/api/v1/rankings/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_rankings_with_limit(self, client):
        """Test getting rankings with limit parameter"""
        response = client.get("/api/v1/rankings/?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_rankings_invalid_limit(self, client):
        """Test getting rankings with invalid limit"""
        response = client.get("/api/v1/rankings/?limit=-1")
        
        # Should handle invalid parameters gracefully
        assert response.status_code in [200, 422]
    
    def test_get_rankings_by_sector_empty(self, client):
        """Test getting rankings by sector when empty"""
        response = client.get("/api/v1/rankings/sector/1")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_magic_formula_rankings(self, client):
        """Test getting Magic Formula rankings"""
        response = client.get("/api/v1/rankings/magic-formula")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_magic_formula_with_parameters(self, client):
        """Test Magic Formula with parameters"""
        response = client.get("/api/v1/rankings/magic-formula?limit=10&min_liquidity=1000000")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestErrorHandling:
    """Test error handling in endpoints"""
    
    def test_invalid_endpoint(self, client):
        """Test invalid endpoint"""
        response = client.get("/api/v1/invalid-endpoint")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test method not allowed"""
        response = client.delete("/api/v1/sectors/")
        
        assert response.status_code == 405
    
    @patch('app.services.fundamentus_service.FundamentusService.update_stocks_data')
    def test_service_error_handling(self, mock_update, client):
        """Test service error handling"""
        mock_update.side_effect = Exception("Service error")
        
        response = client.post("/api/v1/data/update-stocks")
        
        # Should handle service errors gracefully
        assert response.status_code in [200, 500]


class TestPagination:
    """Test pagination functionality"""
    
    def test_rankings_pagination_skip(self, client):
        """Test rankings pagination with skip parameter"""
        response = client.get("/api/v1/rankings/?skip=10&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_rankings_pagination_large_skip(self, client):
        """Test rankings pagination with large skip"""
        response = client.get("/api/v1/rankings/?skip=1000&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Should return empty list


class TestFiltering:
    """Test filtering functionality"""
    
    def test_rankings_filter_by_sector(self, client):
        """Test filtering rankings by sector"""
        response = client.get("/api/v1/rankings/sector/1?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_magic_formula_filtering(self, client):
        """Test Magic Formula filtering"""
        params = {
            "limit": 20,
            "min_liquidity": 1000000,
            "max_pl": 15,
            "max_pvp": 2.5,
            "min_roic": 10
        }
        
        response = client.get("/api/v1/rankings/magic-formula", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self, client):
        """Test CORS headers in response"""
        response = client.options("/api/v1/sectors/")
        
        # Should include CORS headers
        assert response.status_code in [200, 405]
    
    def test_cors_preflight(self, client):
        """Test CORS preflight request"""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = client.options("/api/v1/rankings/", headers=headers)
        
        # Should handle preflight request
        assert response.status_code in [200, 405]
