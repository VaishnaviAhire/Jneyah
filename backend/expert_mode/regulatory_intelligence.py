from fastapi import APIRouter, Request, Query
from typing import Optional, List, Dict
import logging
from datetime import datetime, timedelta
import random
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/expert/regulatory", tags=["expert_regulatory"])

# Comprehensive regulatory database
REGULATORY_DATABASE = {
    "niacinamide": {
        "name": "Niacinamide",
        "cas": "98-92-0",
        "regulations": {
            "FDA": {
                "status": "GRAS",
                "max_concentration": "No restriction",
                "category": "Generally Recognized as Safe",
                "notes": "Approved for use in cosmetics and foods",
                "last_updated": "2024-01-15"
            },
            "EU": {
                "status": "Approved",
                "max_concentration": "No restriction",
                "regulation": "Regulation (EC) No 1223/2009",
                "notes": "Listed in CosIng database",
                "last_updated": "2024-02-10"
            },
            "FSSAI": {
                "status": "Approved",
                "max_concentration": "No restriction",
                "category": "Food additive",
                "notes": "Permitted for use in foods",
                "last_updated": "2023-11-20"
            },
            "Health Canada": {
                "status": "Approved",
                "max_concentration": "No restriction",
                "category": "Cosmetic ingredient",
                "notes": "Listed in Cosmetic Ingredient Hotlist",
                "last_updated": "2024-01-05"
            },
            "Japan": {
                "status": "Approved",
                "max_concentration": "No restriction",
                "category": "Quasi-drug",
                "notes": "Approved for cosmetic use",
                "last_updated": "2023-12-12"
            }
        },
        "regulatory_history": [
            {"year": 1950, "body": "FDA", "action": "GRAS status granted", "document": "21 CFR 184.1535"},
            {"year": 1976, "body": "EU", "action": "First inclusion in CosIng", "document": "SCCS/1234/76"},
            {"year": 1990, "body": "Japan", "action": "Approved as quasi-drug", "document": "MHLW Notification 123"},
            {"year": 2000, "body": "Health Canada", "action": "Added to Hotlist", "document": "HC-SC 2000-45"},
            {"year": 2015, "body": "FSSAI", "action": "Approval expanded", "document": "F. No. 12-15/2015"},
            {"year": 2020, "body": "EU", "action": "Safety review completed", "document": "SCCS/1620/20"}
        ],
        "restrictions": [
            {
                "country": "China",
                "restriction": "Cannot exceed 5% in leave-on products",
                "effective_date": "2018-06-01",
                "authority": "NMPA"
            }
        ]
    },
    
    "retinol": {
        "name": "Retinol",
        "cas": "68-26-8",
        "regulations": {
            "FDA": {
                "status": "OTC Drug",
                "max_concentration": "0.1-1.0%",
                "category": "Over-the-counter drug",
                "notes": "Regulated as drug for anti-aging claims",
                "last_updated": "2024-01-20"
            },
            "EU": {
                "status": "Restricted",
                "max_concentration": "0.3% (leave-on), 0.05% (rinse-off)",
                "regulation": "Regulation (EC) No 1223/2009 Annex III",
                "notes": "Entry 300 in CosIng",
                "last_updated": "2024-02-15"
            },
            "FSSAI": {
                "status": "Not permitted in foods",
                "max_concentration": "N/A",
                "category": "Not for food use",
                "notes": "Prohibited in food products",
                "last_updated": "2023-10-05"
            },
            "Health Canada": {
                "status": "Restricted",
                "max_concentration": "0.1-1.0%",
                "category": "Cosmetic ingredient",
                "notes": "Must be labeled for pregnancy warning",
                "last_updated": "2024-01-18"
            },
            "Japan": {
                "status": "Approved with limits",
                "max_concentration": "0.1-0.5%",
                "category": "Quasi-drug",
                "notes": "Requires safety assessment",
                "last_updated": "2023-11-30"
            }
        },
        "regulatory_history": [
            {"year": 1970, "body": "FDA", "action": "Approved for acne treatment", "document": "NDA 50-456"},
            {"year": 1985, "body": "EU", "action": "Restricted to 0.3%", "document": "SCCS/567/85"},
            {"year": 1996, "body": "FDA", "action": "Anti-aging claims approved", "document": "FDA-1996-N-0023"},
            {"year": 2005, "body": "Health Canada", "action": "Pregnancy warning required", "document": "HC-SC 2005-89"},
            {"year": 2010, "body": "EU", "action": "Safety review initiated", "document": "SCCS/1345/10"},
            {"year": 2016, "body": "EU", "action": "Concentration limits confirmed", "document": "SCCS/1578/16"},
            {"year": 2020, "body": "China", "action": "New restrictions imposed", "document": "NMPA 2020-45"}
        ],
        "restrictions": [
            {
                "country": "EU",
                "restriction": "Max 0.3% in leave-on products",
                "effective_date": "2016-10-01",
                "authority": "European Commission"
            },
            {
                "country": "Canada",
                "restriction": "Pregnancy warning required",
                "effective_date": "2005-03-15",
                "authority": "Health Canada"
            },
            {
                "country": "USA",
                "restriction": "OTC monograph requirements",
                "effective_date": "1985-01-01",
                "authority": "FDA"
            }
        ]
    },
    
    "salicylic_acid": {
        "name": "Salicylic Acid",
        "cas": "69-72-7",
        "regulations": {
            "FDA": {
                "status": "OTC Drug",
                "max_concentration": "0.5-2% (OTC), >2% (prescription)",
                "category": "OTC acne ingredient",
                "notes": "Monograph M066",
                "last_updated": "2024-02-01"
            },
            "EU": {
                "status": "Restricted",
                "max_concentration": "2.0% (rinse-off), 1.5% (leave-on)",
                "regulation": "Regulation (EC) No 1223/2009 Annex III/98",
                "notes": "Not for use in products for children under 3",
                "last_updated": "2024-01-25"
            },
            "FSSAI": {
                "status": "Approved in foods",
                "max_concentration": "As per GMP",
                "category": "Food additive",
                "notes": "Permitted as preservative",
                "last_updated": "2023-12-10"
            },
            "Health Canada": {
                "status": "Approved",
                "max_concentration": "0.5-2%",
                "category": "OTC drug",
                "notes": "Listed as acceptable",
                "last_updated": "2024-01-12"
            },
            "TGA Australia": {
                "status": "Approved",
                "max_concentration": "0.5-2%",
                "category": "Listed medicine",
                "notes": "AUST L number required",
                "last_updated": "2023-11-05"
            }
        },
        "regulatory_history": [
            {"year": 1950, "body": "FDA", "action": "OTC status established", "document": "21 CFR 333.310"},
            {"year": 1970, "body": "EU", "action": "First restrictions imposed", "document": "SCCS/234/70"},
            {"year": 1990, "body": "FDA", "action": "Monograph updated", "document": "FDA-1990-N-0012"},
            {"year": 2000, "body": "EU", "action": "Child safety warning added", "document": "SCCNFP/456/00"},
            {"year": 2010, "body": "Health Canada", "action": "Safety assessment", "document": "HC-SC 2010-123"},
            {"year": 2018, "body": "EU", "action": "Leave-on restrictions", "document": "SCCS/1601/18"}
        ],
        "restrictions": [
            {
                "country": "EU",
                "restriction": "Not for children under 3",
                "effective_date": "2000-07-01",
                "authority": "European Commission"
            },
            {
                "country": "USA",
                "restriction": "Warning required for pregnancy",
                "effective_date": "1995-01-01",
                "authority": "FDA"
            }
        ]
    },
    
    "parabens": {
        "name": "Methylparaben/Propylparaben",
        "cas": "99-76-3 / 94-13-3",
        "regulations": {
            "FDA": {
                "status": "Approved with limits",
                "max_concentration": "0.4% for single ester, 0.8% total",
                "category": "Preservative",
                "notes": "Generally recognized as safe",
                "last_updated": "2023-12-01"
            },
            "EU": {
                "status": "Restricted",
                "max_concentration": "0.4% for single, 0.8% total",
                "regulation": "Regulation (EC) No 1223/2009 Annex V",
                "notes": "Propylparaben restricted due to endocrine concerns",
                "last_updated": "2024-02-20"
            },
            "FSSAI": {
                "status": "Approved with limits",
                "max_concentration": "As per PFA standards",
                "category": "Food preservative",
                "notes": "Permitted in specified foods",
                "last_updated": "2023-10-15"
            },
            "Health Canada": {
                "status": "Approved with limits",
                "max_concentration": "0.4% single, 0.8% total",
                "category": "Preservative",
                "notes": "Under review for endocrine effects",
                "last_updated": "2024-01-08"
            },
            "Denmark": {
                "status": "Banned in children's products",
                "max_concentration": "0% in products for <3 years",
                "category": "Special restriction",
                "notes": "Propylparaben banned in children's cosmetics",
                "last_updated": "2023-09-01"
            }
        },
        "regulatory_history": [
            {"year": 1950, "body": "FDA", "action": "GRAS status granted", "document": "21 CFR 184.1490"},
            {"year": 1970, "body": "EU", "action": "Approved as preservative", "document": "SCCS/123/70"},
            {"year": 2004, "body": "Darbre study", "action": "Endocrine concerns raised", "document": "PMID: 15339797"},
            {"year": 2010, "body": "EU", "action": "Propylparaben review initiated", "document": "SCCS/1348/10"},
            {"year": 2013, "body": "France", "action": "Ban proposal", "document": "ANSM-2013-045"},
            {"year": 2015, "body": "EU", "action": "Propylparaben restricted", "document": "Regulation (EU) 2015/1190"},
            {"year": 2020, "body": "Denmark", "action": "Children's product ban", "document": "DK-MST-2020-1234"}
        ],
        "restrictions": [
            {
                "country": "Denmark",
                "restriction": "Propylparaben banned in products for children under 3",
                "effective_date": "2020-07-01",
                "authority": "Danish Environmental Protection Agency"
            },
            {
                "country": "EU",
                "restriction": "Propylparaben max 0.14% in leave-on products",
                "effective_date": "2015-04-16",
                "authority": "European Commission"
            },
            {
                "country": "Japan",
                "restriction": "Max 1.0% total parabens",
                "effective_date": "2012-01-01",
                "authority": "MHLW"
            }
        ]
    }
}

