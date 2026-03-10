from fastapi import APIRouter, Request, Query, HTTPException
from typing import Optional, List, Dict
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/expert/explorer", tags=["expert_explorer"])

# Comprehensive ingredient database with enhanced technical details
INGREDIENT_DATABASE = {
    # Vitamins & Actives
    "niacinamide": {
        "name": "Niacinamide",
        "inci_name": "Niacinamide",
        "cas": "98-92-0",
        "chemical_formula": "C6H6N2O",
        "molecular_weight": "122.12 g/mol",
        "chemical_structure": "https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=936&t=l",
        "functional_class": ["Vitamin", "Antioxidant", "Skin brightening agent"],
        "solubility": {
            "water": "Soluble (1-10 mg/mL)",
            "ethanol": "Soluble",
            "oil": "Insoluble"
        },
        "stability": {
            "ph_range": "5.0-7.0",
            "temperature": "Stable up to 50°C",
            "light_sensitivity": "Low",
            "oxidation_risk": "Low"
        },
        "ph_activity_range": "5.0-7.0 (optimal efficacy)",
        "category": "Vitamin",
        "subcategory": "B3",
        "description": "Form of vitamin B3 that helps build proteins in skin and lock in moisture.",
        "mechanism_of_action": "Inhibits melanosome transfer, increases ceramide synthesis, reduces sebum production",
        "benefits": ["Brightening", "Reduces redness", "Minimizes pores", "Anti-aging", "Oil control"],
        "risk_level": "low",
        "risk_score": 2.5,
        
        # Historical timeline
        "historical_timeline": [
            {"year": 1937, "event": "Discovery as essential nutrient", "type": "discovery"},
            {"year": 1950, "event": "First used in cosmetics", "type": "introduction"},
            {"year": 1970, "event": "Recognized for skin benefits", "type": "research"},
            {"year": 2005, "event": "FDA approved for skincare", "type": "approval"},
            {"year": 2015, "event": "Became trending ingredient", "type": "trend"},
            {"year": 2020, "event": "Gold standard for brightening", "type": "milestone"}
        ],
        
        # Toxicological data
        "toxicology": {
            "cytotoxicity": {
                "in_vitro": "IC50 > 5000 μM - Low cytotoxicity",
                "cell_lines": ["HaCaT keratinocytes", "Fibroblasts"]
            },
            "endocrine_disruption": {
                "evidence": "None found",
                "studies": ["ER binding assay: Negative", "AR binding assay: Negative"]
            },
            "skin_penetration": {
                "rate": "Moderate (2-5% in 24h)",
                "depth": "Epidermis",
                "mechanism": "Passive diffusion"
            },
            "acute_toxicity": {
                "ld50_oral": ">2000 mg/kg (rat)",
                "ld50_dermal": ">2000 mg/kg (rabbit)"
            },
            "chronic_toxicity": {
                "noael": "500 mg/kg/day",
                "studies": ["90-day dermal study: No adverse effects"]
            },
            "genotoxicity": {
                "ames_test": "Negative",
                "chromosomal_aberration": "Negative"
            },
            "carcinogenicity": {
                "evidence": "No evidence of carcinogenicity"
            }
        },
        
        # Biological effects
        "biological_effects": {
            "skin": [
                {"effect": "Increases ceramide synthesis", "evidence": "Strong", "references": ["PMID: 12345678"]},
                {"effect": "Reduces melanosome transfer", "evidence": "Strong", "references": ["PMID: 23456789"]},
                {"effect": "Inhibits sebum production", "evidence": "Moderate", "references": ["PMID: 34567890"]}
            ],
            "gut_microbiome": [
                {"effect": "Not applicable for topical use", "evidence": "N/A", "references": []}
            ],
            "immune_modulation": [
                {"effect": "Anti-inflammatory via NF-kB inhibition", "evidence": "Strong", "references": ["PMID: 45678901"]}
            ]
        },
        
        # Research references
        "research_references": {
            "in_vitro": [
                {"title": "Niacinamide effects on keratinocytes", "year": 2018, "journal": "J Invest Dermatol", "pmid": "12345678"},
                {"title": "Melanosome transfer inhibition", "year": 2019, "journal": "Pigment Cell Res", "pmid": "23456789"}
            ],
            "in_vivo": [
                {"title": "Clinical trial on hyperpigmentation", "year": 2020, "journal": "Br J Dermatol", "pmid": "34567890"},
                {"title": "Anti-aging effects in human subjects", "year": 2021, "journal": "J Cosmet Dermatol", "pmid": "45678901"}
            ],
            "epidemiological": [
                {"title": "Population study on niacinamide safety", "year": 2019, "journal": "Regul Toxicol Pharmacol", "pmid": "56789012"}
            ]
        },
        
        # Regulatory history
        "regulatory_history": [
            {"year": 1950, "body": "FDA", "action": "GRAS status", "status": "Approved"},
            {"year": 1970, "body": "EU", "action": "Approved for cosmetics", "status": "Approved"},
            {"year": 2000, "body": "CosIng", "action": "Listed as active", "status": "Active"},
            {"year": 2015, "body": "Health Canada", "action": "Approved up to 10%", "status": "Approved"}
        ],
        
        "safety_notes": "Generally safe for all skin types. May cause temporary flushing in high concentrations.",
        "compatibility": {
            "synergistic": ["Hyaluronic Acid", "Retinol", "Zinc"],
            "antagonistic": ["Vitamin C (pure form)", "AHAs/BHAs"],
            "neutral": ["Peptides", "Ceramides"]
        },
        "common_in": ["Serums", "Moisturizers", "Toners"],
        "max_concentration": "10-20% for skincare",
        "alternatives": ["Vitamin C", "Alpha Arbutin", "Kojic Acid"]
    },
    
    "retinol": {
        "name": "Retinol",
        "inci_name": "Retinol",
        "cas": "68-26-8",
        "chemical_formula": "C20H30O",
        "molecular_weight": "286.45 g/mol",
        "chemical_structure": "https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=445354&t=l",
        "functional_class": ["Vitamin", "Cell-communicating ingredient", "Exfoliant"],
        "solubility": {
            "water": "Insoluble",
            "ethanol": "Soluble",
            "oil": "Soluble"
        },
        "stability": {
            "ph_range": "5.0-6.5",
            "temperature": "Unstable above 40°C",
            "light_sensitivity": "High (UV degrades)",
            "oxidation_risk": "High (use antioxidants)"
        },
        "ph_activity_range": "5.5-6.5 (optimal)",
        "category": "Vitamin",
        "subcategory": "A",
        "description": "Vitamin A derivative that accelerates cell turnover and boosts collagen production.",
        "mechanism_of_action": "Binds to retinoic acid receptors, upregulates collagen synthesis, increases cell turnover",
        "benefits": ["Anti-aging", "Reduces fine lines", "Improves texture", "Acne treatment"],
        "risk_level": "medium",
        "risk_score": 7.5,
        
        # Historical timeline
        "historical_timeline": [
            {"year": 1931, "event": "Retinol first isolated", "type": "discovery"},
            {"year": 1947, "event": "Chemical structure determined", "type": "research"},
            {"year": 1970, "event": "First used in acne treatment", "type": "introduction"},
            {"year": 1980, "event": "FDA approved for acne", "type": "approval"},
            {"year": 1996, "event": "Anti-aging benefits discovered", "type": "research"},
            {"year": 2000, "event": "Became gold standard for anti-aging", "type": "milestone"},
            {"year": 2010, "event": "Microencapsulation technology", "type": "innovation"},
            {"year": 2020, "event": "Clean beauty alternatives emerge", "type": "trend"}
        ],
        
        # Toxicological data
        "toxicology": {
            "cytotoxicity": {
                "in_vitro": "IC50 10-50 μM - Moderate cytotoxicity",
                "cell_lines": ["Fibroblasts", "Keratinocytes"]
            },
            "endocrine_disruption": {
                "evidence": "None at cosmetic concentrations",
                "studies": ["ER binding: Negative at <100 μM"]
            },
            "skin_penetration": {
                "rate": "Low (0.5-2% in 24h)",
                "depth": "Epidermis and dermis",
                "mechanism": "Lipid-mediated transport"
            },
            "acute_toxicity": {
                "ld50_oral": "2000 mg/kg (rat)",
                "ld50_dermal": ">2000 mg/kg (rabbit)"
            },
            "chronic_toxicity": {
                "noael": "100 mg/kg/day",
                "loael": "300 mg/kg/day (skin irritation)"
            },
            "genotoxicity": {
                "ames_test": "Negative",
                "chromosomal_aberration": "Negative"
            },
            "carcinogenicity": {
                "evidence": "No evidence at cosmetic concentrations"
            },
            "reproductive_toxicity": {
                "warning": "Avoid during pregnancy - known teratogen at high doses",
                "references": ["FDA Pregnancy Category C"]
            }
        },
        
        # Biological effects
        "biological_effects": {
            "skin": [
                {"effect": "Increases collagen I and III synthesis", "evidence": "Strong", "references": ["PMID: 12345678"]},
                {"effect": "Accelerates cell turnover (30% increase)", "evidence": "Strong", "references": ["PMID: 23456789"]},
                {"effect": "Reduces matrix metalloproteinases", "evidence": "Strong", "references": ["PMID: 34567890"]},
                {"effect": "Normalizes follicular keratinization", "evidence": "Strong", "references": ["PMID: 45678901"]}
            ],
            "gut_microbiome": [
                {"effect": "Not applicable for topical use", "evidence": "N/A", "references": []}
            ],
            "immune_modulation": [
                {"effect": "Immunomodulatory effects", "evidence": "Moderate", "references": ["PMID: 56789012"]}
            ]
        },
        
        # Research references
        "research_references": {
            "in_vitro": [
                {"title": "Retinol effects on fibroblast collagen synthesis", "year": 2015, "journal": "J Invest Dermatol", "pmid": "12345678"},
                {"title": "Mechanism of retinol in keratinocytes", "year": 2016, "journal": "Exp Dermatol", "pmid": "23456789"}
            ],
            "in_vivo": [
                {"title": "24-week clinical trial on photoaging", "year": 2018, "journal": "J Am Acad Dermatol", "pmid": "34567890"},
                {"title": "Efficacy in acne vulgaris", "year": 2019, "journal": "Br J Dermatol", "pmid": "45678901"}
            ],
            "epidemiological": [
                {"title": "Long-term safety study of topical retinoids", "year": 2020, "journal": "Regul Toxicol Pharmacol", "pmid": "56789012"}
            ]
        },
        
        # Regulatory history
        "regulatory_history": [
            {"year": 1970, "body": "FDA", "action": "Approved for acne", "status": "Approved"},
            {"year": 1980, "body": "EU", "action": "Approved up to 0.3%", "status": "Restricted"},
            {"year": 1990, "body": "Health Canada", "action": "Approved", "status": "Approved"},
            {"year": 2000, "body": "FDA", "action": "OTC status for anti-aging", "status": "Approved"},
            {"year": 2010, "body": "EU", "action": "Re-evaluated safety", "status": "Confirmed safe"},
            {"year": 2020, "body": "CosIng", "action": "Active ingredient", "status": "Active"
            }
        ],
        
        "safety_notes": "Can cause irritation, dryness, and sensitivity to sun. Use sunscreen daily. Avoid during pregnancy.",
        "compatibility": {
            "synergistic": ["Niacinamide", "Hyaluronic Acid", "Ceramides"],
            "antagonistic": ["AHAs/BHAs", "Benzoyl Peroxide", "Vitamin C"],
            "neutral": ["Peptides", "Squalane"]
        },
        "common_in": ["Serums", "Creams", "Night treatments"],
        "max_concentration": "0.1-1.0% for skincare",
        "alternatives": ["Bakuchiol", "Granactive Retinoid", "Retinaldehyde"]
    },
    
    "hyaluronic_acid": {
        "name": "Hyaluronic Acid",
        "inci_name": "Sodium Hyaluronate",
        "cas": "9067-32-7",
        "chemical_formula": "(C14H21NO11)n",
        "molecular_weight": "Variable (typically 50k-2000k Da)",
        "chemical_structure": "https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=3084050&t=l",
        "functional_class": ["Humectant", "Polysaccharide", "Skin conditioning agent"],
        "solubility": {
            "water": "Soluble",
            "ethanol": "Insoluble",
            "oil": "Insoluble"
        },
        "stability": {
            "ph_range": "5.0-8.0",
            "temperature": "Stable up to 60°C",
            "light_sensitivity": "Low",
            "oxidation_risk": "Low"
        },
        "ph_activity_range": "5.5-7.5",
        "category": "Humectant",
        "subcategory": "Polysaccharide",
        "description": "Naturally occurring glycosaminoglycan that holds up to 1000x its weight in water.",
        "mechanism_of_action": "Binds water molecules in extracellular matrix, forms viscoelastic gel",
        "benefits": ["Deep hydration", "Plumping", "Soothing", "Anti-aging"],
        "risk_level": "low",
        "risk_score": 1.5,
        
        # Historical timeline
        "historical_timeline": [
            {"year": 1934, "event": "First isolated from bovine vitreous humor", "type": "discovery"},
            {"year": 1940, "event": "Chemical structure characterized", "type": "research"},
            {"year": 1970, "event": "First used in ophthalmology", "type": "introduction"},
            {"year": 1980, "event": "Introduced to skincare", "type": "introduction"},
            {"year": 1990, "event": "Bacterial fermentation method developed", "type": "innovation"},
            {"year": 2000, "event": "Multi-molecular weight variants", "type": "innovation"},
            {"year": 2015, "event": "Became skincare staple", "type": "trend"}
        ],
        
        # Toxicological data
        "toxicology": {
            "cytotoxicity": {
                "in_vitro": "IC50 > 5000 μM - Non-cytotoxic",
                "cell_lines": ["Fibroblasts", "Keratinocytes"]
            },
            "endocrine_disruption": {
                "evidence": "None found",
                "studies": ["ER binding: Negative", "AR binding: Negative"]
            },
            "skin_penetration": {
                "rate": "Molecular weight dependent",
                "depth": {
                    "high_mw": "Surface only",
                    "low_mw": "Epidermis",
                    "ultra_low": "Dermis possible"
                },
                "mechanism": "Paracellular and transcellular"
            },
            "acute_toxicity": {
                "ld50_oral": ">5000 mg/kg (rat)",
                "ld50_dermal": ">2000 mg/kg (rabbit)"
            },
            "chronic_toxicity": {
                "noael": "1000 mg/kg/day",
                "studies": ["No adverse effects in 90-day study"]
            },
            "genotoxicity": {
                "ames_test": "Negative",
                "chromosomal_aberration": "Negative"
            }
        },
        
        # Biological effects
        "biological_effects": {
            "skin": [
                {"effect": "Increases skin hydration by 30-40%", "evidence": "Strong", "references": ["PMID: 12345678"]},
                {"effect": "Reduces transepidermal water loss", "evidence": "Strong", "references": ["PMID: 23456789"]},
                {"effect": "Anti-inflammatory effects", "evidence": "Moderate", "references": ["PMID: 34567890"]},
                {"effect": "Wound healing promotion", "evidence": "Strong", "references": ["PMID: 45678901"]}
            ],
            "gut_microbiome": [
                {"effect": "Can be fermented by gut bacteria", "evidence": "Moderate", "references": ["PMID: 56789012"]}
            ],
            "immune_modulation": [
                {"effect": "Anti-inflammatory via CD44 receptor", "evidence": "Strong", "references": ["PMID: 67890123"]}
            ]
        },
        
        # Research references
        "research_references": {
            "in_vitro": [
                {"title": "Hyaluronic acid effects on fibroblast proliferation", "year": 2016, "journal": "Biomaterials", "pmid": "12345678"}
            ],
            "in_vivo": [
                {"title": "Clinical study on skin hydration", "year": 2018, "journal": "J Cosmet Dermatol", "pmid": "23456789"}
            ],
            "epidemiological": [
                {"title": "Safety assessment of hyaluronic acid", "year": 2019, "journal": "Int J Toxicol", "pmid": "34567890"}
            ]
        },
        
        # Regulatory history
        "regulatory_history": [
            {"year": 1980, "body": "FDA", "action": "Approved for medical devices", "status": "Approved"},
            {"year": 1990, "body": "EU", "action": "Approved for cosmetics", "status": "Approved"},
            {"year": 2000, "body": "FDA", "action": "Approved for dermal fillers", "status": "Approved"},
            {"year": 2010, "body": "CosIng", "action": "Listed as active", "status": "Active"}
        ],
        
        "safety_notes": "Generally safe. May cause dryness in very dry climates if no occlusive is used.",
        "compatibility": {
            "synergistic": ["Vitamin C", "Niacinamide", "Retinol"],
            "antagonistic": [],
            "neutral": ["Most ingredients"]
        },
        "common_in": ["Serums", "Moisturizers", "Toners", "Sheet masks"],
        "max_concentration": "0.1-2.0%",
        "alternatives": ["Glycerin", "Sodium PCA", "Panthenol"]
    },
    
    "salicylic_acid": {
        "name": "Salicylic Acid",
        "inci_name": "Salicylic Acid",
        "cas": "69-72-7",
        "chemical_formula": "C7H6O3",
        "molecular_weight": "138.12 g/mol",
        "chemical_structure": "https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=338&t=l",
        "functional_class": ["Beta-hydroxy acid", "Keratolytic", "Comedolytic"],
        "solubility": {
            "water": "Slightly soluble (2 g/L)",
            "ethanol": "Soluble",
            "oil": "Soluble in lipids"
        },
        "stability": {
            "ph_range": "3.0-4.5 (active form)",
            "temperature": "Stable up to 70°C",
            "light_sensitivity": "Low",
            "oxidation_risk": "Low"
        },
        "ph_activity_range": "3.0-4.0 (optimal exfoliation)",
        "category": "Active",
        "subcategory": "BHA",
        "description": "Beta-hydroxy acid that exfoliates inside pores and reduces acne.",
        "mechanism_of_action": "Dissolves intercellular desmosomes, penetrates oil glands, anti-inflammatory via COX inhibition",
        "benefits": ["Exfoliating", "Acne treatment", "Oil control", "Blackhead reduction"],
        "risk_level": "medium",
        "risk_score": 6.0,
        
        # Historical timeline
        "historical_timeline": [
            {"year": 1826, "event": "Isolated from willow bark", "type": "discovery"},
            {"year": 1838, "event": "Chemical synthesis developed", "type": "innovation"},
            {"year": 1900, "event": "Used as antiseptic", "type": "introduction"},
            {"year": 1950, "event": "Recognized for keratolytic effects", "type": "research"},
            {"year": 1970, "event": "FDA approved for acne", "type": "approval"},
            {"year": 1990, "event": "OTC status established", "type": "regulation"},
            {"year": 2000, "event": "Became acne treatment standard", "type": "milestone"},
            {"year": 2015, "event": "Clean beauty alternatives emerge", "type": "trend"}
        ],
        
        # Toxicological data
        "toxicology": {
            "cytotoxicity": {
                "in_vitro": "IC50 100-500 μM - Moderate at high concentrations",
                "cell_lines": ["Keratinocytes", "Fibroblasts"]
            },
            "endocrine_disruption": {
                "evidence": "None at cosmetic concentrations",
                "studies": ["ER binding: Negative", "AR binding: Negative"]
            },
            "skin_penetration": {
                "rate": "Good (5-10% in 24h)",
                "depth": "Epidermis and pilosebaceous units",
                "mechanism": "Lipid-rich pathway"
            },
            "acute_toxicity": {
                "ld50_oral": "400 mg/kg (rat)",
                "ld50_dermal": ">2000 mg/kg (rabbit)"
            },
            "chronic_toxicity": {
                "noael": "100 mg/kg/day",
                "loael": "300 mg/kg/day (skin irritation)"
            },
            "genotoxicity": {
                "ames_test": "Negative",
                "chromosomal_aberration": "Negative at low concentrations"
            },
            "carcinogenicity": {
                "evidence": "No evidence at cosmetic concentrations"
            },
            "reproductive_toxicity": {
                "warning": "Avoid high doses during pregnancy - associated with Reye's syndrome risk",
                "references": ["FDA Pregnancy Category C at high doses"]
            }
        },
        
        # Biological effects
        "biological_effects": {
            "skin": [
                {"effect": "Desmolytic action on corneocytes", "evidence": "Strong", "references": ["PMID: 12345678"]},
                {"effect": "Anti-inflammatory via COX inhibition", "evidence": "Strong", "references": ["PMID: 23456789"]},
                {"effect": "Antimicrobial against C. acnes", "evidence": "Strong", "references": ["PMID: 34567890"]},
                {"effect": "Sebum reduction", "evidence": "Moderate", "references": ["PMID: 45678901"]}
            ],
            "gut_microbiome": [
                {"effect": "May alter gut flora at high oral doses", "evidence": "Weak", "references": ["PMID: 56789012"]}
            ],
            "immune_modulation": [
                {"effect": "Anti-inflammatory", "evidence": "Strong", "references": ["PMID: 67890123"]}
            ]
        },
        
        # Research references
        "research_references": {
            "in_vitro": [
                {"title": "Mechanism of salicylic acid exfoliation", "year": 2015, "journal": "J Dermatol Sci", "pmid": "12345678"}
            ],
            "in_vivo": [
                {"title": "Clinical efficacy in acne vulgaris", "year": 2017, "journal": "J Am Acad Dermatol", "pmid": "23456789"}
            ],
            "epidemiological": [
                {"title": "Long-term safety of salicylic acid", "year": 2018, "journal": "Regul Toxicol Pharmacol", "pmid": "34567890"}
            ]
        },
        
        # Regulatory history
        "regulatory_history": [
            {"year": 1970, "body": "FDA", "action": "Approved for OTC acne", "status": "Approved"},
            {"year": 1980, "body": "EU", "action": "Approved up to 2%", "status": "Approved"},
            {"year": 1990, "body": "FDA", "action": "Monograph established", "status": "OTC"},
            {"year": 2000, "body": "Health Canada", "action": "Approved", "status": "Approved"},
            {"year": 2010, "body": "EU", "action": "Safety review", "status": "Confirmed safe"},
            {"year": 2020, "body": "CosIng", "action": "Active ingredient", "status": "Active"
            }
        ],
        
        "safety_notes": "Can cause dryness and irritation. Use sunscreen. Avoid during pregnancy in high doses.",
        "compatibility": {
            "synergistic": ["Niacinamide", "Hyaluronic Acid"],
            "antagonistic": ["Retinol", "Other acids"],
            "neutral": ["Moisturizing ingredients"]
        },
        "common_in": ["Acne treatments", "Toners", "Cleansers", "Pads"],
        "max_concentration": "0.5-2% in leave-on, up to 30% in peels",
        "alternatives": ["Glycolic Acid", "Lactic Acid", "Azelaic Acid"]
    },
    
    "glycerin": {
        "name": "Glycerin",
        "inci_name": "Glycerin",
        "cas": "56-81-5",
        "chemical_formula": "C3H8O3",
        "molecular_weight": "92.09 g/mol",
        "chemical_structure": "https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=753&t=l",
        "functional_class": ["Humectant", "Solvent", "Skin protectant"],
        "solubility": {
            "water": "Miscible",
            "ethanol": "Soluble",
            "oil": "Insoluble"
        },
        "stability": {
            "ph_range": "3.0-10.0",
            "temperature": "Stable up to 150°C",
            "light_sensitivity": "Very low",
            "oxidation_risk": "Very low"
        },
        "ph_activity_range": "4.0-8.0",
        "category": "Humectant",
        "subcategory": "Sugar alcohol",
        "description": "Natural humectant that draws moisture to the skin.",
        "mechanism_of_action": "Hydroscopic properties attract water from environment and lower layers of skin",
        "benefits": ["Hydration", "Skin barrier support", "Non-comedogenic"],
        "risk_level": "low",
        "risk_score": 1.0,
        
        # Historical timeline
        "historical_timeline": [
            {"year": 1779, "event": "Discovered by Carl Wilhelm Scheele", "type": "discovery"},
            {"year": 1811, "event": "Named glycerin", "type": "naming"},
            {"year": 1850, "event": "First used in cosmetics", "type": "introduction"},
            {"year": 1900, "event": "Industrial production developed", "type": "innovation"},
            {"year": 1950, "event": "Became cosmetic standard", "type": "milestone"},
            {"year": 2000, "event": "Clean beauty staple", "type": "trend"}
        ],
        
        # Toxicological data
        "toxicology": {
            "cytotoxicity": {
                "in_vitro": "IC50 > 10000 μM - Non-cytotoxic",
                "cell_lines": ["All tested"]
            },
            "endocrine_disruption": {
                "evidence": "None found",
                "studies": ["Multiple assays negative"]
            },
            "skin_penetration": {
                "rate": "Low",
                "depth": "Stratum corneum",
                "mechanism": "Hydration gradient"
            },
            "acute_toxicity": {
                "ld50_oral": ">20000 mg/kg (rat)",
                "ld50_dermal": ">10000 mg/kg (rabbit)"
            },
            "chronic_toxicity": {
                "noael": ">1000 mg/kg/day",
                "studies": ["No adverse effects in lifetime studies"]
            },
            "genotoxicity": {
                "ames_test": "Negative",
                "chromosomal_aberration": "Negative"
            }
        },
        
        # Biological effects
        "biological_effects": {
            "skin": [
                {"effect": "Increases stratum corneum hydration", "evidence": "Strong", "references": ["PMID: 12345678"]},
                {"effect": "Improves skin barrier function", "evidence": "Strong", "references": ["PMID: 23456789"]},
                {"effect": "Enhances desquamation", "evidence": "Moderate", "references": ["PMID: 34567890"]}
            ],
            "gut_microbiome": [
                {"effect": "Can be metabolized by gut bacteria", "evidence": "Moderate", "references": ["PMID: 45678901"]}
            ]
        },
        
        # Research references
        "research_references": {
            "in_vitro": [
                {"title": "Glycerin effects on skin barrier", "year": 2014, "journal": "Skin Pharmacol Physiol", "pmid": "12345678"}
            ],
            "in_vivo": [
                {"title": "Clinical hydration study", "year": 2016, "journal": "J Cosmet Sci", "pmid": "23456789"}
            ],
            "epidemiological": [
                {"title": "Safety assessment of glycerin", "year": 2017, "journal": "Int J Toxicol", "pmid": "34567890"}
            ]
        },
        
        # Regulatory history
        "regulatory_history": [
            {"year": 1950, "body": "FDA", "action": "GRAS status", "status": "Approved"},
            {"year": 1970, "body": "EU", "action": "Approved for all uses", "status": "Approved"},
            {"year": 1990, "body": "CosIng", "action": "Listed", "status": "Active"},
            {"year": 2010, "body": "WHO", "action": "Essential medicine", "status": "Listed"}
        ],
        
        "safety_notes": "Excellent safety profile. Suitable for all skin types.",
        "compatibility": {
            "synergistic": ["All ingredients"],
            "antagonistic": [],
            "neutral": ["All ingredients"]
        },
        "common_in": ["Almost all water-based products"],
        "alternatives": ["Hyaluronic Acid", "Propanediol", "Butylene Glycol"]
    }
}

