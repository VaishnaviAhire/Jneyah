from fastapi import APIRouter, Request, Query
from typing import Optional, List, Dict
import logging
import numpy as np
import random
from datetime import datetime
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/expert/sandbox", tags=["expert_sandbox"])

# Comprehensive ingredient database with properties
INGREDIENT_PROPERTIES = {
    "retinol": {
        "name": "Retinol",
        "category": "Vitamin",
        "risk_score": 7.5,
        "irritation_potential": 0.8,
        "efficacy_score": 0.9,
        "cost_per_unit": 45.0,
        "stability": 0.6,
        "solubility": "lipid",
        "ph_range": [5.0, 6.5],
        "synergistic_with": ["niacinamide", "hyaluronic_acid", "ceramides"],
        "antagonistic_with": ["vitamin_c", "aha_bha", "benzoyl_peroxide"],
        "typical_concentration": [0.1, 1.0]
    },
    "niacinamide": {
        "name": "Niacinamide",
        "category": "Vitamin",
        "risk_score": 2.5,
        "irritation_potential": 0.1,
        "efficacy_score": 0.8,
        "cost_per_unit": 12.0,
        "stability": 0.9,
        "solubility": "water",
        "ph_range": [5.0, 7.0],
        "synergistic_with": ["retinol", "hyaluronic_acid", "zinc"],
        "antagonistic_with": ["vitamin_c", "aha_bha"],
        "typical_concentration": [2.0, 10.0]
    },
    "hyaluronic_acid": {
        "name": "Hyaluronic Acid",
        "category": "Humectant",
        "risk_score": 1.5,
        "irritation_potential": 0.05,
        "efficacy_score": 0.7,
        "cost_per_unit": 8.0,
        "stability": 0.8,
        "solubility": "water",
        "ph_range": [5.0, 8.0],
        "synergistic_with": ["retinol", "niacinamide", "vitamin_c"],
        "antagonistic_with": [],
        "typical_concentration": [0.1, 2.0]
    },
    "vitamin_c": {
        "name": "Vitamin C (L-Ascorbic Acid)",
        "category": "Vitamin",
        "risk_score": 3.0,
        "irritation_potential": 0.6,
        "efficacy_score": 0.85,
        "cost_per_unit": 25.0,
        "stability": 0.3,
        "solubility": "water",
        "ph_range": [3.0, 3.5],
        "synergistic_with": ["vitamin_e", "ferulic_acid", "hyaluronic_acid"],
        "antagonistic_with": ["niacinamide", "retinol", "benzoyl_peroxide"],
        "typical_concentration": [5.0, 20.0]
    },
    "salicylic_acid": {
        "name": "Salicylic Acid",
        "category": "Active",
        "risk_score": 6.0,
        "irritation_potential": 0.7,
        "efficacy_score": 0.8,
        "cost_per_unit": 15.0,
        "stability": 0.7,
        "solubility": "lipid",
        "ph_range": [3.0, 4.0],
        "synergistic_with": ["niacinamide", "hyaluronic_acid"],
        "antagonistic_with": ["retinol", "benzoyl_peroxide"],
        "typical_concentration": [0.5, 2.0]
    },
    "benzoyl_peroxide": {
        "name": "Benzoyl Peroxide",
        "category": "Active",
        "risk_score": 8.0,
        "irritation_potential": 0.85,
        "efficacy_score": 0.9,
        "cost_per_unit": 10.0,
        "stability": 0.5,
        "solubility": "lipid",
        "ph_range": [5.0, 7.0],
        "synergistic_with": ["clindamycin"],
        "antagonistic_with": ["retinol", "vitamin_c", "niacinamide", "hydroquinone"],
        "typical_concentration": [2.5, 10.0]
    },
    "glycerin": {
        "name": "Glycerin",
        "category": "Humectant",
        "risk_score": 1.0,
        "irritation_potential": 0.01,
        "efficacy_score": 0.6,
        "cost_per_unit": 2.0,
        "stability": 1.0,
        "solubility": "water",
        "ph_range": [4.0, 9.0],
        "synergistic_with": ["all"],
        "antagonistic_with": [],
        "typical_concentration": [2.0, 20.0]
    },
    "dimethicone": {
        "name": "Dimethicone",
        "category": "Silicone",
        "risk_score": 2.0,
        "irritation_potential": 0.02,
        "efficacy_score": 0.5,
        "cost_per_unit": 5.0,
        "stability": 0.95,
        "solubility": "oil",
        "ph_range": [4.0, 8.0],
        "synergistic_with": ["most"],
        "antagonistic_with": [],
        "typical_concentration": [0.5, 5.0]
    },
    "ceramides": {
        "name": "Ceramides",
        "category": "Lipid",
        "risk_score": 1.0,
        "irritation_potential": 0.01,
        "efficacy_score": 0.7,
        "cost_per_unit": 30.0,
        "stability": 0.7,
        "solubility": "lipid",
        "ph_range": [4.5, 6.5],
        "synergistic_with": ["niacinamide", "retinol"],
        "antagonistic_with": [],
        "typical_concentration": [0.1, 1.0]
    },
    "aha_bha": {
        "name": "AHAs/BHAs",
        "category": "Active",
        "risk_score": 6.5,
        "irritation_potential": 0.75,
        "efficacy_score": 0.85,
        "cost_per_unit": 12.0,
        "stability": 0.6,
        "solubility": "water",
        "ph_range": [3.0, 4.0],
        "synergistic_with": ["hyaluronic_acid", "niacinamide"],
        "antagonistic_with": ["retinol", "benzoyl_peroxide"],
        "typical_concentration": [5.0, 10.0]
    }
}