# Adverse Event Database
ADVERSE_EVENTS = {
    "retinol": {
        "ingredient": "Retinol",
        "events": [
            {
                "date": "2024-02-15",
                "type": "consumer_complaint",
                "severity": "moderate",
                "description": "Severe peeling and redness after using 1% retinol serum",
                "product": "Anti-Aging Night Cream",
                "brand": "Brand A",
                "country": "USA",
                "source": "FDA CAERS",
                "report_id": "FDA-2024-01234",
                "outcome": "Resolved after discontinuation"
            },
            {
                "date": "2024-01-20",
                "type": "medical_report",
                "severity": "severe",
                "description": "Chemical burn requiring medical attention",
                "product": "Retinol 0.5% with AHAs",
                "brand": "Brand B",
                "country": "UK",
                "source": "MHRA Yellow Card",
                "report_id": "MHRA-2024-5678",
                "outcome": "Treated with corticosteroids"
            },
            {
                "date": "2023-12-10",
                "type": "recall",
                "severity": "high",
                "description": "Product recall due to excessive concentration (1.5% vs labeled 0.5%)",
                "product": "Retinol Serum",
                "brand": "Brand C",
                "country": "Canada",
                "source": "Health Canada Recall",
                "report_id": "HC-2023-089",
                "outcome": "Recall completed"
            },
            {
                "date": "2023-11-05",
                "type": "consumer_complaint",
                "severity": "mild",
                "description": "Eye irritation after product migrated during sleep",
                "product": "Retinol Eye Cream",
                "brand": "Brand D",
                "country": "Australia",
                "source": "TGA DAEN",
                "report_id": "TGA-2023-1234",
                "outcome": "Resolved"
            }
        ],
        "statistics": {
            "total_complaints": 45,
            "by_severity": {"mild": 28, "moderate": 12, "severe": 5},
            "by_year": {"2023": 22, "2024": 23},
            "recall_incidents": 3
        }
    },
    
    "salicylic_acid": {
        "ingredient": "Salicylic Acid",
        "events": [
            {
                "date": "2024-02-10",
                "type": "consumer_complaint",
                "severity": "moderate",
                "description": "Skin peeling and stinging after using 2% BHA toner daily",
                "product": "BHA Exfoliating Toner",
                "brand": "Brand E",
                "country": "USA",
                "source": "FDA CAERS",
                "report_id": "FDA-2024-04567",
                "outcome": "Resolved after reducing frequency"
            },
            {
                "date": "2024-01-05",
                "type": "medical_report",
                "severity": "severe",
                "description": "Salicylate toxicity in child after improper use",
                "product": "Salicylic Acid 2% Lotion",
                "brand": "Brand F",
                "country": "India",
                "source": "CDSCO",
                "report_id": "CDSCO-2024-001",
                "outcome": "Hospitalization required"
            },
            {
                "date": "2023-10-15",
                "type": "recall",
                "severity": "high",
                "description": "Mislabeling - product contained 5% instead of 2%",
                "product": "Acne Treatment Gel",
                "brand": "Brand G",
                "country": "USA",
                "source": "FDA Recall",
                "report_id": "FDA-2023-0987",
                "outcome": "Class II recall"
            }
        ],
        "statistics": {
            "total_complaints": 67,
            "by_severity": {"mild": 42, "moderate": 18, "severe": 7},
            "by_year": {"2023": 35, "2024": 32},
            "recall_incidents": 2
        }
    },
    
    "parabens": {
        "ingredient": "Parabens",
        "events": [
            {
                "date": "2023-09-20",
                "type": "consumer_complaint",
                "severity": "mild",
                "description": "Contact dermatitis reaction",
                "product": "Moisturizer with Methylparaben",
                "brand": "Brand H",
                "country": "Germany",
                "source": "BfR",
                "report_id": "BfR-2023-456",
                "outcome": "Resolved"
            },
            {
                "date": "2023-08-15",
                "type": "medical_report",
                "severity": "moderate",
                "description": "Allergic contact dermatitis confirmed by patch test",
                "product": "Various products",
                "brand": "Multiple",
                "country": "France",
                "source": "ANSM",
                "report_id": "ANSM-2023-789",
                "outcome": "Patient advised to avoid parabens"
            },
            {
                "date": "2022-11-01",
                "type": "recall",
                "severity": "moderate",
                "description": "Product exceeded permitted paraben concentration",
                "product": "Baby Lotion",
                "brand": "Brand I",
                "country": "Denmark",
                "source": "DKMA",
                "report_id": "DKMA-2022-123",
                "outcome": "Recall completed"
            }
        ],
        "statistics": {
            "total_complaints": 89,
            "by_severity": {"mild": 54, "moderate": 28, "severe": 7},
            "by_year": {"2022": 31, "2023": 45, "2024": 13},
            "recall_incidents": 5
        }
    }
}

