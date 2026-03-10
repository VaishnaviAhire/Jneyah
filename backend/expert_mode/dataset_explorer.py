from fastapi import APIRouter, Request, Query, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List, Dict
import logging
import pandas as pd
import numpy as np
import json
import csv
import io
from datetime import datetime
from pathlib import Path
import zipfile
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/expert/datasets", tags=["expert_datasets"])

# Sample datasets for demonstration
COSMETIC_INGREDIENTS_DATASET = {
    "name": "Cosmetic Ingredients Database",
    "description": "Comprehensive database of cosmetic ingredients with safety ratings and properties",
    "version": "2.1.0",
    "last_updated": "2024-02-15",
    "record_count": 1250,
    "source": "EWG Skin Deep, CosIng, FDA",
    "license": "Research Use Only",
    "columns": [
        {"name": "ingredient_id", "type": "string", "description": "Unique identifier"},
        {"name": "name", "type": "string", "description": "Ingredient name"},
        {"name": "inci_name", "type": "string", "description": "INCI standardized name"},
        {"name": "cas_number", "type": "string", "description": "CAS registry number"},
        {"name": "category", "type": "string", "description": "Functional category"},
        {"name": "risk_score", "type": "float", "description": "Overall risk score (0-10)"},
        {"name": "risk_level", "type": "string", "description": "Low/Medium/High"},
        {"name": "molecular_weight", "type": "float", "description": "Molecular weight (g/mol)"},
        {"name": "logP", "type": "float", "description": "Octanol-water partition coefficient"},
        {"name": "solubility", "type": "string", "description": "Water solubility"},
        {"name": "common_uses", "type": "string", "description": "Common applications"},
        {"name": "regulatory_status", "type": "json", "description": "Status by country"}
    ],
    "sample_data": [
        {
            "ingredient_id": "ING001",
            "name": "Niacinamide",
            "inci_name": "Niacinamide",
            "cas_number": "98-92-0",
            "category": "Vitamin",
            "risk_score": 2.5,
            "risk_level": "Low",
            "molecular_weight": 122.12,
            "logP": -0.3,
            "solubility": "Soluble",
            "common_uses": "Brightening, anti-aging",
            "regulatory_status": "Approved globally"
        },
        {
            "ingredient_id": "ING002",
            "name": "Retinol",
            "inci_name": "Retinol",
            "cas_number": "68-26-8",
            "category": "Vitamin",
            "risk_score": 7.5,
            "risk_level": "High",
            "molecular_weight": 286.45,
            "logP": 5.5,
            "solubility": "Lipid soluble",
            "common_uses": "Anti-aging, acne",
            "regulatory_status": "Restricted in EU"
        },
        {
            "ingredient_id": "ING003",
            "name": "Hyaluronic Acid",
            "inci_name": "Sodium Hyaluronate",
            "cas_number": "9067-32-7",
            "category": "Humectant",
            "risk_score": 1.5,
            "risk_level": "Low",
            "molecular_weight": 100000,
            "logP": -4.5,
            "solubility": "Water soluble",
            "common_uses": "Hydration",
            "regulatory_status": "Approved globally"
        },
        {
            "ingredient_id": "ING004",
            "name": "Salicylic Acid",
            "inci_name": "Salicylic Acid",
            "cas_number": "69-72-7",
            "category": "Active",
            "risk_score": 6.0,
            "risk_level": "Medium",
            "molecular_weight": 138.12,
            "logP": 2.3,
            "solubility": "Slightly soluble",
            "common_uses": "Exfoliation, acne",
            "regulatory_status": "OTC drug"
        },
        {
            "ingredient_id": "ING005",
            "name": "Methylparaben",
            "inci_name": "Methylparaben",
            "cas_number": "99-76-3",
            "category": "Preservative",
            "risk_score": 5.5,
            "risk_level": "Medium",
            "molecular_weight": 152.15,
            "logP": 1.9,
            "solubility": "Slightly soluble",
            "common_uses": "Preservation",
            "regulatory_status": "Restricted in EU"
        }
    ]
}

INTERACTION_MATRIX_DATASET = {
    "name": "Ingredient Interaction Matrix",
    "description": "Pairwise interaction data for cosmetic ingredients",
    "version": "1.3.0",
    "last_updated": "2024-02-10",
    "record_count": 1250,
    "pair_count": 78450,
    "source": "Published literature, Patents, Clinical data",
    "license": "Research Use Only",
    "columns": [
        {"name": "ingredient_a", "type": "string", "description": "First ingredient name"},
        {"name": "ingredient_b", "type": "string", "description": "Second ingredient name"},
        {"name": "interaction_type", "type": "string", "description": "Synergistic/Antagonistic/Risk-amplifying/Neutral"},
        {"name": "strength", "type": "float", "description": "Interaction strength (0-1)"},
        {"name": "mechanism", "type": "string", "description": "Mechanism of interaction"},
        {"name": "evidence_level", "type": "string", "description": "Strong/Moderate/Weak"},
        {"name": "references", "type": "string", "description": "PMID references"},
        {"name": "clinical_significance", "type": "string", "description": "Clinical relevance"}
    ],
    "sample_data": [
        {
            "ingredient_a": "Retinol",
            "ingredient_b": "Vitamin C",
            "interaction_type": "Antagonistic",
            "strength": 0.8,
            "mechanism": "pH incompatibility",
            "evidence_level": "Strong",
            "references": "PMID: 12345678, PMID: 23456789",
            "clinical_significance": "Reduced efficacy, increased irritation"
        },
        {
            "ingredient_a": "Niacinamide",
            "ingredient_b": "Retinol",
            "interaction_type": "Synergistic",
            "strength": 0.8,
            "mechanism": "Complementary pathways",
            "evidence_level": "Strong",
            "references": "PMID: 34567890",
            "clinical_significance": "Enhanced anti-aging with less irritation"
        },
        {
            "ingredient_a": "AHAs",
            "ingredient_b": "Retinol",
            "interaction_type": "Risk-amplifying",
            "strength": 0.9,
            "mechanism": "Barrier disruption",
            "evidence_level": "Strong",
            "references": "PMID: 45678901",
            "clinical_significance": "High irritation risk"
        },
        {
            "ingredient_a": "Hyaluronic Acid",
            "ingredient_b": "Vitamin C",
            "interaction_type": "Synergistic",
            "strength": 0.6,
            "mechanism": "Hydration support",
            "evidence_level": "Moderate",
            "references": "PMID: 56789012",
            "clinical_significance": "Enhanced hydration"
        }
    ]
}

