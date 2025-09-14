"""
Pydantic schemas for API request/response models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SectorBase(BaseModel):
    """Base sector schema"""
    name: str
    category: str
    subsectors: Optional[List[str]] = None


class SectorCreate(SectorBase):
    """Schema for creating a sector"""
    pass


class SectorResponse(SectorBase):
    """Schema for sector response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StockBase(BaseModel):
    """Base stock schema"""
    symbol: str
    company_name: Optional[str] = None
    subsector: Optional[str] = None


class StockIndicators(BaseModel):
    """Stock financial indicators"""
    cotacao: Optional[float] = None
    pl: Optional[float] = None
    pvp: Optional[float] = None
    psr: Optional[float] = None
    div_yield: Optional[float] = None
    p_ativo: Optional[float] = None
    p_cap_giro: Optional[float] = None
    p_ebit: Optional[float] = None
    p_ativ_circ_liq: Optional[float] = None
    ev_ebit: Optional[float] = None
    ev_ebitda: Optional[float] = None
    mrg_ebit: Optional[float] = None
    mrg_liq: Optional[float] = None
    liq_corr: Optional[float] = None
    roic: Optional[float] = None
    roe: Optional[float] = None
    liq_2meses: Optional[float] = None
    patrim_liq: Optional[float] = None
    div_br_patrim: Optional[float] = None
    cresc_rec_5a: Optional[float] = None
    receita_liquida: Optional[float] = None
    ebit: Optional[float] = None
    ebitda: Optional[float] = None
    lucro_liquido: Optional[float] = None
    divida_liquida: Optional[float] = None
    ativo_total: Optional[float] = None
    patrimonio_liquido: Optional[float] = None
    div_liq_ebitda: Optional[float] = None


class StockCreate(StockBase, StockIndicators):
    """Schema for creating a stock"""
    sector_id: int


class StockResponse(StockBase, StockIndicators):
    """Schema for stock response"""
    id: int
    sector_id: int
    sector_name: Optional[str] = None
    magic_formula_rank: Optional[int] = None
    sector_rank: Optional[int] = None
    is_active: bool
    last_updated: datetime
    
    class Config:
        from_attributes = True


class RankingScores(BaseModel):
    """Ranking scores schema"""
    earnings_yield_score: float = Field(ge=0, le=100)
    return_on_capital_score: float = Field(ge=0, le=100)
    value_score: float = Field(ge=0, le=100)
    quality_score: float = Field(ge=0, le=100)
    growth_score: float = Field(ge=0, le=100)
    dividend_score: float = Field(ge=0, le=100)
    final_score: float = Field(ge=0, le=100)


class SectorRankingResponse(BaseModel):
    """Schema for sector ranking response"""
    id: int
    stock_id: int
    stock_symbol: str
    stock_name: Optional[str] = None
    sector_id: int
    sector_name: str
    rank_position: int
    scores: RankingScores
    calculation_date: datetime
    
    class Config:
        from_attributes = True


class TopStocksRequest(BaseModel):
    """Schema for top stocks request"""
    sector_id: Optional[int] = None
    sector_name: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)
    score_type: Optional[str] = Field(default="final_score", pattern="^(final_score|earnings_yield_score|return_on_capital_score|value_score|quality_score|growth_score|dividend_score)$")


class TopStocksBySectorResponse(BaseModel):
    """Schema for top stocks by sector response"""
    sector_id: int
    sector_name: str
    sector_category: str
    stocks: List[SectorRankingResponse]


class DataUpdateRequest(BaseModel):
    """Schema for data update request"""
    update_type: str = Field(default="full", pattern="^(full|incremental|rankings)$")
    force_update: bool = Field(default=False)


class DataUpdateResponse(BaseModel):
    """Schema for data update response"""
    update_id: int
    status: str
    message: str
    stocks_processed: int = 0
    sectors_processed: int = 0
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class APIResponse(BaseModel):
    """Generic API response schema"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response schema"""
    items: List[Any]
    page: int
    size: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool
