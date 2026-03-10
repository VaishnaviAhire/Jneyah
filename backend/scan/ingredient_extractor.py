
import re
from typing import List, Dict, Any, Optional, Set
from difflib import SequenceMatcher
import logging
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)

class IngredientExtractor:
    
    # Expanded ingredient database
    INGREDIENT_DATABASE = {
        # Common names to standardized names
        "water": "Water",
        "aqua": "Water",
        "glycerin": "Glycerin",
        "glycerol": "Glycerin",
        "cetearyl alcohol": "Cetearyl Alcohol",
        "cetyl alcohol": "Cetyl Alcohol",
        "stearyl alcohol": "Stearyl Alcohol",
        "dimethicone": "Dimethicone",
        "shea butter": "Shea Butter",
        "butyrospermum parkii": "Shea Butter",
        "coconut oil": "Coconut Oil",
        "cocos nucifera": "Coconut Oil",
        "sweet almond oil": "Sweet Almond Oil",
        "prunus amygdalus dulcis": "Sweet Almond Oil",
        "jojoba oil": "Jojoba Oil",
        "simmondsia chinensis": "Jojoba Oil",
        "tocopherol": "Tocopherol",
        "vitamin e": "Tocopherol",
        "tocopheryl acetate": "Tocopheryl Acetate",
        "phenoxyethanol": "Phenoxyethanol",
        "fragrance": "Fragrance",
        "parfum": "Fragrance",
        "limonene": "Limonene",
        "linalool": "Linalool",
        "citronellol": "Citronellol",
        "geraniol": "Geraniol",
        "niacinamide": "Niacinamide",
        "sodium hyaluronate": "Sodium Hyaluronate",
        "hyaluronic acid": "Hyaluronic Acid",
        "kaolin": "Kaolin",
        "mica": "Mica",
        "calcium carbonate": "Calcium Carbonate",
        "dipropylene glycol": "Dipropylene Glycol",
        "menthol": "Menthol",
        "alpha-isomethyl ionone": "Alpha-Isomethyl Ionone",
        "benzyl alcohol": "Benzyl Alcohol",
        "benzyl salicylate": "Benzyl Salicylate",
        "cinnamyl alcohol": "Cinnamyl Alcohol",
        "coumarin": "Coumarin",
        "eugenol": "Eugenol",
        "hexyl cinnamal": "Hexyl Cinnamal",
        "isoeugenol": "Isoeugenol",
        "disodium lauryl sulfosuccinate": "Disodium Lauryl Sulfosuccinate",
        "maltodextrin": "Maltodextrin",
        "sodium cocoyl isethionate": "Sodium Cocoyl Isethionate",
        "stearic acid": "Stearic Acid",
        "avena sativa": "Oat Kernel Flour",
        "paraffin": "Paraffin",
        "ceteareth-6": "Ceteareth-6",
        "peg-45 palm kernel glycerides": "PEG-45 Palm Kernel Glycerides"
    }
    
    # Category mapping
    INGREDIENT_CATEGORIES = {
        "Water": "solvent",
        "Glycerin": "humectant",
        "Cetearyl Alcohol": "emollient",
        "Dimethicone": "emollient",
        "Shea Butter": "emollient",
        "Coconut Oil": "emollient",
        "Sweet Almond Oil": "emollient",
        "Jojoba Oil": "emollient",
        "Tocopherol": "antioxidant",
        "Tocopheryl Acetate": "antioxidant",
        "Phenoxyethanol": "preservative",
        "Fragrance": "fragrance",
        "Limonene": "fragrance",
        "Linalool": "fragrance",
        "Citronellol": "fragrance",
        "Geraniol": "fragrance",
        "Niacinamide": "active",
        "Sodium Hyaluronate": "humectant",
        "Hyaluronic Acid": "humectant",
        "Kaolin": "absorbent",
        "Mica": "colorant",
        "Calcium Carbonate": "bulk",
        "Dipropylene Glycol": "solvent",
        "Menthol": "cooling",
        "Alpha-Isomethyl Ionone": "fragrance",
        "Benzyl Alcohol": "preservative",
        "Benzyl Salicylate": "fragrance",
        "Cinnamyl Alcohol": "fragrance",
        "Coumarin": "fragrance",
        "Eugenol": "fragrance",
        "Hexyl Cinnamal": "fragrance",
        "Isoeugenol": "fragrance",
        "Disodium Lauryl Sulfosuccinate": "surfactant",
        "Maltodextrin": "bulk",
        "Sodium Cocoyl Isethionate": "surfactant",
        "Stearic Acid": "emollient",
        "Oat Kernel Flour": "absorbent",
        "Paraffin": "emollient",
        "Ceteareth-6": "emulsifier",
        "PEG-45 Palm Kernel Glycerides": "emulsifier"
    }
    
    # Risk levels (1-10, higher = more risky)
    INGREDIENT_RISK = {
        "Water": 1,
        "Glycerin": 1,
        "Cetearyl Alcohol": 1,
        "Dimethicone": 1,
        "Shea Butter": 1,
        "Coconut Oil": 2,
        "Sweet Almond Oil": 1,
        "Jojoba Oil": 1,
        "Tocopherol": 1,
        "Tocopheryl Acetate": 1,
        "Phenoxyethanol": 3,
        "Fragrance": 4,
        "Limonene": 3,
        "Linalool": 3,
        "Citronellol": 3,
        "Geraniol": 3,
        "Niacinamide": 1,
        "Sodium Hyaluronate": 1,
        "Hyaluronic Acid": 1,
        "Kaolin": 1,
        "Mica": 1,
        "Calcium Carbonate": 1,
        "Dipropylene Glycol": 2,
        "Menthol": 2,
        "Alpha-Isomethyl Ionone": 3,
        "Benzyl Alcohol": 3,
        "Benzyl Salicylate": 3,
        "Cinnamyl Alcohol": 3,
        "Coumarin": 3,
        "Eugenol": 3,
        "Hexyl Cinnamal": 3,
        "Isoeugenol": 3,
        "Disodium Lauryl Sulfosuccinate": 1,
        "Maltodextrin": 1,
        "Sodium Cocoyl Isethionate": 1,
        "Stearic Acid": 1,
        "Oat Kernel Flour": 1,
        "Paraffin": 2,
        "Ceteareth-6": 2,
        "PEG-45 Palm Kernel Glycerides": 2
    }
    
    @staticmethod
    def extract_from_text(text: str, threshold: float = 80) -> List[Dict[str, Any]]:
        """
        Extract ingredients using fuzzy matching
        """
        ingredients = []
        seen = set()
        
        # Clean and normalize text
        text = IngredientExtractor._normalize_text(text)
        
        # Extract ingredients section
        ingredients_text = IngredientExtractor._extract_ingredients_section(text)
        
        if not ingredients_text:
            ingredients_text = text
        
        # Split by common delimiters
        parts = re.split(r'[,;•∙·•\n\r]+', ingredients_text)
        
        for part in parts:
            part = part.strip()
            if not part or len(part) < 2:
                continue
            
            # Clean the part
            cleaned = IngredientExtractor._clean_ingredient(part)
            
            if not cleaned:
                continue
            
            # Try exact match
            if cleaned in IngredientExtractor.INGREDIENT_DATABASE:
                name = IngredientExtractor.INGREDIENT_DATABASE[cleaned]
                if name not in seen:
                    seen.add(name)
                    ingredients.append({
                        "name": name,
                        "original": part,
                        "category": IngredientExtractor.INGREDIENT_CATEGORIES.get(name, "other"),
                        "risk_level": IngredientExtractor._get_risk_level(name),
                        "confidence": 1.0
                    })
                continue
            
            # Try fuzzy matching
            match_result = IngredientExtractor._fuzzy_match(cleaned, threshold)
            if match_result:
                name, score = match_result
                if name not in seen:
                    seen.add(name)
                    ingredients.append({
                        "name": name,
                        "original": part,
                        "category": IngredientExtractor.INGREDIENT_CATEGORIES.get(name, "other"),
                        "risk_level": IngredientExtractor._get_risk_level(name),
                        "confidence": score / 100
                    })
        
        return ingredients
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for processing"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep letters, numbers, and common punctuation
        text = re.sub(r'[^\w\s\-.,;:()]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def _extract_ingredients_section(text: str) -> str:
        """Extract ingredients section from text"""
        patterns = [
            r'ingredients?[:\s]+(.*?)(?:warnings?|directions?|distributed|manufactured|made|\n\s*\n|$)',
            r'ingrédients?[:\s]+(.*?)(?:avertissements?|instructions?|$)',
            r'contains?[:\s]+(.*?)(?:warnings?|$)',
            r'composition[:\s]+(.*?)(?:précautions?|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    @staticmethod
    def _clean_ingredient(ingredient: str) -> str:
        """Clean individual ingredient"""
        # Remove numbers at start
        ingredient = re.sub(r'^\d+\.?\s*', '', ingredient)
        
        # Remove percentages
        ingredient = re.sub(r'\d+\s*%', '', ingredient)
        
        # Remove parentheses
        ingredient = re.sub(r'\([^)]*\)', '', ingredient)
        
        # Remove extra spaces
        ingredient = ' '.join(ingredient.split())
        
        # Remove trailing punctuation
        ingredient = ingredient.rstrip('.,;:')
        
        # Convert to lowercase
        ingredient = ingredient.lower().strip()
        
        return ingredient
    
    @staticmethod
    def _fuzzy_match(ingredient: str, threshold: float = 80) -> Optional[tuple]:
        """
        Fuzzy match ingredient against database
        """
        # Try to match against database keys
        result = process.extractOne(
            ingredient,
            IngredientExtractor.INGREDIENT_DATABASE.keys(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=threshold
        )
        
        if result:
            matched_key, score = result[0], result[1]
            return IngredientExtractor.INGREDIENT_DATABASE[matched_key], score
        
        # Try to match against values
        result = process.extractOne(
            ingredient,
            IngredientExtractor.INGREDIENT_DATABASE.values(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=threshold
        )
        
        if result:
            return result[0], result[1]
        
        return None
    
    @staticmethod
    def _get_risk_level(name: str) -> str:
        """Convert numeric risk to level"""
        risk_score = IngredientExtractor.INGREDIENT_RISK.get(name, 3)
        
        if risk_score <= 2:
            return "low"
        elif risk_score <= 4:
            return "medium"
        else:
            return "high"
        
        



# import re
# from typing import List, Dict, Any, Set, Optional
# from difflib import SequenceMatcher
# import logging

# logger = logging.getLogger(__name__)

# class IngredientExtractor:
    
#     # Known ingredient database (simplified)
#     KNOWN_INGREDIENTS = {
#         "paraben": "Paraben",
#         "methylparaben": "Methylparaben",
#         "propylparaben": "Propylparaben",
#         "butylparaben": "Butylparaben",
#         "ethylparaben": "Ethylparaben",
#         "phenoxyethanol": "Phenoxyethanol",
#         "glycerin": "Glycerin",
#         "glycerol": "Glycerin",
#         "vitamin c": "Vitamin C",
#         "ascorbic acid": "Ascorbic Acid",
#         "retinol": "Retinol",
#         "niacinamide": "Niacinamide",
#         "hyaluronic acid": "Hyaluronic Acid",
#         "sodium hyaluronate": "Sodium Hyaluronate",
#         "sodium lauryl sulfate": "Sodium Lauryl Sulfate",
#         "sls": "Sodium Lauryl Sulfate",
#         "fragrance": "Fragrance",
#         "parfum": "Fragrance",
#         "alcohol": "Alcohol",
#         "alcohol denat": "Alcohol Denat",
#         "zinc oxide": "Zinc Oxide",
#         "titanium dioxide": "Titanium Dioxide",
#         "shea butter": "Shea Butter",
#         "coconut oil": "Coconut Oil",
#         "jojoba oil": "Jojoba Oil",
#         "dimethicone": "Dimethicone",
#         "glycolic acid": "Glycolic Acid",
#         "lactic acid": "Lactic Acid",
#         "salicylic acid": "Salicylic Acid",
#         "citric acid": "Citric Acid"
#     }

#     @staticmethod
#     def extract_from_text(text: str) -> List[Dict[str, Any]]:
#         """
#         Extract ingredients from text with improved accuracy
#         """
#         ingredients = []
#         seen = set()
        
#         # Split by common delimiters
#         lines = text.split('\n')
#         for line in lines:
#             # Look for ingredient list patterns
#             if any(keyword in line.lower() for keyword in ['ingredients:', 'ingrédients:', 'contains:', 'ingredient list:']):
#                 ingredients.extend(IngredientExtractor.parse_ingredient_line(line))
#                 continue
            
#             # Split by commas and periods
#             parts = re.split(r'[,\.]', line)
#             for part in parts:
#                 # Look for individual ingredients
#                 found = IngredientExtractor.find_ingredients_in_text(part)
#                 ingredients.extend(found)
        
#         # Deduplicate and clean
#         unique_ingredients = []
#         for ing in ingredients:
#             key = ing['name'].lower()
#             if key not in seen:
#                 seen.add(key)
#                 unique_ingredients.append(ing)
        
#         return unique_ingredients

#     @staticmethod
#     def parse_ingredient_line(line: str) -> List[Dict[str, Any]]:
#         """
#         Parse a line containing ingredient list
#         """
#         ingredients = []
        
#         # Remove the "Ingredients:" label
#         line = re.sub(r'^.*?(?:ingredients|ingrédients|contains|ingredient list)[:\s]*', '', line, flags=re.IGNORECASE)
        
#         # Split by common delimiters
#         parts = re.split(r'[,;\.]|\s+\|\s+', line)
        
#         for part in parts:
#             part = part.strip()
#             if part and len(part) > 1:
#                 # Check if this looks like an ingredient
#                 if IngredientExtractor.is_likely_ingredient(part):
#                     ingredients.append({
#                         "name": part,
#                         "original": part,
#                         "confidence": 0.9
#                     })
        
#         return ingredients

#     @staticmethod
#     def find_ingredients_in_text(text: str) -> List[Dict[str, Any]]:
#         """
#         Find individual ingredients within a text segment
#         """
#         found = []
#         text_lower = text.lower()
        
#         # Check known ingredients
#         for key, name in IngredientExtractor.KNOWN_INGREDIENTS.items():
#             if key in text_lower:
#                 # Extract the actual text with original casing
#                 pattern = re.compile(re.escape(key), re.IGNORECASE)
#                 match = pattern.search(text)
#                 if match:
#                     found.append({
#                         "name": name,
#                         "original": match.group(),
#                         "matched_key": key,
#                         "confidence": 0.95
#                     })
        
#         # Look for INCI names (typically Latin names in parentheses)
#         inci_matches = re.finditer(r'\(([^)]+)\)', text)
#         for match in inci_matches:
#             inci_name = match.group(1).strip()
#             if len(inci_name) > 3:
#                 found.append({
#                     "name": inci_name,
#                     "original": match.group(),
#                     "type": "INCI",
#                     "confidence": 0.8
#                 })
        
#         return found

#     @staticmethod
#     def is_likely_ingredient(text: str) -> bool:
#         """
#         Determine if a text segment is likely an ingredient name
#         """
#         # Too short
#         if len(text) < 3:
#             return False
        
#         # Too long (probably a sentence)
#         if len(text) > 50:
#             return False
        
#         # Contains numbers (could be percentages or concentrations)
#         if re.search(r'\d+%|\d+\s*%', text):
#             return False
        
#         # Common ingredient patterns
#         patterns = [
#             r'^[A-Z][a-z]+',  # Starts with capital letter
#             r'\s+[A-Z][a-z]+\s+',  # Has capitalized words
#             r'[A-Z]{2,}',  # Has acronyms
#             r'\w+\s+acid',  # Something acid
#             r'\w+\s+oil',  # Something oil
#             r'\w+\s+extract',  # Something extract
#             r'\w+\s+butter',  # Something butter
#         ]
        
#         for pattern in patterns:
#             if re.search(pattern, text):
#                 return True
        
#         return False

#     @staticmethod
#     def normalize_ingredient_name(name: str) -> str:
#         """
#         Normalize ingredient name for matching
#         """
#         # Convert to lowercase
#         name = name.lower()
        
#         # Remove common prefixes
#         name = re.sub(r'^\d+\.?\s*', '', name)
        
#         # Remove percentages
#         name = re.sub(r'\d+%\s*', '', name)
        
#         # Remove parentheses content
#         name = re.sub(r'\([^)]*\)', '', name)
        
#         # Remove extra spaces
#         name = ' '.join(name.split())
        
#         return name.strip()

#     @staticmethod
#     def match_ingredient(ingredient: str, threshold: float = 0.8) -> Optional[str]:
#         """
#         Match an ingredient to known database using fuzzy matching
#         """
#         normalized = IngredientExtractor.normalize_ingredient_name(ingredient)
        
#         # Try exact match first
#         if normalized in IngredientExtractor.KNOWN_INGREDIENTS:
#             return IngredientExtractor.KNOWN_INGREDIENTS[normalized]
        
#         # Try fuzzy matching
#         best_match = None
#         best_ratio = 0
        
#         for known_key, known_name in IngredientExtractor.KNOWN_INGREDIENTS.items():
#             ratio = SequenceMatcher(None, normalized, known_key).ratio()
#             if ratio > best_ratio and ratio > threshold:
#                 best_ratio = ratio
#                 best_match = known_name
        
#         return best_match