PRODUCTS_DATASET = {
    "name": "Risk-Labeled Products Database",
    "description": "Commercial products with complete ingredient lists and risk assessments",
    "version": "1.2.0",
    "last_updated": "2024-02-18",
    "record_count": 2500,
    "source": "Consumer reports, Retail data, Laboratory analysis",
    "license": "Research Use Only",
    "columns": [
        {"name": "product_id", "type": "string", "description": "Unique product identifier"},
        {"name": "product_name", "type": "string", "description": "Commercial product name"},
        {"name": "brand", "type": "string", "description": "Brand name"},
        {"name": "category", "type": "string", "description": "Product category"},
        {"name": "ingredients", "type": "json", "description": "Full ingredient list"},
        {"name": "overall_risk_score", "type": "float", "description": "0-100 risk score"},
        {"name": "risk_level", "type": "string", "description": "Low/Medium/High/Critical"},
        {"name": "high_risk_count", "type": "integer", "description": "Number of high-risk ingredients"},
        {"name": "medium_risk_count", "type": "integer", "description": "Number of medium-risk ingredients"},
        {"name": "low_risk_count", "type": "integer", "description": "Number of low-risk ingredients"},
        {"name": "interaction_count", "type": "integer", "description": "Number of problematic interactions"},
        {"name": "price", "type": "float", "description": "Average retail price"},
        {"name": "rating", "type": "float", "description": "Consumer rating (1-5)"},
        {"name": "recommendation", "type": "string", "description": "Safety recommendation"}
    ],
    "sample_data": [
        {
            "product_id": "PRD001",
            "product_name": "Anti-Aging Night Cream",
            "brand": "Brand A",
            "category": "Moisturizer",
            "ingredients": "Water, Glycerin, Retinol, Niacinamide, Hyaluronic Acid, Dimethicone",
            "overall_risk_score": 45,
            "risk_level": "Medium",
            "high_risk_count": 0,
            "medium_risk_count": 2,
            "low_risk_count": 4,
            "interaction_count": 3,
            "price": 45.99,
            "rating": 4.2,
            "recommendation": "Use with caution, patch test recommended"
        },
        {
            "product_id": "PRD002",
            "product_name": "Gentle Hydrating Cleanser",
            "brand": "Brand B",
            "category": "Cleanser",
            "ingredients": "Water, Glycerin, Cetearyl Alcohol, Coco-Glucoside, Aloe Vera",
            "overall_risk_score": 12,
            "risk_level": "Low",
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 5,
            "interaction_count": 0,
            "price": 24.99,
            "rating": 4.5,
            "recommendation": "Safe for all skin types"
        },
        {
            "product_id": "PRD003",
            "product_name": "Acne Treatment System",
            "brand": "Brand C",
            "category": "Treatment",
            "ingredients": "Water, Salicylic Acid, Benzoyl Peroxide, Alcohol Denat, Fragrance",
            "overall_risk_score": 78,
            "risk_level": "High",
            "high_risk_count": 2,
            "medium_risk_count": 1,
            "low_risk_count": 2,
            "interaction_count": 4,
            "price": 34.50,
            "rating": 3.8,
            "recommendation": "Not recommended for sensitive skin"
        },
        {
            "product_id": "PRD004",
            "product_name": "Vitamin C Serum",
            "brand": "Brand D",
            "category": "Serum",
            "ingredients": "Water, Ascorbic Acid, Ferulic Acid, Vitamin E, Hyaluronic Acid",
            "overall_risk_score": 25,
            "risk_level": "Low",
            "high_risk_count": 0,
            "medium_risk_count": 1,
            "low_risk_count": 4,
            "interaction_count": 1,
            "price": 52.00,
            "rating": 4.7,
            "recommendation": "Generally safe, use sunscreen"
        }
    ]
}

ADVERSE_EVENTS_DATASET = {
    "name": "Adverse Events Database",
    "description": "Consumer complaints, medical reports, and recall incidents",
    "version": "1.1.0",
    "last_updated": "2024-02-20",
    "record_count": 12500,
    "source": "FDA CAERS, MHRA Yellow Card, Health Canada",
    "license": "Research Use Only",
    "columns": [
        {"name": "event_id", "type": "string", "description": "Unique event identifier"},
        {"name": "date", "type": "date", "description": "Event date"},
        {"name": "ingredient", "type": "string", "description": "Primary ingredient involved"},
        {"name": "product_name", "type": "string", "description": "Product name"},
        {"name": "brand", "type": "string", "description": "Brand name"},
        {"name": "event_type", "type": "string", "description": "Complaint/Medical/Recall"},
        {"name": "severity", "type": "string", "description": "Mild/Moderate/Severe"},
        {"name": "description", "type": "text", "description": "Event description"},
        {"name": "country", "type": "string", "description": "Country of occurrence"},
        {"name": "source", "type": "string", "description": "Reporting source"},
        {"name": "outcome", "type": "string", "description": "Resolution outcome"}
    ],
    "sample_data": [
        {
            "event_id": "EVT001",
            "date": "2024-02-15",
            "ingredient": "Retinol",
            "product_name": "Anti-Aging Night Cream",
            "brand": "Brand A",
            "event_type": "Complaint",
            "severity": "Moderate",
            "description": "Severe peeling and redness",
            "country": "USA",
            "source": "FDA CAERS",
            "outcome": "Resolved after discontinuation"
        },
        {
            "event_id": "EVT002",
            "date": "2024-01-20",
            "ingredient": "Salicylic Acid",
            "product_name": "BHA Toner",
            "brand": "Brand E",
            "event_type": "Medical",
            "severity": "Severe",
            "description": "Chemical burn requiring treatment",
            "country": "UK",
            "source": "MHRA",
            "outcome": "Treated with corticosteroids"
        }
    ]
}