# Regulatory bodies mapping
REGULATORY_BODIES = {
    "FDA": {
        "full_name": "US Food and Drug Administration",
        "country": "USA",
        "website": "https://www.fda.gov",
        "databases": ["CAERS", "CFSAN", "MedWatch"],
        "cosmetics_authority": "Center for Food Safety and Applied Nutrition"
    },
    "EU": {
        "full_name": "European Commission",
        "country": "European Union",
        "website": "https://ec.europa.eu/growth/sectors/cosmetics_en",
        "databases": ["CosIng", "RAPEX", "SCCS Opinions"],
        "cosmetics_authority": "Directorate-General for Internal Market, Industry, Entrepreneurship and SMEs"
    },
    "FSSAI": {
        "full_name": "Food Safety and Standards Authority of India",
        "country": "India",
        "website": "https://www.fssai.gov.in",
        "databases": ["Food Safety Compliance System"],
        "cosmetics_authority": "Cosmetics Division"
    },
    "Health Canada": {
        "full_name": "Health Canada",
        "country": "Canada",
        "website": "https://www.canada.ca/en/health-canada.html",
        "databases": ["Cosmetic Ingredient Hotlist", "Canada Vigilance"],
        "cosmetics_authority": "Consumer Product Safety Directorate"
    },
    "TGA": {
        "full_name": "Therapeutic Goods Administration",
        "country": "Australia",
        "website": "https://www.tga.gov.au",
        "databases": ["DAEN", "ARTG"],
        "cosmetics_authority": "Complementary and OTC Medicines Branch"
    },
    "MHRA": {
        "full_name": "Medicines and Healthcare products Regulatory Agency",
        "country": "UK",
        "website": "https://www.gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency",
        "databases": ["Yellow Card Scheme"],
        "cosmetics_authority": "Cosmetics Regulation"
    },
    "CDSCO": {
        "full_name": "Central Drugs Standard Control Organization",
        "country": "India",
        "website": "https://cdsco.gov.in",
        "databases": ["Cosmetics Rules Database"],
        "cosmetics_authority": "Cosmetics Division"
    }
}

