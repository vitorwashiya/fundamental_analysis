"""
API endpoints for sector operations
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.models.schemas import SectorResponse, APIResponse
from app.models.models import Sector

router = APIRouter()


@router.get("/", response_model=APIResponse)
async def get_all_sectors(
    category: Optional[str] = Query(None, description="Filter by sector category"),
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Get all available sectors
    
    - **category**: Optional filter by sector category (e.g., "Financeiro", "Utilities")
    """
    try:
        query = db.query(Sector)
        
        if category:
            query = query.filter(Sector.category == category)
        
        sectors = query.order_by(Sector.category, Sector.name).all()
        
        # Group sectors by category
        sectors_by_category = {}
        for sector in sectors:
            if sector.category not in sectors_by_category:
                sectors_by_category[sector.category] = []
            
            sector_data = {
                "id": sector.id,
                "name": sector.name,
                "category": sector.category,
                "subsectors": sector.subsectors.split(',') if sector.subsectors else [],
                "created_at": sector.created_at,
                "updated_at": sector.updated_at
            }
            sectors_by_category[sector.category].append(sector_data)
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(sectors)} sectors",
            data=sectors_by_category
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=APIResponse)
async def get_sector_categories(db: Session = Depends(get_db)) -> APIResponse:
    """
    Get all sector categories
    """
    try:
        from sqlalchemy import distinct
        
        categories = db.query(distinct(Sector.category)).all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        # Get count of sectors in each category
        category_counts = {}
        for category in category_list:
            count = db.query(Sector).filter(Sector.category == category).count()
            category_counts[category] = count
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(category_list)} categories",
            data={
                "categories": category_list,
                "counts": category_counts
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sector_id}", response_model=APIResponse)
async def get_sector(
    sector_id: int,
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Get a specific sector by ID
    
    - **sector_id**: Sector ID
    """
    try:
        sector = db.query(Sector).filter(Sector.id == sector_id).first()
        
        if not sector:
            raise HTTPException(status_code=404, detail="Sector not found")
        
        # Get stock count for this sector
        from app.models.models import Stock
        stock_count = db.query(Stock).filter(Stock.sector_id == sector_id).count()
        
        sector_data = {
            "id": sector.id,
            "name": sector.name,
            "category": sector.category,
            "subsectors": sector.subsectors.split(',') if sector.subsectors else [],
            "created_at": sector.created_at,
            "updated_at": sector.updated_at,
            "stock_count": stock_count
        }
        
        return APIResponse(
            success=True,
            message="Sector retrieved successfully",
            data=sector_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sector_id}/stocks", response_model=APIResponse)
async def get_sector_stocks(
    sector_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    active_only: bool = Query(True, description="Show only active stocks"),
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Get stocks in a specific sector
    
    - **sector_id**: Sector ID
    - **page**: Page number (default: 1)
    - **size**: Page size (default: 20, max: 100)
    - **active_only**: Show only active stocks (default: True)
    """
    try:
        from app.models.models import Stock
        from sqlalchemy import and_
        
        # Check if sector exists
        sector = db.query(Sector).filter(Sector.id == sector_id).first()
        if not sector:
            raise HTTPException(status_code=404, detail="Sector not found")
        
        # Build query
        query = db.query(Stock).filter(Stock.sector_id == sector_id)
        
        if active_only:
            query = query.filter(Stock.is_active == True)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        stocks = query.order_by(Stock.sector_rank.asc().nullslast(), Stock.symbol).offset(offset).limit(size).all()
        
        # Format stock data
        stock_data = []
        for stock in stocks:
            stock_info = {
                "id": stock.id,
                "symbol": stock.symbol,
                "company_name": stock.company_name,
                "subsector": stock.subsector,
                "sector_rank": stock.sector_rank,
                "magic_formula_rank": stock.magic_formula_rank,
                "cotacao": stock.cotacao,
                "pl": stock.pl,
                "pvp": stock.pvp,
                "div_yield": stock.div_yield,
                "roic": stock.roic,
                "roe": stock.roe,
                "is_active": stock.is_active,
                "last_updated": stock.last_updated
            }
            stock_data.append(stock_info)
        
        # Calculate pagination info
        pages = (total + size - 1) // size
        has_next = page < pages
        has_prev = page > 1
        
        pagination_info = {
            "page": page,
            "size": size,
            "total": total,
            "pages": pages,
            "has_next": has_next,
            "has_prev": has_prev
        }
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(stock_data)} stocks from sector {sector.name}",
            data={
                "sector": {
                    "id": sector.id,
                    "name": sector.name,
                    "category": sector.category
                },
                "stocks": stock_data,
                "pagination": pagination_info
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
