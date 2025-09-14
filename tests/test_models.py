"""
Tests for database models
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.models import Sector, Stock, SectorRanking, DataUpdateLog
from app.database.connection import Base


class TestSector:
    """Test Sector model"""
    
    def test_create_sector(self, test_db):
        """Test creating a sector"""
        sector = Sector(
            name="Financeiro",
            category="Bancos",
            subsectors="Bancos Comerciais,Bancos de Investimento"
        )
        test_db.add(sector)
        test_db.commit()
        
        assert sector.id is not None
        assert sector.name == "Financeiro"
        assert sector.category == "Bancos"
        assert "Bancos Comerciais" in sector.subsectors
    
    def test_sector_repr(self, test_db):
        """Test sector string representation"""
        sector = Sector(name="Test Sector", category="Test")
        assert "Test Sector" in str(sector)


class TestStock:
    """Test Stock model"""
    
    def test_create_stock(self, test_db, sample_sector_data):
        """Test creating a stock"""
        # Create sector first
        sector = Sector(**sample_sector_data)
        test_db.add(sector)
        test_db.commit()
        
        # Create stock
        stock = Stock(
            symbol="PETR4",
            company_name="Petróleo Brasileiro S.A.",
            sector_id=sector.id,
            subsector="Petróleo e Gás",
            cotacao=30.50,
            pl=8.5,
            pvp=1.2,
            div_yield=12.5,
            roic=15.2,
            roe=18.5,
            is_active=True
        )
        test_db.add(stock)
        test_db.commit()
        
        assert stock.id is not None
        assert stock.symbol == "PETR4"
        assert stock.sector_id == sector.id
        assert stock.is_active is True
    
    def test_stock_sector_relationship(self, test_db, sample_sector_data):
        """Test stock-sector relationship"""
        # Create sector
        sector = Sector(**sample_sector_data)
        test_db.add(sector)
        test_db.commit()
        
        # Create stock
        stock = Stock(
            symbol="TEST4",
            company_name="Test Company",
            sector_id=sector.id,
            cotacao=10.0,
            is_active=True
        )
        test_db.add(stock)
        test_db.commit()
        
        # Test relationship
        assert stock.sector is not None
        assert stock.sector.name == sample_sector_data["name"]
        assert len(sector.stocks) == 1
        assert sector.stocks[0].symbol == "TEST4"


class TestSectorRanking:
    """Test SectorRanking model"""
    
    def test_create_ranking(self, test_db, sample_sector_data):
        """Test creating a sector ranking"""
        # Create sector and stock
        sector = Sector(**sample_sector_data)
        test_db.add(sector)
        test_db.commit()
        
        stock = Stock(
            symbol="TEST4",
            company_name="Test Company",
            sector_id=sector.id,
            cotacao=10.0,
            is_active=True
        )
        test_db.add(stock)
        test_db.commit()
        
        # Create ranking
        ranking = SectorRanking(
            stock_id=stock.id,
            sector_id=sector.id,
            score=85.5,
            rank_position=1,
            total_stocks=10
        )
        test_db.add(ranking)
        test_db.commit()
        
        assert ranking.id is not None
        assert ranking.score == 85.5
        assert ranking.rank_position == 1
    
    def test_ranking_relationships(self, test_db, sample_sector_data):
        """Test ranking relationships"""
        # Create sector and stock
        sector = Sector(**sample_sector_data)
        test_db.add(sector)
        test_db.commit()
        
        stock = Stock(
            symbol="TEST4",
            company_name="Test Company",
            sector_id=sector.id,
            cotacao=10.0,
            is_active=True
        )
        test_db.add(stock)
        test_db.commit()
        
        # Create ranking
        ranking = SectorRanking(
            stock_id=stock.id,
            sector_id=sector.id,
            score=75.0,
            rank_position=5,
            total_stocks=20
        )
        test_db.add(ranking)
        test_db.commit()
        
        # Test relationships
        assert ranking.stock is not None
        assert ranking.stock.symbol == "TEST4"
        assert ranking.sector is not None
        assert ranking.sector.name == sample_sector_data["name"]


class TestDataUpdateLog:
    """Test DataUpdateLog model"""
    
    def test_create_update_log(self, test_db):
        """Test creating an update log"""
        log = DataUpdateLog(
            operation_type="data_update",
            status="success",
            details="Updated 100 stocks successfully",
            stocks_updated=100
        )
        test_db.add(log)
        test_db.commit()
        
        assert log.id is not None
        assert log.operation_type == "data_update"
        assert log.status == "success"
        assert log.stocks_updated == 100
        assert log.created_at is not None
    
    def test_update_log_failure(self, test_db):
        """Test creating a failure log"""
        log = DataUpdateLog(
            operation_type="ranking_calculation",
            status="error",
            details="Failed to calculate rankings due to missing data",
            error_message="KeyError: 'cotacao'",
            stocks_updated=0
        )
        test_db.add(log)
        test_db.commit()
        
        assert log.status == "error"
        assert log.error_message is not None
        assert log.stocks_updated == 0
