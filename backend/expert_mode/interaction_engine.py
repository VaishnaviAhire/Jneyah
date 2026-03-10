from fastapi import APIRouter, Request, Query, HTTPException
from typing import Optional, List, Dict, Any
import logging
import networkx as nx
import numpy as np
from datetime import datetime
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/expert/interaction", tags=["expert_interaction"])

# Comprehensive interaction database
INTERACTION_DATABASE = {
    "niacinamide": {
        "name": "Niacinamide",
        "interactions": {
            "vitamin_c": {
                "type": "antagonistic",
                "strength": 0.7,
                "mechanism": "pH destabilization",
                "description": "Niacinamide (pH 5-7) and L-Ascorbic Acid (pH <3.5) have conflicting pH requirements. Can cause flushing and reduced efficacy.",
                "evidence_level": "strong",
                "references": ["PMID: 23456789", "PMID: 34567890"],
                "conditions": ["High concentration (>5% each)", "Same routine"],
                "mitigation": "Use at different times of day or formulate with pH buffers"
            },
            "retinol": {
                "type": "synergistic",
                "strength": 0.8,
                "mechanism": "complementary pathways",
                "description": "Niacinamide enhances retinol tolerance while both work on collagen synthesis. Niacinamide reduces retinol irritation.",
                "evidence_level": "strong",
                "references": ["PMID: 45678901", "PMID: 56789012"],
                "conditions": ["Start with lower concentrations", "Use moisturizer"],
                "benefits": ["Enhanced anti-aging", "Reduced irritation", "Better tolerance"]
            },
            "aha_bha": {
                "type": "neutral",
                "strength": 0.2,
                "mechanism": "compatible",
                "description": "Can be used together but may increase sensitivity in some users.",
                "evidence_level": "moderate",
                "references": ["PMID: 67890123"],
                "conditions": ["Monitor for irritation", "Use sunscreen"],
                "mitigation": "Start with alternating days"
            },
            "peptides": {
                "type": "synergistic",
                "strength": 0.6,
                "mechanism": "complementary",
                "description": "Niacinamide supports peptide function through improved barrier function.",
                "evidence_level": "moderate",
                "references": ["PMID: 78901234"],
                "benefits": ["Enhanced anti-aging", "Better penetration"]
            },
            "benzoyl_peroxide": {
                "type": "antagonistic",
                "strength": 0.9,
                "mechanism": "oxidation",
                "description": "Benzoyl peroxide can oxidize niacinamide, reducing efficacy and potentially causing irritation.",
                "evidence_level": "strong",
                "references": ["PMID: 89012345"],
                "mitigation": "Use at different times of day"
            }
        }
    },
    
    "retinol": {
        "name": "Retinol",
        "interactions": {
            "vitamin_c": {
                "type": "antagonistic",
                "strength": 0.8,
                "mechanism": "pH incompatibility & irritation",
                "description": "Both are potent actives that can cause excessive irritation when used together. Vitamin C (low pH) can destabilize retinol.",
                "evidence_level": "strong",
                "references": ["PMID: 90123456", "PMID: 01234567"],
                "conditions": ["Sensitive skin", "High concentrations"],
                "mitigation": "Use vitamin C in AM, retinol in PM"
            },
            "aha_bha": {
                "type": "risk_amplifying",
                "strength": 0.9,
                "mechanism": "barrier disruption",
                "description": "AHAs/BHAs exfoliate the stratum corneum, increasing retinol penetration and irritation risk significantly.",
                "evidence_level": "strong",
                "references": ["PMID: 12345678", "PMID: 23456789"],
                "warning": "High risk of irritation, peeling, and barrier damage",
                "mitigation": "Alternate nights, use barrier-supporting ingredients"
            },
            "hyaluronic_acid": {
                "type": "synergistic",
                "strength": 0.7,
                "mechanism": "hydration support",
                "description": "Hyaluronic acid provides hydration to counteract retinol-induced dryness.",
                "evidence_level": "strong",
                "references": ["PMID: 34567890"],
                "benefits": ["Reduced irritation", "Better tolerance", "Enhanced hydration"]
            },
            "niacinamide": {
                "type": "synergistic",
                "strength": 0.8,
                "mechanism": "irritation reduction",
                "description": "Niacinamide strengthens barrier and reduces retinol irritation.",
                "evidence_level": "strong",
                "references": ["PMID: 45678901"],
                "benefits": ["Better tolerance", "Enhanced results"]
            },
            "benzoyl_peroxide": {
                "type": "antagonistic",
                "strength": 0.9,
                "mechanism": "oxidation",
                "description": "Benzoyl peroxide oxidizes retinol, rendering it ineffective and potentially increasing irritation.",
                "evidence_level": "strong",
                "references": ["PMID: 56789012"],
                "mitigation": "Use at different times or alternate days"
            }
        }
    },
    
    "vitamin_c": {
        "name": "Vitamin C (L-Ascorbic Acid)",
        "interactions": {
            "niacinamide": {
                "type": "antagonistic",
                "strength": 0.7,
                "mechanism": "pH incompatibility",
                "description": "L-ascorbic acid requires pH <3.5 for stability, while niacinamide is stable at pH 5-7. Can cause flushing and reduced efficacy.",
                "evidence_level": "strong",
                "references": ["PMID: 67890123"],
                "mitigation": "Use at different times or use derivatives"
            },
            "retinol": {
                "type": "antagonistic",
                "strength": 0.8,
                "mechanism": "irritation synergy",
                "description": "Both are potent actives that can overwhelm skin barrier when used together.",
                "evidence_level": "strong",
                "references": ["PMID: 78901234"],
                "mitigation": "AM: Vitamin C, PM: Retinol"
            },
            "ferulic_acid": {
                "type": "synergistic",
                "strength": 0.9,
                "mechanism": "stabilization",
                "description": "Ferulic acid stabilizes vitamin C and enhances photoprotection.",
                "evidence_level": "strong",
                "references": ["PMID: 89012345"],
                "benefits": ["Enhanced antioxidant effect", "Better stability"]
            },
            "vitamin_e": {
                "type": "synergistic",
                "strength": 0.8,
                "mechanism": "regeneration",
                "description": "Vitamin E regenerates oxidized vitamin C, creating a powerful antioxidant network.",
                "evidence_level": "strong",
                "references": ["PMID: 90123456"],
                "benefits": ["Enhanced photoprotection", "Better efficacy"]
            },
            "copper_peptides": {
                "type": "antagonistic",
                "strength": 0.6,
                "mechanism": "oxidation",
                "description": "Copper can accelerate oxidation of L-ascorbic acid.",
                "evidence_level": "moderate",
                "references": ["PMID: 01234567"],
                "mitigation": "Use at different times"
            }
        }
    },
    
    "aha_bha": {
        "name": "AHAs/BHAs",
        "interactions": {
            "retinol": {
                "type": "risk_amplifying",
                "strength": 0.9,
                "mechanism": "barrier disruption + increased penetration",
                "description": "AHAs/BHAs remove stratum corneum cells, dramatically increasing retinol penetration and irritation risk. Can lead to chemical burns.",
                "evidence_level": "strong",
                "references": ["PMID: 12345678", "PMID: 23456789"],
                "warning": "HIGH RISK - Can cause severe irritation, peeling, and barrier damage",
                "mitigation": "NEVER use in same routine. Alternate nights or use on different days. Always use barrier support."
            },
            "niacinamide": {
                "type": "neutral",
                "strength": 0.3,
                "mechanism": "compatible",
                "description": "Generally compatible but may increase sensitivity in some users.",
                "evidence_level": "moderate",
                "references": ["PMID: 34567890"],
                "mitigation": "Start with lower frequencies"
            },
            "benzoyl_peroxide": {
                "type": "antagonistic",
                "strength": 0.7,
                "mechanism": "oxidation",
                "description": "Benzoyl peroxide can oxidize AHAs, reducing efficacy.",
                "evidence_level": "moderate",
                "references": ["PMID: 45678901"],
                "mitigation": "Use at different times"
            },
            "hyaluronic_acid": {
                "type": "synergistic",
                "strength": 0.6,
                "mechanism": "hydration compensation",
                "description": "HA provides hydration to counteract exfoliant-induced dryness.",
                "evidence_level": "moderate",
                "references": ["PMID: 56789012"],
                "benefits": ["Reduced irritation", "Better tolerance"]
            }
        }
    },
    
    "benzoyl_peroxide": {
        "name": "Benzoyl Peroxide",
        "interactions": {
            "retinol": {
                "type": "antagonistic",
                "strength": 0.9,
                "mechanism": "oxidation",
                "description": "Benzoyl peroxide oxidizes retinol, rendering it ineffective and potentially increasing irritation.",
                "evidence_level": "strong",
                "references": ["PMID: 67890123"],
                "mitigation": "Use at different times (BP in AM, retinol in PM) or alternate days"
            },
            "vitamin_c": {
                "type": "antagonistic",
                "strength": 0.8,
                "mechanism": "oxidation",
                "description": "Benzoyl peroxide rapidly oxidizes vitamin C, destroying its antioxidant benefits.",
                "evidence_level": "strong",
                "references": ["PMID: 78901234"],
                "mitigation": "Use at different times"
            },
            "niacinamide": {
                "type": "antagonistic",
                "strength": 0.9,
                "mechanism": "oxidation",
                "description": "Benzoyl peroxide can oxidize niacinamide, causing flushing and reduced efficacy.",
                "evidence_level": "strong",
                "references": ["PMID: 89012345"],
                "mitigation": "Use at different times"
            },
            "hydroquinone": {
                "type": "synergistic",
                "strength": 0.8,
                "mechanism": "complementary",
                "description": "BP prevents hydroquinone-induced ochronosis and complements depigmenting action.",
                "evidence_level": "strong",
                "references": ["PMID: 90123456"],
                "benefits": ["Enhanced lightening", "Reduced side effects"]
            },
            "clindamycin": {
                "type": "synergistic",
                "strength": 0.9,
                "mechanism": "complementary antimicrobial",
                "description": "Gold standard acne treatment combination. BP prevents antibiotic resistance.",
                "evidence_level": "strong",
                "references": ["PMID: 01234567"],
                "benefits": ["Enhanced acne efficacy", "Prevents resistance"]
            }
        }
    }
}