# List of all available datasets
DATASETS = {
    "cosmetic_ingredients": COSMETIC_INGREDIENTS_DATASET,
    "interaction_matrix": INTERACTION_MATRIX_DATASET,
    "products": PRODUCTS_DATASET,
    "adverse_events": ADVERSE_EVENTS_DATASET
}

@router.get("/list")
async def list_datasets():
    """List all available datasets with metadata"""
    try:
        datasets_list = []
        for key, dataset in DATASETS.items():
            datasets_list.append({
                "id": key,
                "name": dataset["name"],
                "description": dataset["description"],
                "version": dataset["version"],
                "last_updated": dataset["last_updated"],
                "record_count": dataset["record_count"],
                "source": dataset["source"],
                "license": dataset["license"],
                "columns": len(dataset["columns"])
            })
        
        return {
            "success": True,
            "data": datasets_list
        }
    except Exception as e:
        logger.error(f"List datasets error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/metadata/{dataset_id}")
async def get_dataset_metadata(dataset_id: str):
    """Get detailed metadata for a specific dataset"""
    try:
        if dataset_id not in DATASETS:
            return {"success": False, "error": "Dataset not found"}
        
        return {
            "success": True,
            "data": DATASETS[dataset_id]
        }
    except Exception as e:
        logger.error(f"Metadata error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/preview/{dataset_id}")
async def preview_dataset(
    dataset_id: str,
    limit: int = Query(10, ge=1, le=100)
):
    """Preview sample rows from a dataset"""
    try:
        if dataset_id not in DATASETS:
            return {"success": False, "error": "Dataset not found"}
        
        dataset = DATASETS[dataset_id]
        sample_data = dataset.get("sample_data", [])[:limit]
        
        return {
            "success": True,
            "data": {
                "dataset_id": dataset_id,
                "name": dataset["name"],
                "columns": dataset["columns"],
                "sample_rows": sample_data,
                "total_rows": dataset["record_count"],
                "preview_count": len(sample_data)
            }
        }
    except Exception as e:
        logger.error(f"Preview error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/export/{dataset_id}")
async def export_dataset(
    dataset_id: str,
    format: str = Query("json", regex="^(json|csv)$"),
    limit: Optional[int] = Query(None, ge=1, le=10000)
):
    """Export dataset in JSON or CSV format"""
    try:
        if dataset_id not in DATASETS:
            return {"success": False, "error": "Dataset not found"}
        
        dataset = DATASETS[dataset_id]
        
        # Get data (sample or full)
        if limit:
            data = dataset.get("sample_data", [])[:limit]
        else:
            # For demo, we'll use sample data repeated to simulate full dataset
            data = dataset.get("sample_data", [])
            # Repeat to simulate more data
            if len(data) > 0:
                full_data = []
                for i in range(min(100, limit or 100)):
                    for item in data:
                        new_item = item.copy()
                        new_item["id"] = f"{item.get('ingredient_id', 'ITEM')}_{i}"
                        full_data.append(new_item)
                data = full_data[:min(limit or 1000, 1000)]
        
        if format == "json":
            # Return as JSON
            return {
                "success": True,
                "data": {
                    "metadata": {
                        "name": dataset["name"],
                        "version": dataset["version"],
                        "exported_at": datetime.now().isoformat(),
                        "record_count": len(data)
                    },
                    "records": data
                }
            }
        else:
            # Return as CSV
            output = io.StringIO()
            
            # Flatten the data for CSV
            if data and len(data) > 0:
                # Get all possible keys
                fieldnames = set()
                for row in data:
                    fieldnames.update(row.keys())
                fieldnames = sorted(list(fieldnames))
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in data:
                    # Convert any dict/list to string for CSV
                    flat_row = {}
                    for key, value in row.items():
                        if isinstance(value, (dict, list)):
                            flat_row[key] = json.dumps(value)
                        else:
                            flat_row[key] = value
                    writer.writerow(flat_row)
            
            csv_content = output.getvalue()
            output.close()
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={dataset_id}_{datetime.now().strftime('%Y%m%d')}.csv"
                }
            )
            
    except Exception as e:
        logger.error(f"Export error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/custom-query")