@router.post("/what-if")
async def what_if_analysis(request: Request):
    """Perform what-if analysis on a formulation"""
    try:
        data = await request.json()
        formulation = data.get("formulation", [])
        changes = data.get("changes", [])
        
        if not formulation:
            return {"success": False, "error": "No formulation provided"}
        
        # Calculate baseline metrics
        baseline = calculate_formulation_metrics(formulation)
        
        # Apply changes and calculate new metrics
        scenarios = []
        
        for change in changes:
            modified_formulation = apply_change(formulation, change)
            if modified_formulation:
                new_metrics = calculate_formulation_metrics(modified_formulation)
                
                # Calculate deltas
                delta = {
                    "risk_score": new_metrics["overall_risk"] - baseline["overall_risk"],
                    "irritation_potential": new_metrics["irritation_potential"] - baseline["irritation_potential"],
                    "efficacy": new_metrics["efficacy"] - baseline["efficacy"],
                    "cost": new_metrics["cost"] - baseline["cost"],
                    "stability": new_metrics["stability"] - baseline["stability"]
                }
                
                scenarios.append({
                    "change": change,
                    "baseline": baseline,
                    "new_metrics": new_metrics,
                    "delta": delta,
                    "interpretation": generate_interpretation(change, delta)
                })
        
        return {
            "success": True,
            "data": {
                "baseline": baseline,
                "scenarios": scenarios
            }
        }
    except Exception as e:
        logger.error(f"What-if analysis error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/simulate-alternative")
async def simulate_alternative(request: Request):
    """Simulate safer alternatives for a formulation"""
    try:
        data = await request.json()
        formulation = data.get("formulation", [])
        target_ingredient = data.get("target_ingredient")
        max_risk_reduction = data.get("max_risk_reduction", 30)
        
        if not formulation or not target_ingredient:
            return {"success": False, "error": "Formulation and target ingredient required"}
        
        # Find the target ingredient in formulation
        target = None
        for ing in formulation:
            if ing["name"].lower() == target_ingredient.lower():
                target = ing
                break
        
        if not target:
            return {"success": False, "error": f"Ingredient {target_ingredient} not found in formulation"}
        
        # Find alternatives
        alternatives = find_safer_alternatives(target["name"])
        
        simulated_formulations = []
        
        for alt in alternatives[:5]:  # Top 5 alternatives
            # Create new formulation with alternative
            new_formulation = []
            for ing in formulation:
                if ing["name"].lower() == target["name"].lower():
                    # Replace with alternative
                    new_ing = {
                        "name": alt["name"],
                        "concentration": ing["concentration"]  # Use same concentration
                    }
                    new_formulation.append(new_ing)
                else:
                    new_formulation.append(ing)
            
            # Calculate metrics
            baseline_metrics = calculate_formulation_metrics(formulation)
            new_metrics = calculate_formulation_metrics(new_formulation)
            
            # Calculate risk reduction
            risk_reduction = ((baseline_metrics["overall_risk"] - new_metrics["overall_risk"]) / 
                            baseline_metrics["overall_risk"] * 100)
            
            if risk_reduction <= max_risk_reduction:
                simulated_formulations.append({
                    "alternative": alt,
                    "formulation": new_formulation,
                    "metrics": new_metrics,
                    "risk_reduction": round(risk_reduction, 1),
                    "delta": {
                        "risk_score": new_metrics["overall_risk"] - baseline_metrics["overall_risk"],
                        "irritation": new_metrics["irritation_potential"] - baseline_metrics["irritation_potential"],
                        "efficacy": new_metrics["efficacy"] - baseline_metrics["efficacy"],
                        "cost": new_metrics["cost"] - baseline_metrics["cost"]
                    }
                })
        
        # Sort by risk reduction (most reduction first)
        simulated_formulations.sort(key=lambda x: x["risk_reduction"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "original": {
                    "ingredient": target,
                    "metrics": baseline_metrics
                },
                "alternatives": simulated_formulations
            }
        }
    except Exception as e:
        logger.error(f"Alternative simulation error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/optimize")