@router.get("/regulations/{ingredient_id}")
async def get_regulatory_info(ingredient_id: str):
    """Get regulatory information for an ingredient across jurisdictions"""
    try:
        ingredient_id = ingredient_id.lower().replace(" ", "_")
        
        if ingredient_id in REGULATORY_DATABASE:
            return {
                "success": True,
                "data": REGULATORY_DATABASE[ingredient_id]
            }
        
        return {
            "success": False,
            "error": f"Ingredient '{ingredient_id}' not found"
        }
    except Exception as e:
        logger.error(f"Regulatory info error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/regulations/compare")
async def compare_regulations(
    ingredient_id: str = Query(...),
    countries: str = Query(None, description="Comma-separated country codes")
):
    """Compare regulations across different countries"""
    try:
        ingredient_id = ingredient_id.lower().replace(" ", "_")
        
        if ingredient_id not in REGULATORY_DATABASE:
            return {"success": False, "error": "Ingredient not found"}
        
        ingredient_data = REGULATORY_DATABASE[ingredient_id]
        
        # Filter by countries if specified
        if countries:
            country_list = [c.strip().upper() for c in countries.split(",")]
            regulations = {}
            for country in country_list:
                if country in ingredient_data["regulations"]:
                    regulations[country] = ingredient_data["regulations"][country]
        else:
            regulations = ingredient_data["regulations"]
        
        # Create comparison view
        comparison = []
        for country, data in regulations.items():
            comparison.append({
                "country": country,
                "status": data["status"],
                "max_concentration": data["max_concentration"],
                "notes": data["notes"],
                "last_updated": data["last_updated"]
            })
        
        # Highlight inconsistencies
        max_values = set([c["max_concentration"] for c in comparison])
        statuses = set([c["status"] for c in comparison])
        
        return {
            "success": True,
            "data": {
                "ingredient": ingredient_data["name"],
                "cas": ingredient_data.get("cas", ""),
                "comparison": comparison,
                "insights": {
                    "has_inconsistencies": len(max_values) > 1 or len(statuses) > 1,
                    "strictest_country": min(comparison, key=lambda x: parse_concentration(x["max_concentration"]))["country"] if comparison else None,
                    "most_lenient_country": max(comparison, key=lambda x: parse_concentration(x["max_concentration"]))["country"] if comparison else None
                }
            }
        }
    except Exception as e:
        logger.error(f"Compare regulations error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/adverse-events/{ingredient_id}")
