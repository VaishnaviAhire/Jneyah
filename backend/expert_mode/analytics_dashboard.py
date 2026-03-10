from fastapi import APIRouter, Request, Query
from typing import Optional, List
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/expert/dashboard", tags=["expert_dashboard"])

# Initialize service
try:
    analytics_service = AnalyticsService()
    logger.info("✅ Analytics Dashboard Service initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize Analytics Dashboard: {e}")
    analytics_service = None

@router.get("/market-composition")
async def get_market_composition(
    industry: str = Query("cosmetic", description="cosmetic or food"),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    time_range: str = Query("1y", description="1m, 3m, 6m, 1y")
):
    """Get market composition analytics with visualizations"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Service not available"}
        
        data = analytics_service.get_market_composition({
            "industry": industry,
            "category": category,
            "brand": brand,
            "time_range": time_range
        })
        
        # Add visualization configurations
        visualizations = {
            "ingredient_frequency": {
                "type": "bar",
                "title": "Top 20 Most Common Ingredients",
                "x_axis": "ingredient",
                "y_axis": "count",
                "color": "#38bdf8"
            },
            "brand_prevalence": {
                "type": "pie",
                "title": "Market Share by Brand",
                "labels": "brand",
                "values": "product_count"
            },
            "category_density": {
                "type": "treemap",
                "title": "Formulation Complexity by Category",
                "labels": "category",
                "parents": "",
                "values": "avg_ingredients"
            }
        }
        
        return {
            "success": True, 
            "data": data,
            "visualizations": visualizations
        }
    except Exception as e:
        logger.error(f"Market composition error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/risk-distribution")
async def get_risk_distribution(
    category: Optional[str] = None,
    min_risk: float = Query(0, description="Minimum risk score"),
    max_risk: float = Query(10, description="Maximum risk score")
):
    """Get risk distribution heatmap and cluster data"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Service not available"}
        
        data = analytics_service.get_risk_distribution({
            "category": category,
            "min_risk": min_risk,
            "max_risk": max_risk
        })
        
        visualizations = {
            "risk_heatmap": {
                "type": "heatmap",
                "title": "Ingredient Risk Distribution Heatmap",
                "x_axis": ["Acute", "Chronic", "Allergen", "Environmental"],
                "y_axis": "categories"
            },
            "risk_clusters": {
                "type": "scatter",
                "title": "High-Risk Ingredient Clusters",
                "x_axis": "toxicity",
                "y_axis": "frequency",
                "size": "risk_score"
            },
            "category_risk": {
                "type": "box",
                "title": "Risk Score Distribution by Category",
                "x_axis": "category",
                "y_axis": "risk_score"
            }
        }
        
        return {
            "success": True,
            "data": data,
            "visualizations": visualizations
        }
    except Exception as e:
        logger.error(f"Risk distribution error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/interaction-network")
async def get_interaction_network(
    ingredient: Optional[str] = Query(None, description="Ingredient name or ID"),
    depth: int = Query(2, description="Network depth")
):
    """Get ingredient interaction network graph"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Service not available"}
        
        # If no ingredient specified, return overview stats
        if not ingredient:
            data = analytics_service.get_network_overview()
        else:
            data = analytics_service.get_interaction_network(ingredient, depth)
        
        visualizations = {
            "network_graph": {
                "type": "network",
                "title": f"Ingredient Interaction Network{f' - {ingredient}' if ingredient else ''}",
                "layout": "force-directed"
            },
            "interaction_stats": {
                "type": "bar",
                "title": "Interaction Types Distribution",
                "x_axis": "type",
                "y_axis": "count"
            }
        }
        
        return {
            "success": True,
            "data": data,
            "visualizations": visualizations
        }
    except Exception as e:
        logger.error(f"Interaction network error: {e}")
        return {"success": False, "error": str(e)}
    
    
@router.get("/exposure-analysis")
async def get_exposure_analysis(
    ingredients: str = Query(..., description="Comma-separated ingredient names"),
    time_period: str = Query("365", description="Days to analyze"),
    population: str = Query("general", description="general, sensitive, pediatric")
):
    """Get cumulative exposure analysis"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Service not available"}
        
        ingredient_list = [i.strip() for i in ingredients.split(',')]
        
        data = analytics_service.get_exposure_analysis({
            "ingredients": ingredient_list,
            "time_period": time_period,
            "population": population
        })
        
        visualizations = {
            "risk_curve": {
                "type": "line",
                "title": "Cumulative Risk Over Time",
                "x_axis": "time (days)",
                "y_axis": "risk score"
            },
            "population_distribution": {
                "type": "histogram",
                "title": "Population Risk Distribution",
                "x_axis": "risk score",
                "y_axis": "frequency"
            },
            "risk_factors": {
                "type": "radar",
                "title": "Risk Factor Breakdown",
                "categories": "factors",
                "values": "contributions"
            }
        }
        
        return {
            "success": True,
            "data": data,
            "visualizations": visualizations
        }
    except Exception as e:
        logger.error(f"Exposure analysis error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/time-trends")