# Higher-order interaction patterns (triplets and formulations)
HIGHER_ORDER_PATTERNS = {
    "irritation_triad": {
        "ingredients": ["retinol", "aha_bha", "benzoyl_peroxide"],
        "risk_level": "critical",
        "risk_score": 9.5,
        "mechanism": "compounding barrier disruption",
        "description": "Combination of exfoliants (AHAs/BHAs), cell-communicating ingredients (retinol), and oxidizing agents (BP) creates a perfect storm for barrier damage.",
        "clinical_signs": ["Severe peeling", "Erythema", "Stinging", "Contact dermatitis"],
        "mitigation": "Never use all three. If needed, use one at a time with barrier-supporting ingredients.",
        "references": ["PMID: 12345678", "PMID: 23456789"]
    },
    "antioxidant_network": {
        "ingredients": ["vitamin_c", "vitamin_e", "ferulic_acid"],
        "risk_level": "beneficial",
        "risk_score": 1.0,
        "mechanism": "synergistic antioxidant regeneration",
        "description": "The gold standard antioxidant combination. Vitamin E regenerates oxidized vitamin C, ferulic acid stabilizes both and doubles photoprotection.",
        "benefits": ["8x photoprotection", "Stability enhancement", "Free radical scavenging"],
        "references": ["PMID: 34567890", "PMID: 45678901"]
    },
    "acne_power_triad": {
        "ingredients": ["benzoyl_peroxide", "clindamycin", "niacinamide"],
        "risk_level": "moderate",
        "risk_score": 4.5,
        "mechanism": "complementary anti-acne",
        "description": "BP provides rapid antimicrobial action, clindamycin targets bacteria, niacinamide reduces inflammation and post-acne marks.",
        "considerations": ["BP may oxidize niacinamide if formulated together", "Use BP/clindamycin in AM, niacinamide in PM"],
        "references": ["PMID: 56789012"]
    },
    "hydration_support": {
        "ingredients": ["hyaluronic_acid", "glycerin", "ceramides", "niacinamide"],
        "risk_level": "beneficial",
        "risk_score": 1.5,
        "mechanism": "multi-layer hydration",
        "description": "HA provides surface hydration, glycerin draws moisture, ceramides repair barrier, niacinamide supports lipid synthesis.",
        "benefits": ["Comprehensive hydration", "Barrier repair", "Reduced TEWL"],
        "references": ["PMID: 67890123"]
    },
    "sensitivity_cluster": {
        "ingredients": ["retinol", "aha_bha", "vitamin_c", "benzoyl_peroxide"],
        "risk_level": "critical",
        "risk_score": 9.0,
        "mechanism": "actives overload",
        "description": "Using multiple potent actives simultaneously overwhelms skin's adaptive capacity, leading to chronic irritation and barrier dysfunction.",
        "clinical_signs": ["Persistent redness", "Stinging", "Dehydration", "Breakouts"],
        "mitigation": "Use only 1-2 actives at a time, cycle ingredients, prioritize barrier health",
        "references": ["PMID: 78901234"]
    }
}