async def optimize_formulation(request: Request):
    """Optimize formulation for multiple objectives"""
    try:
        data = await request.json()
        formulation = data.get("formulation", [])
        objectives = data.get("objectives", ["risk", "cost", "efficacy"])
        constraints = data.get("constraints", {})
        
        if not formulation:
            return {"success": False, "error": "No formulation provided"}
        
        # Generate optimization suggestions
        suggestions = []
        
        # Try different concentration adjustments
        for ing in formulation:
            ing_id = ing["name"].lower().replace(" ", "_")
            if ing_id in INGREDIENT_PROPERTIES:
                props = INGREDIENT_PROPERTIES[ing_id]
                
                # Try reducing concentration for high-risk ingredients
                if props["risk_score"] > 5:
                    new_conc = ing["concentration"] * 0.7
                    if new_conc >= props["typical_concentration"][0]:
                        suggestions.append({
                            "type": "reduce_concentration",
                            "ingredient": ing["name"],
                            "current": ing["concentration"],
                            "suggested": round(new_conc, 2),
                            "reason": f"High risk ingredient ({props['risk_score']}/10)",
                            "expected_impact": {
                                "risk_reduction": f"-{round(props['risk_score'] * 0.3, 1)}%",
                                "efficacy_impact": "minor reduction"
                            }
                        })
                
                # Try finding synergistic pairs
                if ing_id in props.get("synergistic_with", []):
                    suggestions.append({
                        "type": "add_synergistic",
                        "ingredient": ing["name"],
                        "suggested_pair": props["synergistic_with"][0],
                        "reason": "Synergistic combination available",
                        "expected_impact": {
                            "efficacy_boost": "+15-20%",
                            "risk_impact": "neutral"
                        }
                    })
        
        return {
            "success": True,
            "data": {
                "formulation": formulation,
                "optimization_suggestions": suggestions,
                "objectives": objectives,
                "constraints": constraints
            }
        }
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/concentration-optimization")
async def optimize_concentration(request: Request):
    """Optimize concentrations for a single ingredient"""
    try:
        data = await request.json()
        ingredient = data.get("ingredient")
        current_conc = data.get("current_concentration")
        target = data.get("target", "risk_efficacy_balance")
        
        if not ingredient or not current_conc:
            return {"success": False, "error": "Ingredient and concentration required"}
        
        ing_id = ingredient.lower().replace(" ", "_")
        if ing_id not in INGREDIENT_PROPERTIES:
            return {"success": False, "error": f"Ingredient {ingredient} not found"}
        
        props = INGREDIENT_PROPERTIES[ing_id]
        min_conc, max_conc = props["typical_concentration"]
        
        # Generate concentration curve
        concentrations = []
        risks = []
        efficacies = []
        costs = []
        
        steps = np.linspace(min_conc, max_conc, 10)
        for conc in steps:
            # Risk increases with concentration (non-linear)
            risk = props["risk_score"] * (conc / max_conc) ** 1.2
            # Efficacy increases but plateaus
            efficacy = props["efficacy_score"] * (1 - np.exp(-2 * conc / max_conc))
            # Cost linear
            cost = props["cost_per_unit"] * conc
            
            concentrations.append(round(conc, 2))
            risks.append(round(risk, 2))
            efficacies.append(round(efficacy, 2))
            costs.append(round(cost, 2))
        
        # Find optimal concentration based on target
        if target == "min_risk":
            optimal_idx = 0
        elif target == "max_efficacy":
            optimal_idx = len(concentrations) - 1
        else:
            # Balance risk and efficacy
            scores = [e - r/10 for e, r in zip(efficacies, risks)]
            optimal_idx = np.argmax(scores)
        
        return {
            "success": True,
            "data": {
                "ingredient": ingredient,
                "current_concentration": current_conc,
                "optimal_concentration": concentrations[optimal_idx],
                "concentration_range": [min_conc, max_conc],
                "curve": {
                    "concentrations": concentrations,
                    "risks": risks,
                    "efficacies": efficacies,
                    "costs": costs
                },
                "recommendation": get_concentration_recommendation(
                    current_conc, concentrations[optimal_idx], props
                )
            }
        }
    except Exception as e:
        logger.error(f"Concentration optimization error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/ingredient-properties/{ingredient_id}")