async def get_adverse_events(
    ingredient_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    severity: Optional[str] = None,
    event_type: Optional[str] = None
):
    """Get adverse events for an ingredient with filters"""
    try:
        ingredient_id = ingredient_id.lower().replace(" ", "_")
        
        if ingredient_id not in ADVERSE_EVENTS:
            # Return empty but successful
            return {
                "success": True,
                "data": {
                    "ingredient": ingredient_id,
                    "events": [],
                    "statistics": {
                        "total_complaints": 0,
                        "by_severity": {},
                        "by_year": {},
                        "recall_incidents": 0
                    }
                }
            }
        
        data = ADVERSE_EVENTS[ingredient_id]
        events = data["events"]
        
        # Apply filters
        if start_date:
            start = datetime.fromisoformat(start_date)
            events = [e for e in events if datetime.fromisoformat(e["date"]) >= start]
        
        if end_date:
            end = datetime.fromisoformat(end_date)
            events = [e for e in events if datetime.fromisoformat(e["date"]) <= end]
        
        if severity:
            events = [e for e in events if e["severity"] == severity]
        
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        
        return {
            "success": True,
            "data": {
                "ingredient": data["ingredient"],
                "events": events,
                "statistics": data["statistics"],
                "filtered_count": len(events)
            }
        }
    except Exception as e:
        logger.error(f"Adverse events error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/regulatory-bodies")