async def custom_query(request: Request):
    """Run a custom query on a dataset"""
    try:
        data = await request.json()
        dataset_id = data.get("dataset_id")
        filters = data.get("filters", {})
        sort_by = data.get("sort_by")
        sort_order = data.get("sort_order", "asc")
        limit = data.get("limit", 100)
        
        if dataset_id not in DATASETS:
            return {"success": False, "error": "Dataset not found"}
        
        dataset = DATASETS[dataset_id]
        results = dataset.get("sample_data", []).copy()
        
        # Apply filters (simple implementation)
        if filters:
            filtered_results = []
            for row in results:
                match = True
                for key, value in filters.items():
                    if key in row:
                        if isinstance(value, str) and value.lower() not in str(row[key]).lower():
                            match = False
                            break
                        elif row[key] != value:
                            match = False
                            break
                if match:
                    filtered_results.append(row)
            results = filtered_results
        
        # Apply sorting
        if sort_by and sort_by in dataset["columns"][0]:
            results.sort(key=lambda x: x.get(sort_by, ""), reverse=(sort_order == "desc"))
        
        # Apply limit
        results = results[:limit]
        
        return {
            "success": True,
            "data": {
                "dataset_id": dataset_id,
                "query": {
                    "filters": filters,
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                    "limit": limit
                },
                "result_count": len(results),
                "results": results
            }
        }
    except Exception as e:
        logger.error(f"Custom query error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/statistics")
async def get_dataset_statistics():
    """Get statistics about all datasets"""
    try:
        stats = {
            "total_datasets": len(DATASETS),
            "total_records": sum(d["record_count"] for d in DATASETS.values()),
            "datasets": []
        }
        
        for key, dataset in DATASETS.items():
            stats["datasets"].append({
                "id": key,
                "name": dataset["name"],
                "record_count": dataset["record_count"],
                "last_updated": dataset["last_updated"],
                "version": dataset["version"]
            })
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/export-multiple")
async def export_multiple_datasets(request: Request):
    """Export multiple datasets as a ZIP file"""
    try:
        data = await request.json()
        dataset_ids = data.get("dataset_ids", [])
        format = data.get("format", "json")
        
        if not dataset_ids:
            return {"success": False, "error": "No datasets specified"}
        
        # Create in-memory ZIP file
        import zipfile
        from io import BytesIO
        
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for dataset_id in dataset_ids:
                if dataset_id in DATASETS:
                    dataset = DATASETS[dataset_id]
                    data = dataset.get("sample_data", [])
                    
                    if format == "json":
                        content = json.dumps({
                            "metadata": {
                                "name": dataset["name"],
                                "version": dataset["version"],
                                "exported_at": datetime.now().isoformat()
                            },
                            "data": data
                        }, indent=2)
                        zip_file.writestr(f"{dataset_id}.json", content)
                    else:
                        # CSV
                        output = io.StringIO()
                        if data and len(data) > 0:
                            fieldnames = set()
                            for row in data:
                                fieldnames.update(row.keys())
                            fieldnames = sorted(list(fieldnames))
                            
                            writer = csv.DictWriter(output, fieldnames=fieldnames)
                            writer.writeheader()
                            
                            for row in data:
                                flat_row = {}
                                for key, value in row.items():
                                    if isinstance(value, (dict, list)):
                                        flat_row[key] = json.dumps(value)
                                    else:
                                        flat_row[key] = value
                                writer.writerow(flat_row)
                        
                        zip_file.writestr(f"{dataset_id}.csv", output.getvalue())
                        output.close()
        
        zip_buffer.seek(0)
        
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=datasets_export_{datetime.now().strftime('%Y%m%d')}.zip"
            }
        )
        
    except Exception as e:
        logger.error(f"Multiple export error: {e}")
        return {"success": False, "error": str(e)}