async def get_ingredient_properties(ingredient_id: str):
    """Get detailed properties for an ingredient"""
    try:
        ing_id = ingredient_id.lower().replace(" ", "_")
        
        if ing_id in INGREDIENT_PROPERTIES:
            return {
                "success": True,
                "data": INGREDIENT_PROPERTIES[ing_id]
            }
        
        return {"success": False, "error": "Ingredient not found"}
    except Exception as e:
        logger.error(f"Properties error: {e}")
        return {"success": False, "error": str(e)}

def calculate_formulation_metrics(formulation):
    """Calculate comprehensive metrics for a formulation"""
    total_risk = 0
    total_irritation = 0
    total_efficacy = 0
    total_cost = 0
    total_stability = 0
    interaction_count = 0
    interaction_penalty = 0
    
    ingredient_count = len(formulation)
    
    for ing in formulation:
        ing_id = ing["name"].lower().replace(" ", "_")
        conc = ing.get("concentration", 1.0)
        
        if ing_id in INGREDIENT_PROPERTIES:
            props = INGREDIENT_PROPERTIES[ing_id]
            
            # Scale by concentration (normalized)
            norm_conc = conc / props["typical_concentration"][1] if props["typical_concentration"][1] > 0 else 1
            
            total_risk += props["risk_score"] * norm_conc
            total_irritation += props["irritation_potential"] * norm_conc
            total_efficacy += props["efficacy_score"] * norm_conc
            total_cost += props["cost_per_unit"] * conc
            total_stability += props["stability"]
    
    # Calculate interactions between ingredients
    for i in range(len(formulation)):
        for j in range(i+1, len(formulation)):
            ing_a = formulation[i]["name"].lower().replace(" ", "_")
            ing_b = formulation[j]["name"].lower().replace(" ", "_")
            
            if ing_a in INGREDIENT_PROPERTIES and ing_b in INGREDIENT_PROPERTIES:
                props_a = INGREDIENT_PROPERTIES[ing_a]
                
                # Check antagonistic interactions
                if ing_b in props_a.get("antagonistic_with", []):
                    interaction_count += 1
                    interaction_penalty += 0.2 * props_a["risk_score"]
    
    # Normalize scores
    avg_risk = (total_risk / ingredient_count) if ingredient_count > 0 else 0
    avg_irritation = (total_irritation / ingredient_count) if ingredient_count > 0 else 0
    avg_efficacy = (total_efficacy / ingredient_count) if ingredient_count > 0 else 0
    avg_stability = (total_stability / ingredient_count) if ingredient_count > 0 else 0
    
    # Add interaction penalty to risk
    overall_risk = avg_risk + interaction_penalty
    
    # Determine risk level
    if overall_risk < 3:
        risk_level = "Low"
    elif overall_risk < 6:
        risk_level = "Medium"
    elif overall_risk < 8:
        risk_level = "High"
    else:
        risk_level = "Critical"
    
    return {
        "overall_risk": round(overall_risk, 2),
        "risk_level": risk_level,
        "irritation_potential": round(avg_irritation, 2),
        "efficacy": round(avg_efficacy, 2),
        "cost": round(total_cost, 2),
        "stability": round(avg_stability, 2),
        "interaction_count": interaction_count,
        "ingredient_count": ingredient_count
    }

