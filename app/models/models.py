"""
Database models for the Fundamental Analysis API
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Sector(Base):
    """
    Model for financial sectors
    """
    __tablename__ = "sectors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # Financeiro, Utilities, etc.
    subsectors = Column(Text)  # JSON string with subsectors list
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stocks = relationship("Stock", back_populates="sector")


class Stock(Base):
    """
    Model for individual stocks and their indicators
    """
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    company_name = Column(String(200))
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    subsector = Column(String(100))
    
    # Financial indicators from fundamentus.get_resultado()
    cotacao = Column(Float)  # Current price
    pl = Column(Float)  # P/E ratio
    pvp = Column(Float)  # P/B ratio
    psr = Column(Float)  # P/S ratio
    div_yield = Column(Float)  # Dividend yield
    p_ativo = Column(Float)  # Price to assets
    p_cap_giro = Column(Float)  # Price to working capital
    p_ebit = Column(Float)  # Price to EBIT
    p_ativ_circ_liq = Column(Float)  # Price to net current assets
    ev_ebit = Column(Float)  # EV/EBIT
    ev_ebitda = Column(Float)  # EV/EBITDA
    mrg_ebit = Column(Float)  # EBIT margin
    mrg_liq = Column(Float)  # Net margin
    liq_corr = Column(Float)  # Current liquidity
    roic = Column(Float)  # Return on invested capital
    roe = Column(Float)  # Return on equity
    liq_2meses = Column(Float)  # 2-month liquidity
    patrim_liq = Column(Float)  # Net equity
    div_br_patrim = Column(Float)  # Gross debt to equity
    cresc_rec_5a = Column(Float)  # 5-year revenue growth
    
    # Additional indicators from fundamentus.get_papel()
    receita_liquida = Column(Float)  # Net revenue
    ebit = Column(Float)
    ebitda = Column(Float)
    lucro_liquido = Column(Float)  # Net profit
    divida_liquida = Column(Float)  # Net debt
    ativo_total = Column(Float)  # Total assets
    patrimonio_liquido = Column(Float)  # Shareholders' equity
    
    # Calculated indicators
    div_liq_ebitda = Column(Float)  # Net debt / EBITDA
    magic_formula_rank = Column(Integer)  # Magic formula ranking
    sector_rank = Column(Integer)  # Ranking within sector
    
    # Metadata
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sector = relationship("Sector", back_populates="stocks")
    rankings = relationship("SectorRanking", back_populates="stock")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_stock_sector_rank', 'sector_id', 'sector_rank'),
        Index('idx_stock_magic_formula', 'magic_formula_rank'),
        Index('idx_stock_active', 'is_active'),
    )


class SectorRanking(Base):
    """
    Model for sector-specific rankings
    """
    __tablename__ = "sector_rankings"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    
    # Ranking scores (0-100, higher is better)
    earnings_yield_score = Column(Float, default=0)  # EBIT/EV score
    return_on_capital_score = Column(Float, default=0)  # ROIC score
    value_score = Column(Float, default=0)  # Combined value indicators
    quality_score = Column(Float, default=0)  # Quality indicators
    growth_score = Column(Float, default=0)  # Growth indicators
    dividend_score = Column(Float, default=0)  # Dividend indicators
    
    # Final combined score
    final_score = Column(Float, default=0)
    rank_position = Column(Integer)
    
    # Metadata
    calculation_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="rankings")
    sector = relationship("Sector")
    
    # Indexes
    __table_args__ = (
        Index('idx_sector_ranking_score', 'sector_id', 'final_score'),
        Index('idx_sector_ranking_position', 'sector_id', 'rank_position'),
        Index('idx_sector_ranking_date', 'calculation_date'),
    )


class DataUpdateLog(Base):
    """
    Model to track data updates
    """
    __tablename__ = "data_update_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    update_type = Column(String(50), nullable=False)  # 'full', 'incremental', 'rankings'
    status = Column(String(20), nullable=False)  # 'started', 'completed', 'failed'
    stocks_processed = Column(Integer, default=0)
    sectors_processed = Column(Integer, default=0)
    error_message = Column(Text)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Indexes
    __table_args__ = (
        Index('idx_update_log_type_status', 'update_type', 'status'),
        Index('idx_update_log_date', 'start_time'),
    )