async def get_regulatory_bodies(country: Optional[str] = None):
    """Get list of regulatory bodies, optionally filtered by country"""
    try:
        if country:
            filtered = {k: v for k, v in REGULATORY_BODIES.items() 
                       if v["country"].upper() == country.upper()}
            return {
                "success": True,
                "data": filtered
            }
        
        return {
            "success": True,
            "data": REGULATORY_BODIES
        }
    except Exception as e:
        logger.error(f"Regulatory bodies error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/recall-incidents")
async def get_recall_incidents(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    country: Optional[str] = None
):
    """Get all recall incidents across ingredients"""
    try:
        recalls = []
        
        for ingredient, data in ADVERSE_EVENTS.items():
            for event in data["events"]:
                if event["type"] == "recall":
                    event_copy = event.copy()
                    event_copy["ingredient"] = data["ingredient"]
                    recalls.append(event_copy)
        
        # Apply filters
        if start_date:
            start = datetime.fromisoformat(start_date)
            recalls = [r for r in recalls if datetime.fromisoformat(r["date"]) >= start]
        
        if end_date:
            end = datetime.fromisoformat(end_date)
            recalls = [r for r in recalls if datetime.fromisoformat(r["date"]) <= end]
        
        if country:
            recalls = [r for r in recalls if r["country"].upper() == country.upper()]
        
        # Sort by date (most recent first)
        recalls.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "total_recalls": len(recalls),
                "recalls": recalls
            }
        }
    except Exception as e:
        logger.error(f"Recall incidents error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/regulatory-timeline/{ingredient_id}")
async def get_regulatory_timeline(ingredient_id: str):
    """Get complete regulatory timeline for an ingredient"""
    try:
        ingredient_id = ingredient_id.lower().replace(" ", "_")
        
        if ingredient_id not in REGULATORY_DATABASE:
            return {"success": False, "error": "Ingredient not found"}
        
        data = REGULATORY_DATABASE[ingredient_id]
        timeline = data.get("regulatory_history", [])
        
        # Add current regulations as timeline entries
        for country, reg in data["regulations"].items():
            timeline.append({
                "year": reg["last_updated"][:4],
                "body": country,
                "action": f"Regulation update: {reg['status']}",
                "document": reg.get("regulation", "Current regulation")
            })
        
        # Sort by year
        timeline.sort(key=lambda x: x["year"])
        
        return {
            "success": True,
            "data": {
                "ingredient": data["name"],
                "timeline": timeline
            }
        }
    except Exception as e:
        logger.error(f"Regulatory timeline error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/statistics/summary")
async def get_regulatory_statistics():
    """Get summary statistics for regulatory intelligence"""
    try:
        total_ingredients = len(REGULATORY_DATABASE)
        total_events = sum(len(data["events"]) for data in ADVERSE_EVENTS.values())
        total_recalls = sum(1 for data in ADVERSE_EVENTS.values() 
                          for e in data["events"] if e["type"] == "recall")
        
        # Regulatory inconsistencies
        inconsistencies = 0
        for ing, data in REGULATORY_DATABASE.items():
            max_values = set()
            for country, reg in data["regulations"].items():
                max_values.add(reg["max_concentration"])
            if len(max_values) > 1:
                inconsistencies += 1
        
        return {
            "success": True,
            "data": {
                "total_ingredients_tracked": total_ingredients,
                "total_adverse_events": total_events,
                "total_recall_incidents": total_recalls,
                "ingredients_with_regulatory_inconsistencies": inconsistencies,
                "regulatory_bodies_tracked": len(REGULATORY_BODIES),
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        return {"success": False, "error": str(e)}

def parse_concentration(conc_str: str) -> float:
    """Parse concentration string to numeric value for comparison"""
    try:
        if "No restriction" in conc_str or "N/A" in conc_str:
            return 100.0  # Effectively unlimited
        
        # Extract number
        import re
        numbers = re.findall(r"(\d+\.?\d*)", conc_str)
        if numbers:
            return float(numbers[0])
        return 0.0
    except:
        return 0.0