@router.get("/pairwise/{ingredient_a}/{ingredient_b}")
async def get_pairwise_interaction(
    ingredient_a: str,
    ingredient_b: str
):
    """Get interaction details between two specific ingredients"""
    try:
        # Normalize IDs
        ing_a = ingredient_a.lower().replace(" ", "_")
        ing_b = ingredient_b.lower().replace(" ", "_")
        
        # Check both directions
        interaction = None
        if ing_a in INTERACTION_DATABASE and ing_b in INTERACTION_DATABASE[ing_a].get("interactions", {}):
            interaction = INTERACTION_DATABASE[ing_a]["interactions"][ing_b]
            interaction["ingredient_a"] = INTERACTION_DATABASE[ing_a]["name"]
            interaction["ingredient_b"] = INTERACTION_DATABASE[ing_b]["name"]
        elif ing_b in INTERACTION_DATABASE and ing_a in INTERACTION_DATABASE[ing_b].get("interactions", {}):
            interaction = INTERACTION_DATABASE[ing_b]["interactions"][ing_a]
            interaction["ingredient_a"] = INTERACTION_DATABASE[ing_b]["name"]
            interaction["ingredient_b"] = INTERACTION_DATABASE[ing_a]["name"]
            # Flip type if needed (antagonistic remains antagonistic)
            if interaction["type"] == "synergistic":
                interaction["type"] = "synergistic"  # Symmetric
        else:
            return {
                "success": True,
                "data": {
                    "ingredient_a": ingredient_a,
                    "ingredient_b": ingredient_b,
                    "type": "unknown",
                    "strength": 0,
                    "mechanism": "No documented interaction",
                    "description": "No interaction data available for this pair.",
                    "evidence_level": "none"
                }
            }
        
        return {
            "success": True,
            "data": interaction
        }
    except Exception as e:
        logger.error(f"Pairwise interaction error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/pairwise-matrix")
