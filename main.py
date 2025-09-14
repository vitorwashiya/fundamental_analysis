"""
Main FastAPI application
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.settings import settings
from app.database.connection import create_tables, get_db
from app.api import data_update, sectors, rankings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    print("Starting Fundamental Analysis API...")
    
    # Create database tables
    create_tables()
    print("Database tables created/verified")
    
    # Optionally perform data update on startup
    if settings.update_on_startup:
        print("Performing initial data update...")
        # This would be implemented to run in background
    
    yield
    
    # Shutdown
    print("Shutting down Fundamental Analysis API...")


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="""
    ## Fundamental Analysis API
    
    A comprehensive API for Brazilian stock market fundamental analysis.
    
    ### Features:
    - **Sector-specific analysis** with custom scoring algorithms
    - **Magic Formula rankings** based on "The Little Book That Beats the Market"
    - **Automated data updates** from fundamentus library
    - **Flexible filtering and search** capabilities
    
    ### Data Sources:
    - Fundamentus library for Brazilian market data
    - Sector-specific analysis methodologies
    - Custom scoring algorithms for each sector category
    
    ### Endpoints:
    - `/api/v1/data/` - Data update operations
    - `/api/v1/sectors/` - Sector information and stock listings
    - `/api/v1/rankings/` - Stock rankings and top performers
    """,
    lifespan=lifespan,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    data_update.router,
    prefix=f"{settings.api_v1_str}/data",
    tags=["Data Update"]
)

app.include_router(
    sectors.router,
    prefix=f"{settings.api_v1_str}/sectors",
    tags=["Sectors"]
)

app.include_router(
    rankings.router,
    prefix=f"{settings.api_v1_str}/rankings",
    tags=["Rankings"]
)


@app.get("/")
async def root():
    """
    API root endpoint
    """
    return {
        "message": f"Welcome to {settings.project_name}",
        "version": settings.version,
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running"
    }


@app.get("/health")
async def health_check(db = Depends(get_db)):
    """
    Health check endpoint
    """
    try:
        # Test database connection
        from app.models.models import Sector
        sector_count = db.query(Sector).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "sectors_in_db": sector_count,
            "version": settings.version
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
            "version": settings.version
        }


@app.get(f"{settings.api_v1_str}/info")
async def api_info():
    """
    API information and statistics
    """
    return {
        "api_name": settings.project_name,
        "version": settings.version,
        "endpoints": {
            "data_update": f"{settings.api_v1_str}/data/",
            "sectors": f"{settings.api_v1_str}/sectors/", 
            "rankings": f"{settings.api_v1_str}/rankings/"
        },
        "features": [
            "Sector-specific fundamental analysis",
            "Magic Formula rankings",
            "Automated data updates from fundamentus",
            "Brazilian stock market focus",
            "RESTful API with OpenAPI documentation"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
