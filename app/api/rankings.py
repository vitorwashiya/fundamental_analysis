"""
API endpoints for stock rankings
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.database.connection import get_db
from app.models.schemas import APIResponse, TopStocksRequest
from app.services import RankingService

router = APIRouter()


@router.get("/sector/{sector_id}", response_model=APIResponse)
async def get_top_stocks_by_sector(
    sector_id: int,
    limit: int = Query(10, ge=1, le=100, description="Number of top stocks to return"),
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Get top N stocks for a specific sector
    
    - **sector_id**: Sector ID
    - **limit**: Number of top stocks to return (default: 10, max: 100)
    """
    try:
        from app.models.models import Sector, Stock, SectorRanking
        
        # Check if sector exists
        sector = db.query(Sector).filter(Sector.id == sector_id).first()
        if not sector:
            raise HTTPException(status_code=404, detail="Sector not found")
        
        # Get top rankings for this sector
        rankings = db.query(SectorRanking).join(Stock).filter(
            SectorRanking.sector_id == sector_id
        ).order_by(SectorRanking.rank_position).limit(limit).all()
        
        if not rankings:
            return APIResponse(
                success=True,
                message=f"No rankings found for sector {sector.name}",
                data={
                    "sector": {
                        "id": sector.id,
                        "name": sector.name,
                        "category": sector.category
                    },
                    "stocks": []
                }
            )
        
        # Format ranking data
        stocks_data = []
        for ranking in rankings:
            stock = ranking.stock
            stock_info = {
                "rank_position": ranking.rank_position,
                "stock_id": stock.id,
                "symbol": stock.symbol,
                "company_name": stock.company_name,
                "subsector": stock.subsector,
                "scores": {
                    "earnings_yield_score": ranking.earnings_yield_score,
                    "return_on_capital_score": ranking.return_on_capital_score,
                    "value_score": ranking.value_score,
                    "quality_score": ranking.quality_score,
                    "growth_score": ranking.growth_score,
                    "dividend_score": ranking.dividend_score,
                    "final_score": ranking.final_score
                },
                "key_metrics": {
                    "cotacao": stock.cotacao,
                    "pl": stock.pl,
                    "pvp": stock.pvp,
                    "div_yield": stock.div_yield,
                    "roic": stock.roic,
                    "roe": stock.roe,
                    "ev_ebit": stock.ev_ebit,
                    "ev_ebitda": stock.ev_ebitda
                },
                "calculation_date": ranking.calculation_date
            }
            stocks_data.append(stock_info)
        
        return APIResponse(
            success=True,
            message=f"Retrieved top {len(stocks_data)} stocks for sector {sector.name}",
            data={
                "sector": {
                    "id": sector.id,
                    "name": sector.name,
                    "category": sector.category
                },
                "stocks": stocks_data
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sector/{sector_id}/by-score", response_model=APIResponse)
async def get_stocks_by_score_type(
    sector_id: int,
    score_type: str = Query("final_score", description="Type of score to rank by"),
    limit: int = Query(10, ge=1, le=100, description="Number of stocks to return"),
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Get top stocks by specific score type
    
    - **sector_id**: Sector ID
    - **score_type**: Score type (final_score, earnings_yield_score, return_on_capital_score, etc.)
    - **limit**: Number of stocks to return
    """
    try:
        from app.models.models import Sector, SectorRanking
        from sqlalchemy import desc
        
        # Validate score type
        valid_scores = [
            'final_score', 'earnings_yield_score', 'return_on_capital_score',
            'value_score', 'quality_score', 'growth_score', 'dividend_score'
        ]
        
        if score_type not in valid_scores:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid score type. Must be one of: {', '.join(valid_scores)}"
            )
        
        # Check if sector exists
        sector = db.query(Sector).filter(Sector.id == sector_id).first()
        if not sector:
            raise HTTPException(status_code=404, detail="Sector not found")
        
        # Get rankings ordered by specified score
        score_column = getattr(SectorRanking, score_type)
        rankings = db.query(SectorRanking).filter(
            SectorRanking.sector_id == sector_id
        ).order_by(desc(score_column)).limit(limit).all()
        
        # Format data
        stocks_data = []
        for i, ranking in enumerate(rankings, 1):
            stock = ranking.stock
            stock_info = {
                "position": i,
                "stock_id": stock.id,
                "symbol": stock.symbol,
                "company_name": stock.company_name,
                "score_value": getattr(ranking, score_type),
                "all_scores": {
                    "earnings_yield_score": ranking.earnings_yield_score,
                    "return_on_capital_score": ranking.return_on_capital_score,
                    "value_score": ranking.value_score,
                    "quality_score": ranking.quality_score,
                    "growth_score": ranking.growth_score,
                    "dividend_score": ranking.dividend_score,
                    "final_score": ranking.final_score
                }
            }
            stocks_data.append(stock_info)
        
        return APIResponse(
            success=True,
            message=f"Retrieved top {len(stocks_data)} stocks by {score_type}",
            data={
                "sector": {"id": sector.id, "name": sector.name},
                "score_type": score_type,
                "stocks": stocks_data
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-sectors", response_model=APIResponse)
async def get_top_stocks_all_sectors(
    limit_per_sector: int = Query(5, ge=1, le=20, description="Number of top stocks per sector"),
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Get top N stocks for each sector
    
    - **limit_per_sector**: Number of top stocks per sector (default: 5, max: 20)
    """
    try:
        ranking_service = RankingService(db)
        results = ranking_service.get_top_stocks_all_sectors(limit_per_sector)
        
        # Format results
        sectors_data = {}
        total_stocks = 0
        
        for sector_name, rankings in results.items():
            stocks_data = []
            for ranking in rankings:
                stock = ranking.stock
                stock_info = {
                    "rank_position": ranking.rank_position,
                    "symbol": stock.symbol,
                    "company_name": stock.company_name,
                    "final_score": ranking.final_score,
                    "key_metrics": {
                        "cotacao": stock.cotacao,
                        "pl": stock.pl,
                        "roic": stock.roic,
                        "div_yield": stock.div_yield
                    }
                }
                stocks_data.append(stock_info)
            
            sectors_data[sector_name] = {
                "sector_id": rankings[0].sector_id,
                "stocks": stocks_data
            }
            total_stocks += len(stocks_data)
        
        return APIResponse(
            success=True,
            message=f"Retrieved top stocks for {len(sectors_data)} sectors ({total_stocks} total stocks)",
            data=sectors_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/magic-formula", response_model=APIResponse)
async def get_magic_formula_stocks(
    limit: int = Query(20, ge=1, le=100, description="Number of top stocks to return"),
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Get top stocks by Magic Formula ranking
    (Based on "The Little Book That Beats the Market")
    
    - **limit**: Number of top stocks to return (default: 20, max: 100)
    """
    try:
        ranking_service = RankingService(db)
        stocks = ranking_service.get_top_magic_formula_stocks(limit)
        
        if not stocks:
            return APIResponse(
                success=True,
                message="No Magic Formula rankings available",
                data=[]
            )
        
        # Format stock data
        stocks_data = []
        for stock in stocks:
            # Calculate earnings yield
            earnings_yield = (1 / stock.ev_ebit) * 100 if stock.ev_ebit and stock.ev_ebit > 0 else None
            
            stock_info = {
                "magic_formula_rank": stock.magic_formula_rank,
                "symbol": stock.symbol,
                "company_name": stock.company_name,
                "sector_name": stock.sector.name if stock.sector else None,
                "key_metrics": {
                    "cotacao": stock.cotacao,
                    "earnings_yield": earnings_yield,
                    "roic": stock.roic,
                    "pl": stock.pl,
                    "pvp": stock.pvp,
                    "ev_ebit": stock.ev_ebit,
                    "div_yield": stock.div_yield
                },
                "last_updated": stock.last_updated
            }
            stocks_data.append(stock_info)
        
        return APIResponse(
            success=True,
            message=f"Retrieved top {len(stocks_data)} Magic Formula stocks",
            data={
                "methodology": "Magic Formula combines Earnings Yield (EBIT/EV) and Return on Capital (ROIC)",
                "stocks": stocks_data
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=APIResponse)
async def search_stock_rankings(
    symbol: Optional[str] = Query(None, description="Stock symbol to search"),
    sector_name: Optional[str] = Query(None, description="Sector name to filter"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum final score"),
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Search stock rankings with various filters
    
    - **symbol**: Stock symbol to search
    - **sector_name**: Sector name to filter  
    - **min_score**: Minimum final score threshold
    """
    try:
        from app.models.models import Stock, SectorRanking, Sector
        from sqlalchemy import and_
        
        # Build query
        query = db.query(SectorRanking).join(Stock).join(Sector)
        
        filters = []
        if symbol:
            filters.append(Stock.symbol.ilike(f"%{symbol.upper()}%"))
        
        if sector_name:
            filters.append(Sector.name.ilike(f"%{sector_name}%"))
        
        if min_score is not None:
            filters.append(SectorRanking.final_score >= min_score)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Execute query
        rankings = query.order_by(SectorRanking.final_score.desc()).limit(50).all()
        
        # Format results
        results = []
        for ranking in rankings:
            stock = ranking.stock
            sector = ranking.sector
            
            result = {
                "symbol": stock.symbol,
                "company_name": stock.company_name,
                "sector": {
                    "id": sector.id,
                    "name": sector.name,
                    "category": sector.category
                },
                "rank_position": ranking.rank_position,
                "final_score": ranking.final_score,
                "key_metrics": {
                    "cotacao": stock.cotacao,
                    "pl": stock.pl,
                    "roic": stock.roic,
                    "div_yield": stock.div_yield
                }
            }
            results.append(result)
        
        return APIResponse(
            success=True,
            message=f"Found {len(results)} matching stocks",
            data=results
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