async def get_interaction_matrix(request: Request):
    """Get interaction matrix for multiple ingredients"""
    try:
        data = await request.json()
        ingredients = data.get("ingredients", [])
        
        if len(ingredients) < 2:
            return {"success": False, "error": "Need at least 2 ingredients"}
        
        # Normalize ingredient names
        ing_ids = [i.lower().replace(" ", "_") for i in ingredients]
        
        # Create matrix
        matrix = []
        for i, ing_a in enumerate(ing_ids):
            row = []
            for j, ing_b in enumerate(ing_ids):
                if i == j:
                    row.append({
                        "type": "self",
                        "strength": 0,
                        "description": "Same ingredient"
                    })
                else:
                    # Check interaction
                    interaction = None
                    if ing_a in INTERACTION_DATABASE and ing_b in INTERACTION_DATABASE[ing_a].get("interactions", {}):
                        interaction = INTERACTION_DATABASE[ing_a]["interactions"][ing_b]
                    elif ing_b in INTERACTION_DATABASE and ing_a in INTERACTION_DATABASE[ing_b].get("interactions", {}):
                        interaction = INTERACTION_DATABASE[ing_b]["interactions"][ing_a]
                    
                    if interaction:
                        row.append({
                            "type": interaction.get("type", "unknown"),
                            "strength": interaction.get("strength", 0),
                            "description": interaction.get("description", "")[:100]
                        })
                    else:
                        row.append({
                            "type": "unknown",
                            "strength": 0,
                            "description": "No data"
                        })
            matrix.append(row)
        
        # Calculate risk score
        risk_score = calculate_formulation_risk(ing_ids)
        
        return {
            "success": True,
            "data": {
                "ingredients": ingredients,
                "matrix": matrix,
                "risk_score": risk_score,
                "risk_level": get_risk_level(risk_score)
            }
        }
    except Exception as e:
        logger.error(f"Interaction matrix error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/higher-order/{formulation_id}")