async def get_time_trends(
    ingredients: Optional[str] = Query(None, description="Comma-separated ingredients"),
    category: Optional[str] = None,
    start_year: int = Query(2015),
    end_year: int = Query(2025)
):
    """Get time-based trends analysis"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Service not available"}
        
        ingredient_list = [i.strip() for i in ingredients.split(',')] if ingredients else None
        
        data = analytics_service.get_time_trends({
            "ingredients": ingredient_list,
            "category": category,
            "start_year": start_year,
            "end_year": end_year
        })
        
        visualizations = {
            "trend_lines": {
                "type": "line",
                "title": "Ingredient Usage Trends Over Time",
                "x_axis": "year",
                "y_axis": "frequency"
            },
            "category_shifts": {
                "type": "bar",
                "title": "Category Growth Rates",
                "x_axis": "category",
                "y_axis": "growth_rate"
            },
            "heatmap_trends": {
                "type": "heatmap",
                "title": "Year-over-Year Changes",
                "x_axis": "year",
                "y_axis": "ingredient"
            }
        }
        
        return {
            "success": True,
            "data": data,
            "visualizations": visualizations
        }
    except Exception as e:
        logger.error(f"Time trends error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/export")
async def export_analytics(
    format: str = Query("json", description="json, csv, pdf"),
    sections: str = Query("all", description="Comma-separated sections")
):
    """Export analytics data in various formats"""
    try:
        if analytics_service is None:
            return {"success": False, "error": "Service not available"}
        
        section_list = sections.split(',') if sections != 'all' else ['market', 'risk', 'interaction', 'exposure', 'trends']
        
        data = analytics_service.generate_report({
            "include_market": 'market' in section_list,
            "include_risk": 'risk' in section_list,
            "include_interaction": 'interaction' in section_list,
            "include_exposure": 'exposure' in section_list,
            "include_trends": 'trends' in section_list
        })
        
        if format == 'csv':
            # Convert to CSV format
            return {"success": True, "data": data, "format": "csv"}
        elif format == 'pdf':
            return {"success": True, "data": data, "format": "pdf"}
        else:
            return {"success": True, "data": data, "format": "json"}
            
    except Exception as e:
        logger.error(f"Export error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/filters")
async def get_available_filters():
    """Get available filter options for dashboard"""
    try:
        filters = {
            "industries": ["cosmetic", "food"],
            "categories": {
                "cosmetic": ["Moisturizer", "Cleanser", "Serum", "Sunscreen", "Mask", "Toner", "Eye Cream"],
                "food": ["Snacks", "Beverages", "Dairy", "Bakery", "Frozen Foods", "Canned Goods", "Condiments"]
            },
            "brands": {
                "cosmetic": ["L'Oreal", "Neutrogena", "Cetaphil", "CeraVe", "The Ordinary", "La Roche-Posay"],
                "food": ["Brand A", "Brand B", "Brand C", "Brand D", "Brand E"]
            },
            "risk_levels": ["Low", "Medium", "High"],
            "time_ranges": [
                {"value": "1m", "label": "Last Month"},
                {"value": "3m", "label": "Last 3 Months"},
                {"value": "6m", "label": "Last 6 Months"},
                {"value": "1y", "label": "Last Year"},
                {"value": "5y", "label": "Last 5 Years"}
            ]
        }
        return {"success": True, "data": filters}
    except Exception as e:
        logger.error(f"Filters error: {e}")
        return {"success": False, "error": str(e)}