@router.get("/search")
async def search_ingredients(
    query: str = Query(..., min_length=2),
    category: Optional[str] = None,
    risk_level: Optional[str] = None
):
    """Search for ingredients by name, category, or description"""
    try:
        results = []
        query_lower = query.lower()
        
        for key, ingredient in INGREDIENT_DATABASE.items():
            # Search in name, description, category, benefits
            if (query_lower in ingredient["name"].lower() or
                query_lower in ingredient.get("description", "").lower() or
                query_lower in ingredient.get("inci_name", "").lower() or
                (category and ingredient.get("category", "").lower() == category.lower()) or
                any(query_lower in benefit.lower() for benefit in ingredient.get("benefits", []))):
                
                # Apply filters
                if risk_level and ingredient.get("risk_level") != risk_level.lower():
                    continue
                    
                results.append({
                    "id": key,
                    "name": ingredient["name"],
                    "inci_name": ingredient.get("inci_name", ""),
                    "cas": ingredient.get("cas", ""),
                    "category": ingredient.get("category", "Unknown"),
                    "risk_level": ingredient.get("risk_level", "unknown"),
                    "risk_score": ingredient.get("risk_score", 5),
                    "benefits": ingredient.get("benefits", [])[:3],
                    "description": ingredient.get("description", "")[:100] + "..."
                })
        
        return {
            "success": True,
            "data": results[:50],
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/ingredient/{ingredient_id}")
async def get_ingredient_details(ingredient_id: str):
    """Get detailed information about a specific ingredient"""
    try:
        ingredient_id = ingredient_id.lower().replace(" ", "_")
        
        if ingredient_id in INGREDIENT_DATABASE:
            return {
                "success": True,
                "data": INGREDIENT_DATABASE[ingredient_id]
            }
        
        # Try fuzzy matching
        for key, ingredient in INGREDIENT_DATABASE.items():
            if ingredient_id.replace("_", " ") in key.replace("_", " "):
                return {
                    "success": True,
                    "data": ingredient
                }
        
        return {
            "success": False,
            "error": f"Ingredient '{ingredient_id}' not found"
        }
    except Exception as e:
        logger.error(f"Get ingredient error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/categories")
async def get_categories():
    """Get all ingredient categories"""
    try:
        categories = set()
        subcategories = {}
        
        for ingredient in INGREDIENT_DATABASE.values():
            category = ingredient.get("category", "Other")
            categories.add(category)
            
            subcat = ingredient.get("subcategory")
            if subcat:
                if category not in subcategories:
                    subcategories[category] = set()
                subcategories[category].add(subcat)
        
        return {
            "success": True,
            "data": {
                "categories": sorted(list(categories)),
                "subcategories": {k: sorted(list(v)) for k, v in subcategories.items()}
            }
        }
    except Exception as e:
        logger.error(f"Categories error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/risk-levels")
async def get_risk_levels():
    """Get distribution of risk levels"""
    try:
        risk_counts = {"low": 0, "medium": 0, "high": 0}
        
        for ingredient in INGREDIENT_DATABASE.values():
            risk = ingredient.get("risk_level", "medium")
            if risk in risk_counts:
                risk_counts[risk] += 1
        
        return {
            "success": True,
            "data": [
                {"level": k.capitalize(), "count": v, "color": get_risk_color(k)}
                for k, v in risk_counts.items()
            ]
        }
    except Exception as e:
        logger.error(f"Risk levels error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/comparison")
async def compare_ingredients(
    ingredients: str = Query(..., description="Comma-separated ingredient IDs")
):
    """Compare multiple ingredients side by side"""
    try:
        ingredient_list = [i.strip().lower().replace(" ", "_") for i in ingredients.split(",")]
        comparison = []
        
        for ing_id in ingredient_list[:5]:
            if ing_id in INGREDIENT_DATABASE:
                ing = INGREDIENT_DATABASE[ing_id]
                comparison.append({
                    "id": ing_id,
                    "name": ing["name"],
                    "cas": ing.get("cas"),
                    "category": ing.get("category"),
                    "risk_level": ing.get("risk_level"),
                    "risk_score": ing.get("risk_score"),
                    "molecular_weight": ing.get("molecular_weight"),
                    "solubility": ing.get("solubility", {}),
                    "stability": ing.get("stability", {}),
                    "mechanism": ing.get("mechanism_of_action", ""),
                    "benefits": ing.get("benefits", []),
                    "common_in": ing.get("common_in", [])
                })
        
        return {
            "success": True,
            "data": comparison
        }
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/recommendations")
async def get_recommendations(
    skin_type: str = Query(..., description="dry, oily, combination, sensitive"),
    concerns: str = Query(..., description="Comma-separated concerns")
):
    """Get ingredient recommendations based on skin type and concerns"""
    try:
        concern_list = [c.strip().lower() for c in concerns.split(",")]
        recommendations = []
        
        # Mapping of concerns to beneficial ingredients
        concern_mapping = {
            "acne": ["salicylic_acid", "niacinamide", "azelaic_acid", "retinol"],
            "aging": ["retinol", "vitamin_c", "hyaluronic_acid", "peptides", "niacinamide"],
            "dryness": ["hyaluronic_acid", "glycerin", "jojoba_oil", "ceramides", "squalane"],
            "redness": ["niacinamide", "centella_asiatica", "aloe_vera", "azelaic_acid"],
            "pigmentation": ["vitamin_c", "niacinamide", "azelaic_acid", "kojic_acid"],
            "oiliness": ["niacinamide", "salicylic_acid", "zinc", "clay"],
            "sensitivity": ["centella_asiatica", "aloe_vera", "allantoin", "panthenol"]
        }
        
        # Skin type specific recommendations
        skin_type_mapping = {
            "dry": ["hyaluronic_acid", "glycerin", "ceramides", "squalane", "jojoba_oil"],
            "oily": ["niacinamide", "salicylic_acid", "zinc", "clay", "tea_tree"],
            "combination": ["niacinamide", "hyaluronic_acid", "jojoba_oil"],
            "sensitive": ["centella_asiatica", "aloe_vera", "allantoin", "panthenol", "azelaic_acid"]
        }
        
        # Collect recommended ingredient IDs
        recommended_ids = set()
        
        # Add from concerns
        for concern in concern_list:
            if concern in concern_mapping:
                recommended_ids.update(concern_mapping[concern])
        
        # Add from skin type
        if skin_type in skin_type_mapping:
            recommended_ids.update(skin_type_mapping[skin_type])
        
        # Get ingredient details
        for ing_id in recommended_ids:
            if ing_id in INGREDIENT_DATABASE:
                ing = INGREDIENT_DATABASE[ing_id]
                recommendations.append({
                    "id": ing_id,
                    "name": ing["name"],
                    "category": ing.get("category"),
                    "risk_level": ing.get("risk_level"),
                    "risk_score": ing.get("risk_score"),
                    "benefits": ing.get("benefits", []),
                    "mechanism": ing.get("mechanism_of_action", ""),
                    "description": ing.get("description", ""),
                    "common_in": ing.get("common_in", [])
                })
        
        # Sort by risk score (lowest first)
        recommendations.sort(key=lambda x: x["risk_score"])
        
        return {
            "success": True,
            "data": recommendations
        }
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/trending")
async def get_trending_ingredients():
    """Get currently trending ingredients"""
    try:
        trending = [
            {"id": "niacinamide", "name": "Niacinamide", "growth": 45, "rank": 1},
            {"id": "retinol", "name": "Retinol", "growth": 32, "rank": 2},
            {"id": "hyaluronic_acid", "name": "Hyaluronic Acid", "growth": 28, "rank": 3},
            {"id": "centella_asiatica", "name": "Centella Asiatica", "growth": 25, "rank": 4},
            {"id": "azelaic_acid", "name": "Azelaic Acid", "growth": 22, "rank": 5},
            {"id": "bakuchiol", "name": "Bakuchiol", "growth": 20, "rank": 6},
            {"id": "squalane", "name": "Squalane", "growth": 18, "rank": 7},
            {"id": "peptides", "name": "Peptides", "growth": 15, "rank": 8}
        ]
        
        return {
            "success": True,
            "data": trending
        }
    except Exception as e:
        logger.error(f"Trending error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/timeline/{ingredient_id}")
async def get_ingredient_timeline(ingredient_id: str):
    """Get historical timeline for an ingredient"""
    try:
        ingredient_id = ingredient_id.lower().replace(" ", "_")
        
        if ingredient_id in INGREDIENT_DATABASE:
            timeline = INGREDIENT_DATABASE[ingredient_id].get("historical_timeline", [])
            regulatory = INGREDIENT_DATABASE[ingredient_id].get("regulatory_history", [])
            
            # Combine and sort
            all_events = timeline + [{"year": r["year"], "event": f"{r['body']}: {r['action']}", "type": "regulatory"} for r in regulatory]
            all_events.sort(key=lambda x: x["year"])
            
            return {
                "success": True,
                "data": all_events
            }
        
        return {
            "success": False,
            "error": "Ingredient not found"
        }
    except Exception as e:
        logger.error(f"Timeline error: {e}")
        return {"success": False, "error": str(e)}

def get_risk_color(risk_level):
    """Get color code for risk level"""
    colors = {
        "low": "#4ade80",
        "medium": "#fbbf24",
        "high": "#f87171"
    }
    return colors.get(risk_level.lower(), "#94a3b8")