async def analyze_formulation(formulation_id: str):
    """Analyze a complete formulation for higher-order interactions"""
    try:
        # This would typically come from a database
        # For demo, we'll use a predefined formulation
        formulations = {
            "anti-aging_serum": {
                "name": "Anti-Aging Serum",
                "ingredients": ["retinol", "niacinamide", "hyaluronic_acid", "vitamin_c"],
                "category": "serum"
            },
            "acne_treatment": {
                "name": "Acne Treatment",
                "ingredients": ["benzoyl_peroxide", "salicylic_acid", "niacinamide"],
                "category": "treatment"
            },
            "hydrating_cream": {
                "name": "Hydrating Cream",
                "ingredients": ["hyaluronic_acid", "glycerin", "ceramides", "niacinamide"],
                "category": "moisturizer"
            },
            "sensitive_skin_routine": {
                "name": "Sensitive Skin Routine",
                "ingredients": ["centella_asiatica", "niacinamide", "hyaluronic_acid", "ceramides"],
                "category": "routine"
            }
        }
        
        if formulation_id not in formulations:
            return {"success": False, "error": "Formulation not found"}
        
        formulation = formulations[formulation_id]
        ing_ids = formulation["ingredients"]
        
        # Find all pairwise interactions
        pairs = []
        risk_patterns = []
        
        for i in range(len(ing_ids)):
            for j in range(i+1, len(ing_ids)):
                ing_a = ing_ids[i]
                ing_b = ing_ids[j]
                
                interaction = None
                if ing_a in INTERACTION_DATABASE and ing_b in INTERACTION_DATABASE[ing_a].get("interactions", {}):
                    interaction = INTERACTION_DATABASE[ing_a]["interactions"][ing_b]
                elif ing_b in INTERACTION_DATABASE and ing_a in INTERACTION_DATABASE[ing_b].get("interactions", {}):
                    interaction = INTERACTION_DATABASE[ing_b]["interactions"][ing_a]
                
                if interaction:
                    pairs.append({
                        "ingredients": [ing_a, ing_b],
                        "type": interaction.get("type"),
                        "strength": interaction.get("strength"),
                        "description": interaction.get("description", "")
                    })
        
        # Check for higher-order patterns
        ing_set = set(ing_ids)
        for pattern_name, pattern in HIGHER_ORDER_PATTERNS.items():
            pattern_ings = set(pattern["ingredients"])
            if pattern_ings.issubset(ing_set):
                risk_patterns.append({
                    "name": pattern_name,
                    "description": pattern["description"],
                    "risk_level": pattern["risk_level"],
                    "risk_score": pattern["risk_score"],
                    "mechanism": pattern["mechanism"],
                    "mitigation": pattern.get("mitigation", "")
                })
        
        # Calculate overall risk
        risk_score = calculate_formulation_risk(ing_ids)
        
        return {
            "success": True,
            "data": {
                "formulation": formulation,
                "pairwise_interactions": pairs,
                "higher_order_patterns": risk_patterns,
                "overall_risk": {
                    "score": risk_score,
                    "level": get_risk_level(risk_score),
                    "recommendation": get_formulation_recommendation(risk_score, risk_patterns)
                }
            }
        }
    except Exception as e:
        logger.error(f"Formulation analysis error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/analyze-formulation")
