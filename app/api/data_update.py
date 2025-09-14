"""
API endpoints for data update operations
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.connection import get_db
from app.models.schemas import DataUpdateRequest, DataUpdateResponse, APIResponse
from app.services import FundamentusService, RankingService

router = APIRouter()


@router.post("/update", response_model=APIResponse)
async def update_data(
    background_tasks: BackgroundTasks,
    request: DataUpdateRequest = DataUpdateRequest(),
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Update financial data from fundamentus
    
    - **update_type**: Type of update (full, incremental, rankings)
    - **force_update**: Force update even if recent data exists
    """
    try:
        fundamentus_service = FundamentusService(db)
        ranking_service = RankingService(db)
        
        if request.update_type == "full":
            # Full data update
            background_tasks.add_task(
                _perform_full_update, 
                fundamentus_service, 
                ranking_service
            )
            return APIResponse(
                success=True,
                message="Full data update started in background",
                data={"update_type": "full", "status": "started"}
            )
        
        elif request.update_type == "rankings":
            # Rankings only update
            background_tasks.add_task(
                _perform_rankings_update,
                ranking_service
            )
            return APIResponse(
                success=True,
                message="Rankings update started in background",
                data={"update_type": "rankings", "status": "started"}
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Update type '{request.update_type}' not supported"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/update/status", response_model=APIResponse)
async def get_update_status(db: Session = Depends(get_db)) -> APIResponse:
    """
    Get the status of the latest data update
    """
    try:
        from app.models.models import DataUpdateLog
        
        # Get the latest update log
        latest_update = db.query(DataUpdateLog).order_by(
            DataUpdateLog.start_time.desc()
        ).first()
        
        if not latest_update:
            return APIResponse(
                success=True,
                message="No update logs found",
                data=None
            )
        
        update_data = {
            "update_id": latest_update.id,
            "update_type": latest_update.update_type,
            "status": latest_update.status,
            "stocks_processed": latest_update.stocks_processed,
            "sectors_processed": latest_update.sectors_processed,
            "start_time": latest_update.start_time,
            "end_time": latest_update.end_time,
            "duration_seconds": latest_update.duration_seconds,
            "error_message": latest_update.error_message
        }
        
        return APIResponse(
            success=True,
            message="Update status retrieved successfully",
            data=update_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/update/history", response_model=APIResponse)
async def get_update_history(
    limit: int = 10,
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Get history of data updates
    
    - **limit**: Number of recent updates to return (default: 10)
    """
    try:
        from app.models.models import DataUpdateLog
        
        updates = db.query(DataUpdateLog).order_by(
            DataUpdateLog.start_time.desc()
        ).limit(limit).all()
        
        history = []
        for update in updates:
            history.append({
                "update_id": update.id,
                "update_type": update.update_type,
                "status": update.status,
                "stocks_processed": update.stocks_processed,
                "sectors_processed": update.sectors_processed,
                "start_time": update.start_time,
                "end_time": update.end_time,
                "duration_seconds": update.duration_seconds,
                "error_message": update.error_message
            })
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(history)} update records",
            data=history
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _perform_full_update(
    fundamentus_service: FundamentusService,
    ranking_service: RankingService
):
    """
    Background task for full data update
    """
    try:
        # Update stock and sector data
        stocks_count, sectors_count = fundamentus_service.full_data_update()
        
        # Update rankings
        ranking_service.update_all_sector_rankings()
        ranking_service.calculate_magic_formula_rankings()
        
        print(f"Full update completed: {stocks_count} stocks, {sectors_count} sectors")
    
    except Exception as e:
        print(f"Full update failed: {e}")


async def _perform_rankings_update(ranking_service: RankingService):
    """
    Background task for rankings update
    """
    try:
        # Update sector rankings
        results = ranking_service.update_all_sector_rankings()
        
        # Update Magic Formula rankings
        magic_count = ranking_service.calculate_magic_formula_rankings()
        
        total_rankings = sum(results.values())
        print(f"Rankings update completed: {total_rankings} sector rankings, {magic_count} Magic Formula rankings")
    
    except Exception as e:
        print(f"Rankings update failed: {e}")


@router.post("/sectors/sync", response_model=APIResponse)
async def sync_sectors(db: Session = Depends(get_db)) -> APIResponse:
    """
    Synchronize sector configuration with database
    """
    try:
        from app.sectors import SectorAnalyzerFactory
        from app.models.models import Sector
        
        factory = SectorAnalyzerFactory()
        all_sectors = factory.get_all_sectors()
        
        synced_sectors = []
        
        for category, subsectors in all_sectors.items():
            for subsector in subsectors:
                # Check if sector exists
                existing = db.query(Sector).filter(Sector.name == subsector).first()
                
                if not existing:
                    # Create new sector
                    new_sector = Sector(
                        name=subsector,
                        category=category,
                        subsectors=subsector
                    )
                    db.add(new_sector)
                    synced_sectors.append(subsector)
                else:
                    # Update category if needed
                    if existing.category != category:
                        existing.category = category
                        synced_sectors.append(f"{subsector} (updated)")
        
        db.commit()
        
        return APIResponse(
            success=True,
            message=f"Synchronized {len(synced_sectors)} sectors",
            data={"synced_sectors": synced_sectors}
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
