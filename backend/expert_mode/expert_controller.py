from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from .analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/expert", tags=["expert"])

# Initialize service
try:
    analytics_service = AnalyticsService()
    logger.info("✅ Expert Mode Analytics Service initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize Analytics Service: {e}")
    analytics_service = None

# No auth dependency - open to all
@router.get("/dashboard/overview")
async def get_dashboard_overview():
    """Get overview statistics for expert dashboard"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Analytics service not available"}
        stats = analytics_service.get_overview_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"Dashboard overview error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/dashboard/market-composition")
async def get_market_composition(request: Request):
    """Get market composition analytics"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Analytics service not available"}
        filters = await request.json() if await request.body() else {}
        data = analytics_service.get_market_composition(filters)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Market composition error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/dashboard/risk-distribution")
async def get_risk_distribution(request: Request):
    """Get risk distribution heatmap data"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Analytics service not available"}
        filters = await request.json() if await request.body() else {}
        data = analytics_service.get_risk_distribution(filters)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Risk distribution error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/dashboard/interaction-network/{ingredient_id}")
async def get_interaction_network(ingredient_id: str, depth: Optional[int] = 2):
    """Get ingredient interaction network"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Analytics service not available"}
        data = analytics_service.get_interaction_network(ingredient_id, depth)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Interaction network error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/dashboard/exposure-analysis")
async def get_exposure_analysis(request: Request):
    """Get cumulative exposure analysis"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Analytics service not available"}
        params = await request.json() if await request.body() else {}
        data = analytics_service.get_exposure_analysis(params)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Exposure analysis error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/dashboard/time-trends")
async def get_time_trends(request: Request):
    """Get time-based trends for ingredients"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Analytics service not available"}
        filters = await request.json() if await request.body() else {}
        data = analytics_service.get_time_trends(filters)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Time trends error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/dashboard/export-report")
async def export_report(request: Request):
    """Export analytics report"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Analytics service not available"}
        params = await request.json()
        report_data = analytics_service.generate_report(params)
        return {"success": True, "data": report_data}
    except Exception as e:
        logger.error(f"Export report error: {e}")
        return {"success": False, "error": str(e)}