def apply_change(formulation, change):
    """Apply a single change to a formulation"""
    change_type = change.get("type")
    ingredient = change.get("ingredient")
    value = change.get("value")
    
    new_formulation = [ing.copy() for ing in formulation]
    
    if change_type == "remove":
        # Remove ingredient
        new_formulation = [ing for ing in new_formulation 
                          if ing["name"].lower() != ingredient.lower()]
    
    elif change_type == "add":
        # Add new ingredient
        if not any(ing["name"].lower() == ingredient.lower() for ing in new_formulation):
            new_formulation.append({
                "name": ingredient,
                "concentration": value.get("concentration", 1.0)
            })
    
    elif change_type == "modify_concentration":
        # Modify concentration
        for ing in new_formulation:
            if ing["name"].lower() == ingredient.lower():
                ing["concentration"] = value
    
    elif change_type == "replace":
        # Replace with another ingredient
        new_formulation = [ing for ing in new_formulation 
                          if ing["name"].lower() != ingredient.lower()]
        new_formulation.append({
            "name": value.get("new_ingredient"),
            "concentration": value.get("concentration", 1.0)
        })
    
    return new_formulation if new_formulation else None

def find_safer_alternatives(ingredient_name):
    """Find safer alternatives for an ingredient"""
    ing_id = ingredient_name.lower().replace(" ", "_")
    
    if ing_id not in INGREDIENT_PROPERTIES:
        return []
    
    props = INGREDIENT_PROPERTIES[ing_id]
    alternatives = []
    
    # Find ingredients in same category with lower risk
    for alt_id, alt_props in INGREDIENT_PROPERTIES.items():
        if alt_id != ing_id and alt_props["category"] == props["category"]:
            if alt_props["risk_score"] < props["risk_score"]:
                alternatives.append({
                    "name": alt_props["name"],
                    "risk_score": alt_props["risk_score"],
                    "risk_reduction": props["risk_score"] - alt_props["risk_score"],
                    "efficacy_delta": alt_props["efficacy_score"] - props["efficacy_score"],
                    "cost_delta": alt_props["cost_per_unit"] - props["cost_per_unit"],
                    "stability": alt_props["stability"],
                    "synergy_profile": alt_props.get("synergistic_with", [])
                })
    
    # Sort by risk reduction (most reduction first)
    alternatives.sort(key=lambda x: x["risk_reduction"], reverse=True)
    
    return alternatives

def generate_interpretation(change, delta):
    """Generate human-readable interpretation of changes"""
    risk_change = delta["risk_score"]
    efficacy_change = delta["efficacy"]
    
    if risk_change < 0:
        risk_text = f"reduced by {abs(risk_change):.1f} points"
    elif risk_change > 0:
        risk_text = f"increased by {risk_change:.1f} points"
    else:
        risk_text = "unchanged"
    
    if efficacy_change > 0:
        efficacy_text = f"improved by {efficacy_change:.1f} points"
    elif efficacy_change < 0:
        efficacy_text = f"decreased by {abs(efficacy_change):.1f} points"
    else:
        efficacy_text = "unchanged"
    
    if change["type"] == "remove":
        return f"Removing {change['ingredient']}: Risk {risk_text}, efficacy {efficacy_text}"
    elif change["type"] == "add":
        return f"Adding {change['ingredient']}: Risk {risk_text}, efficacy {efficacy_text}"
    elif change["type"] == "modify_concentration":
        return f"Changing {change['ingredient']} concentration to {change['value']}%: Risk {risk_text}, efficacy {efficacy_text}"
    elif change["type"] == "replace":
        return f"Replacing {change['ingredient']} with {change['value']['new_ingredient']}: Risk {risk_text}, efficacy {efficacy_text}"
    
    return "Change applied"

def get_concentration_recommendation(current, optimal, props):
    """Generate recommendation for concentration adjustment"""
    if abs(current - optimal) < 0.1 * optimal:
        return "Current concentration is optimal"
    elif current < optimal:
        return f"Increase concentration to {optimal}% for better efficacy (risk will increase by ~{round(props['risk_score'] * 0.1, 1)} points)"
    else:
        return f"Decrease concentration to {optimal}% to reduce risk (efficacy will decrease by ~{round(props['efficacy_score'] * 0.1, 1)} points)"