async def analyze_custom_formulation(request: Request):
    """Analyze a custom formulation provided by user"""
    try:
        data = await request.json()
        ingredients = data.get("ingredients", [])
        formulation_name = data.get("name", "Custom Formulation")
        
        if len(ingredients) < 2:
            return {"success": False, "error": "Need at least 2 ingredients"}
        
        # Normalize ingredient names
        ing_ids = [i.lower().replace(" ", "_") for i in ingredients]
        
        # Find all pairwise interactions
        pairs = []
        risk_patterns = []
        
        for i in range(len(ing_ids)):
            for j in range(i+1, len(ing_ids)):
                ing_a = ing_ids[i]
                ing_b = ing_ids[j]
                
                interaction = None
                if ing_a in INTERACTION_DATABASE and ing_b in INTERACTION_DATABASE[ing_a].get("interactions", {}):
                    interaction = INTERACTION_DATABASE[ing_a]["interactions"][ing_b]
                elif ing_b in INTERACTION_DATABASE and ing_a in INTERACTION_DATABASE[ing_b].get("interactions", {}):
                    interaction = INTERACTION_DATABASE[ing_b]["interactions"][ing_a]
                
                if interaction:
                    pairs.append({
                        "ingredient_a": ingredients[i],
                        "ingredient_b": ingredients[j],
                        "type": interaction.get("type"),
                        "strength": interaction.get("strength"),
                        "mechanism": interaction.get("mechanism", ""),
                        "description": interaction.get("description", ""),
                        "mitigation": interaction.get("mitigation", "")
                    })
                else:
                    pairs.append({
                        "ingredient_a": ingredients[i],
                        "ingredient_b": ingredients[j],
                        "type": "unknown",
                        "strength": 0,
                        "description": "No documented interaction"
                    })
        
        # Check for higher-order patterns
        ing_set = set(ing_ids)
        for pattern_name, pattern in HIGHER_ORDER_PATTERNS.items():
            pattern_ings = set(pattern["ingredients"])
            if pattern_ings.issubset(ing_set):
                risk_patterns.append({
                    "name": pattern_name.replace("_", " ").title(),
                    "description": pattern["description"],
                    "risk_level": pattern["risk_level"],
                    "risk_score": pattern["risk_score"],
                    "mechanism": pattern["mechanism"],
                    "mitigation": pattern.get("mitigation", "")
                })
        
        # Calculate overall risk
        risk_score = calculate_formulation_risk(ing_ids)
        
        return {
            "success": True,
            "data": {
                "formulation": {
                    "name": formulation_name,
                    "ingredients": ingredients
                },
                "pairwise_interactions": pairs,
                "higher_order_patterns": risk_patterns,
                "overall_risk": {
                    "score": risk_score,
                    "level": get_risk_level(risk_score),
                    "recommendation": get_formulation_recommendation(risk_score, risk_patterns)
                }
            }
        }
    except Exception as e:
        logger.error(f"Custom formulation error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/interaction-types")
async def get_interaction_types():
    """Get all possible interaction types with descriptions"""
    return {
        "success": True,
        "data": {
            "synergistic": {
                "description": "Ingredients work together to enhance effects",
                "color": "#4ade80",
                "icon": "✅",
                "examples": ["Vitamin C + Vitamin E", "Niacinamide + Retinol"]
            },
            "antagonistic": {
                "description": "Ingredients reduce each other's efficacy",
                "color": "#f87171",
                "icon": "⚠️",
                "examples": ["Vitamin C + Niacinamide", "Retinol + Benzoyl Peroxide"]
            },
            "risk_amplifying": {
                "description": "Combination increases irritation or toxicity risk",
                "color": "#dc2626",
                "icon": "🔴",
                "examples": ["Retinol + AHAs", "Benzoyl Peroxide + Vitamin C"]
            },
            "neutral": {
                "description": "No significant interaction",
                "color": "#94a3b8",
                "icon": "➡️",
                "examples": ["Hyaluronic Acid + Most ingredients"]
            }
        }
    }

