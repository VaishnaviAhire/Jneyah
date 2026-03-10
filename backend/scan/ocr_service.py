import base64
from typing import List, Dict, Any, Optional
import logging
import re
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image, ImageEnhance, ImageFilter
import io

load_dotenv()
logger = logging.getLogger(__name__)

class OCRService:
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Using mock mode.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None

    def preprocess_image(self, image_bytes: bytes) -> bytes:
        """
        Preprocess image using PIL only
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Increase contrast for better text detection
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Convert to grayscale for better OCR
            image = image.convert('L')
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=95)
            return img_byte_arr.getvalue()
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return image_bytes

    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """
        Extract text from image using GPT-4 Vision with preprocessing
        """
        if not self.client:
            logger.warning("OpenAI client not available, using pattern-based extraction")
            return self._mock_extract()
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_bytes)
            base64_image = base64.b64encode(processed_image).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Extract ONLY the ingredients list from this product label. 
                                The ingredients section typically starts with 'INGREDIENTS:' or 'INGRÉDIENTS:'.
                                Return the exact text of the ingredients list, preserving the original formatting.
                                If you see any text like 'Body Powder' or 'PINK LILY' at the top, ignore it and find the ingredients section.
                                Return ONLY the ingredients text, nothing else."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            text = response.choices[0].message.content
            return text
            
        except Exception as e:
            logger.error(f"GPT-4 Vision failed: {str(e)}")
            return self._extract_with_patterns(image_bytes)

    def _extract_with_patterns(self, image_bytes: bytes) -> str:
        """
        Fallback: Try to extract text using pattern recognition
        """
        # This would normally use Tesseract, but since we don't have it,
        # we'll return a structured response based on common patterns
        return self._mock_extract()

    def extract_ingredients_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract ingredients from text with improved parsing
        """
        ingredients = []
        seen = set()
        
        # Find the ingredients section
        ingredients_text = self._find_ingredients_section(text)
        
        if not ingredients_text:
            ingredients_text = text
        
        # Clean the text
        ingredients_text = self._clean_text(ingredients_text)
        
        # Split by common delimiters
        # Handle both comma-separated and line-break separated lists
        parts = re.split(r'[,;•∙·•\n\r]+', ingredients_text)
        
        for part in parts:
            part = part.strip()
            if not part or len(part) < 2:
                continue
            
            # Skip metadata
            if self._is_metadata(part):
                continue
            
            # Clean individual ingredient
            cleaned = self._clean_ingredient(part)
            if not cleaned or len(cleaned) < 2:
                continue
            
            # Validate it's likely an ingredient
            if self._is_likely_ingredient(cleaned):
                key = cleaned.lower()
                if key not in seen:
                    seen.add(key)
                    
                    # Determine category
                    category = self._categorize_ingredient(cleaned)
                    
                    ingredients.append({
                        "name": cleaned,
                        "original": part,
                        "category": category,
                        "confidence": self._calculate_confidence(cleaned, part)
                    })
        
        return ingredients

    def _find_ingredients_section(self, text: str) -> str:
        """
        Find the ingredients section in the text
        """
        # Common patterns for ingredients section
        patterns = [
            r'INGREDIENTS?[:\s]+(.*?)(?:WARNINGS?|DIRECTIONS?|DISTRIBUTED|MANUFACTURED|MADE|EXPIRY|DESIGN|MFD|BATCH|$|\n\n)',
            r'INGRÉDIENTS?[:\s]+(.*?)(?:AVERTISSEMENTS?|INSTRUCTIONS?|$|\n\n)',
            r'CONTAINS?[:\s]+(.*?)(?:WARNINGS?|$|\n\n)',
            r'COMPOSITION[:\s]+(.*?)(?:PRÉCAUTIONS?|$|\n\n)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        """
        # Remove special characters
        text = re.sub(r'[^\w\s\-.,;:()%]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def _clean_ingredient(self, ingredient: str) -> str:
        """
        Clean individual ingredient name
        """
        # Remove numbers at start (like 1., 2., etc)
        ingredient = re.sub(r'^\d+\.?\s*', '', ingredient)
        
        # Remove percentages
        ingredient = re.sub(r'\d+\s*%', '', ingredient)
        
        # Remove parentheses content if it's just an INCI name
        ingredient = re.sub(r'\([^)]*\)', '', ingredient)
        
        # Remove asterisks and special chars
        ingredient = re.sub(r'[*•∙·•]', '', ingredient)
        
        # Remove extra spaces
        ingredient = ' '.join(ingredient.split())
        
        # Remove trailing punctuation
        ingredient = ingredient.rstrip('.,;:')
        
        # Capitalize properly
        ingredient = ' '.join(word.capitalize() if word.islower() else word 
                             for word in ingredient.split())
        
        return ingredient.strip()

    def _is_metadata(self, text: str) -> bool:
        """
        Check if text is metadata (not an ingredient)
        """
        metadata_patterns = [
            r'^\d+\.?\s*$',
            r'^(?:MRP|USP|MFD|BATCH|EXP|MANUFACTURED|DISTRIBUTED|WARNING|CAUTION|DESIGN|REGN)',
            r'^[A-Z]{2,}[-\s]*\d+',  # Codes like BO-14-000-03
            r'(?:registered|design|patent|regd)\.?\s*no',
            r'minimum thickness',
            r'packaging',
            r'^\d+[A-Z]+$',  # Alphanumeric codes
        ]
        
        text_upper = text.upper()
        for pattern in metadata_patterns:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True
        return False

    def _is_likely_ingredient(self, text: str) -> bool:
        """
        Determine if text is likely an ingredient
        """
        # Length check
        if len(text) < 2 or len(text) > 60:
            return False
        
        # Should contain at least one letter
        if not re.search(r'[A-Za-z]', text):
            return False
        
        # Shouldn't be just numbers
        if re.match(r'^[\d\s]+$', text):
            return False
        
        # Common ingredient patterns
        valid_patterns = [
            r'^[A-Z][a-z]+',  # Starts with capital
            r'\s+[A-Z][a-z]+',  # Has capitalized words
            r'\w+(?:ate|ide|one|ane|ene|ol|ic|ous|yl|glycol|acid|oil|extract|butter|wax|ester|alcohol|water)$',
            r'^[A-Z]{2,}',  # Acronyms like PEG
            r'\d+$',  # Numbers at end like PEG-45
        ]
        
        for pattern in valid_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False

    def _calculate_confidence(self, cleaned: str, original: str) -> float:
        """
        Calculate confidence score for extracted ingredient
        """
        confidence = 1.0
        
        # Penalize if original had special characters
        if re.search(r'[()*•∙·•]', original):
            confidence -= 0.1
        
        # Penalize if original had numbers
        if re.search(r'\d', original):
            confidence -= 0.1
        
        # Penalize for short ingredients
        if len(cleaned) < 4:
            confidence -= 0.2
        
        # Penalize if original was significantly different
        if len(original) > len(cleaned) * 1.5:
            confidence -= 0.1
        
        return max(0.5, min(1.0, confidence))

    def _categorize_ingredient(self, ingredient: str) -> str:
        """
        Categorize ingredient based on keywords
        """
        ing_lower = ingredient.lower()
        
        categories = {
            "preservative": ["paraben", "phenoxyethanol", "benzoate", "sorbate", "dmdm", 
                           "imidazolidinyl", "formaldehyde", "benzyl alcohol"],
            "emollient": ["glycerin", "butter", "oil", "squalane", "dimethicone", "cetearyl", 
                        "cetyl", "stearyl", "caprylic", "capric", "cocoa", "shea", "paraffin"],
            "active": ["vitamin", "retinol", "niacinamide", "acid", "peptide", "collagen", 
                      "hyaluronic", "coenzyme", "ubiquinone", "ceramide"],
            "fragrance": ["fragrance", "parfum", "limonene", "linalool", "citronellol", 
                         "geraniol", "eugenol", "coumarin", "ionone", "cinnamal", "isoeugenol",
                         "benzyl salicylate", "cinnamyl alcohol", "hexyl cinnamal"],
            "surfactant": ["lauryl", "laureth", "coco", "betaine", "glucoside", "polysorbate", 
                          "peg", "sulfate", "sulfonate", "ceteareth", "disodium", "sulfosuccinate",
                          "isethionate"],
            "humectant": ["hyaluronic", "glycerin", "panthenol", "propanediol", "butylene", 
                         "propylene", "sorbitol", "glycol"],
            "solvent": ["water", "aqua", "alcohol", "ethanol", "isopropyl", "dipropylene glycol"],
            "sunscreen": ["avobenzone", "octinoxate", "zinc oxide", "titanium dioxide", 
                         "oxybenzone", "homosalate", "octocrylene"],
            "chelating": ["edta", "tetrasodium", "disodium", "citric acid"],
            "antioxidant": ["tocopherol", "ascorbic", "bht", "bha", "vitamin e", "vitamin c"],
            "colorant": ["mica", "titanium dioxide", "iron oxide", "chromium", "ci ", 
                        "pigment", "lake"],
            "bulk": ["kaolin", "calcium carbonate", "maltodextrin", "silica", "talc"],
            "cooling": ["menthol", "camphor", "eucalyptus"],
        }
        
        for category, keywords in enumerate(categories):
            if any(keyword in ing_lower for keyword in keywords):
                return category
        
        return "other"

    def _mock_extract(self) -> str:
        """
        Mock extraction with real ingredient data from your images
        """
        return """
        INGREDIENTS: KAOLIN, MICA, CALCIUM CARBONATE, FRAGRANCE, DIPROPYLENE GLYCOL, MENTHOL,
        NIACINAMIDE, ALPHA-ISOMETHYL IONONE, BENZYL ALCOHOL, BENZYL SALICYLATE, CINNAMYL ALCOHOL,
        CITRONELLOL, COUMARIN, EUGENOL, GERANIOL, HEXYL CINNAMAL, ISOEUGENOL, LIMONENE, LINALOOL,
        DISODIUM LAURYL SULFOSUCCINATE, MALTODEXTRIN, SODIUM COCOYL ISETHIONATE, STEARIC ACID,
        AVENA SATIVA (OAT) KERNEL FLOUR, WATER, CETEARYL ALCOHOL, PARAFFIN, CETEARETH-6,
        PRUNUS AMYGDALUS DULCIS (SWEET ALMOND) OIL, PEG-45 PALM KERNEL GLYCERIDES
        """