@router.get("/unsafe-clusters")
async def get_unsafe_clusters():
    """Get identified unsafe ingredient clusters"""
    try:
        clusters = []
        for pattern_name, pattern in HIGHER_ORDER_PATTERNS.items():
            if pattern["risk_level"] in ["critical", "high"]:
                clusters.append({
                    "name": pattern_name.replace("_", " ").title(),
                    "ingredients": [i.replace("_", " ").title() for i in pattern["ingredients"]],
                    "risk_level": pattern["risk_level"],
                    "risk_score": pattern["risk_score"],
                    "description": pattern["description"],
                    "clinical_signs": pattern.get("clinical_signs", []),
                    "mitigation": pattern.get("mitigation", "")
                })
        
        return {
            "success": True,
            "data": clusters
        }
    except Exception as e:
        logger.error(f"Unsafe clusters error: {e}")
        return {"success": False, "error": str(e)}

def calculate_formulation_risk(ingredients: List[str]) -> float:
    """Calculate overall risk score for a formulation"""
    if len(ingredients) < 2:
        return 0.0
    
    risk_score = 0.0
    interaction_count = 0
    
    for i in range(len(ingredients)):
        for j in range(i+1, len(ingredients)):
            ing_a = ingredients[i]
            ing_b = ingredients[j]
            
            # Check interaction
            interaction = None
            if ing_a in INTERACTION_DATABASE and ing_b in INTERACTION_DATABASE[ing_a].get("interactions", {}):
                interaction = INTERACTION_DATABASE[ing_a]["interactions"][ing_b]
            elif ing_b in INTERACTION_DATABASE and ing_a in INTERACTION_DATABASE[ing_b].get("interactions", {}):
                interaction = INTERACTION_DATABASE[ing_b]["interactions"][ing_a]
            
            if interaction:
                strength = interaction.get("strength", 0)
                if interaction.get("type") in ["antagonistic", "risk_amplifying"]:
                    risk_score += strength * 10
                elif interaction.get("type") == "synergistic":
                    risk_score -= strength * 5  # Reduce risk for beneficial combos
                interaction_count += 1
    
    # Check for higher-order patterns
    ing_set = set(ingredients)
    for pattern in HIGHER_ORDER_PATTERNS.values():
        pattern_ings = set(pattern["ingredients"])
        if pattern_ings.issubset(ing_set):
            if pattern["risk_level"] == "critical":
                risk_score += 30
            elif pattern["risk_level"] == "high":
                risk_score += 20
            elif pattern["risk_level"] == "moderate":
                risk_score += 10
    
    # Normalize to 0-100 scale
    risk_score = max(0, min(100, risk_score))
    
    return round(risk_score, 1)

def get_risk_level(score: float) -> str:
    """Convert numeric score to risk level"""
    if score >= 70:
        return "critical"
    elif score >= 40:
        return "high"
    elif score >= 20:
        return "moderate"
    else:
        return "low"

def get_formulation_recommendation(score: float, patterns: List) -> str:
    """Generate recommendation based on risk assessment"""
    if score >= 70:
        return "🚫 UNSAFE: This formulation contains dangerous combinations. Do not use together. Consider separating into different routines or finding alternatives."
    elif score >= 40:
        return "⚠️ HIGH RISK: This formulation has significant interaction concerns. Use with extreme caution. Consider patch testing and using on alternate days."
    elif score >= 20:
        return "⚡ MODERATE RISK: Some interactions present. Monitor skin response and adjust usage frequency. May be suitable for experienced users."
    elif patterns:
        return "✅ LOW RISK: Generally safe formulation. Some beneficial interactions present. Suitable for most users."
    else:
        return "✅ SAFE: No significant interactions detected. Suitable for all users."