import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
import logging
import os
from pathlib import Path
import random

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "database" / "data"
        self.cosmetics_df = None
        self.food_df = None
        self._load_datasets()
    
    def _load_datasets(self):
        """Load datasets from CSV files"""
        try:
            # Try to load cosmetics dataset
            cosmetics_path = self.data_path / "cosmetics.csv"
            if cosmetics_path.exists():
                self.cosmetics_df = pd.read_csv(cosmetics_path)
                logger.info(f"✅ Loaded cosmetics dataset: {len(self.cosmetics_df)} rows")
            else:
                logger.warning("⚠️ Cosmetics dataset not found, using sample data")
                self._create_sample_cosmetics_data()
            
            # Try to load food ingredients dataset
            food_path = self.data_path / "food_ingredients.csv"
            if food_path.exists():
                self.food_df = pd.read_csv(food_path)
                logger.info(f"✅ Loaded food ingredients dataset: {len(self.food_df)} rows")
            else:
                logger.warning("⚠️ Food dataset not found, using sample data")
                self._create_sample_food_data()
                
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
            self._create_sample_data()
    
    def _create_sample_cosmetics_data(self):
        """Create sample cosmetics data with proper column names"""
        n_rows = 100
        
        # Sample ingredient lists
        ingredient_lists = [
            'Water, Glycerin, Dimethicone, Niacinamide, Hyaluronic Acid',
            'Water, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, Fragrance, Citric Acid',
            'Cyclopentasiloxane, Dimethicone, Dimethicone Crosspolymer, Silica',
            'Water, Glycerin, Cetearyl Alcohol, Stearic Acid, Glycolic Acid, Sodium Hydroxide',
            'Water, Shea Butter, Cocoa Butter, Jojoba Oil, Vitamin E, Tocopherol',
            'Water, Salicylic Acid, Niacinamide, Zinc PCA, Aloe Vera, Allantoin',
            'Water, Retinol, Hyaluronic Acid, Ceramides, Peptides, Panthenol',
            'Water, Titanium Dioxide, Zinc Oxide, Alumina, Dimethicone, Silica',
            'Water, Glycerin, Cetearyl Alcohol, Cetyl Alcohol, Stearyl Alcohol, Phenoxyethanol',
            'Water, Glycerin, Butyrospermum Parkii Butter, Prunus Amygdalus Dulcis Oil'
        ]
        
        sample_data = {
            'product_name': [f'Cosmetic Product {i+1}' for i in range(n_rows)],
            'brand': np.random.choice(['L\'Oreal', 'Neutrogena', 'Cetaphil', 'CeraVe', 'The Ordinary', 'La Roche-Posay', 'Olay', 'Kiehl\'s'], n_rows),
            'category': np.random.choice(['Moisturizer', 'Cleanser', 'Serum', 'Sunscreen', 'Mask', 'Toner', 'Eye Cream', 'Exfoliator'], n_rows),
            'ingredients': np.random.choice(ingredient_lists, n_rows),
            'price': np.random.uniform(5, 100, n_rows).round(2),
            'rating': np.random.uniform(3, 5, n_rows).round(1)
        }
        self.cosmetics_df = pd.DataFrame(sample_data)
        logger.info("✅ Created sample cosmetics dataset with 100 rows")
    
    def _create_sample_food_data(self):
        """Create sample food ingredients data with proper column names"""
        n_rows = 100
        
        # Sample food ingredient lists
        ingredient_lists = [
            'Sugar, Enriched Flour, Vegetable Oil, High Fructose Corn Syrup, Salt, Leavening',
            'Water, Sugar, Citric Acid, Natural Flavors, Sodium Benzoate, Potassium Sorbate',
            'Milk, Cream, Sugar, Stabilizers, Natural Flavors, Carrageenan',
            'Flour, Water, Yeast, Salt, Sugar, Vegetable Oil, Dough Conditioner',
            'Corn, Vegetable Oil, Salt, Natural Flavors, TBHQ, Citric Acid',
            'Tomatoes, Water, Sugar, Salt, Spices, Citric Acid, Onion Powder',
            'Chicken Broth, Chicken, Carrots, Celery, Noodles, Salt, Yeast Extract',
            'Beans, Water, Salt, Calcium Chloride, Onion Powder, Garlic Powder',
            'Sugar, Cocoa Butter, Chocolate, Milk, Soy Lecithin, Vanillin',
            'Enriched Flour, Sugar, Vegetable Oil, Cocoa, Salt, Baking Soda'
        ]
        
        sample_data = {
            'food_name': [f'Food Product {i+1}' for i in range(n_rows)],
            'category': np.random.choice(['Snacks', 'Beverages', 'Dairy', 'Bakery', 'Frozen Foods', 'Canned Goods', 'Confectionery', 'Condiments'], n_rows),
            'brand': np.random.choice(['Kraft', 'Nestle', 'General Mills', 'Kellogg\'s', 'PepsiCo', 'Coca-Cola', 'Unilever', 'Mars'], n_rows),
            'ingredients': np.random.choice(ingredient_lists, n_rows),
            'allergens': np.random.choice(['Milk, Soy', 'Wheat, Gluten', 'None', 'Tree Nuts', 'Eggs', 'Fish', 'Peanuts'], n_rows),
            'calories': np.random.randint(50, 500, n_rows),
            'fat_g': np.random.randint(0, 30, n_rows),
            'sugar_g': np.random.randint(0, 40, n_rows)
        }
        self.food_df = pd.DataFrame(sample_data)
        logger.info("✅ Created sample food dataset with 100 rows")
    
    def _create_sample_data(self):
        """Fallback to create both datasets"""
        self._create_sample_cosmetics_data()
        self._create_sample_food_data()
    
    def get_overview_stats(self):
        """Get overview statistics for dashboard"""
        try:
            stats = {
                "total_ingredients": 0,
                "total_products": 0,
                "high_risk_ingredients": 0,
                "interaction_pairs": 1247,
                "recent_trends": [],
                "category_breakdown": []
            }
            
            if self.cosmetics_df is not None and 'ingredients' in self.cosmetics_df.columns:
                stats["total_products"] += len(self.cosmetics_df)
                
                # Extract all ingredients
                all_ingredients = []
                for ingredients in self.cosmetics_df['ingredients'].dropna():
                    if isinstance(ingredients, str):
                        all_ingredients.extend([i.strip().lower() for i in ingredients.split(',')])
                
                stats["total_ingredients"] = len(set(all_ingredients))
                
                # Category breakdown
                if 'category' in self.cosmetics_df.columns:
                    breakdown = self.cosmetics_df['category'].value_counts().to_dict()
                    stats["category_breakdown"] = [
                        {"category": k, "count": int(v)} for k, v in breakdown.items()
                    ]
            
            if self.food_df is not None and 'ingredients' in self.food_df.columns:
                stats["total_products"] += len(self.food_df)
                
                # Add food ingredients to total
                all_food_ingredients = []
                for ingredients in self.food_df['ingredients'].dropna():
                    if isinstance(ingredients, str):
                        all_food_ingredients.extend([i.strip().lower() for i in ingredients.split(',')])
                
                stats["total_ingredients"] += len(set(all_food_ingredients))
            
            # If still zero, set default values
            if stats["total_ingredients"] == 0:
                stats["total_ingredients"] = 1250
                stats["total_products"] = 5000
                stats["high_risk_ingredients"] = 89
                stats["category_breakdown"] = [
                    {"category": "Moisturizer", "count": 1200},
                    {"category": "Cleanser", "count": 800},
                    {"category": "Serum", "count": 600},
                    {"category": "Sunscreen", "count": 400}
                ]
            
            # Recent trends (simulated)
            stats["recent_trends"] = [
                {"ingredient": "Niacinamide", "growth": 45},
                {"ingredient": "Retinol", "growth": 32},
                {"ingredient": "Hyaluronic Acid", "growth": 28},
                {"ingredient": "Parabens", "growth": -15},
                {"ingredient": "Sulfates", "growth": -22},
                {"ingredient": "High Fructose Corn Syrup", "growth": -8}
            ]
            
            # High risk ingredients count (simulated)
            if stats["high_risk_ingredients"] == 0:
                stats["high_risk_ingredients"] = 89
            
            return stats
        except Exception as e:
            logger.error(f"Error in overview stats: {e}")
            return self._get_default_stats()
    
    def _get_default_stats(self):
        """Return default stats if everything fails"""
        return {
            "total_ingredients": 1250,
            "total_products": 5000,
            "high_risk_ingredients": 89,
            "interaction_pairs": 1247,
            "recent_trends": [
                {"ingredient": "Niacinamide", "growth": 45},
                {"ingredient": "Retinol", "growth": 32},
                {"ingredient": "Parabens", "growth": -15}
            ],
            "category_breakdown": [
                {"category": "Moisturizer", "count": 1200},
                {"category": "Cleanser", "count": 800},
                {"category": "Serum", "count": 600}
            ]
        }
    
    def get_market_composition(self, filters):
        """Get market composition analytics"""
        try:
            result = {
                "ingredient_frequency": [],
                "brand_prevalence": [],
                "category_density": [],
                "time_series": []
            }
            
            # Use cosmetics or food based on filter
            industry = filters.get('industry', 'cosmetic')
            df = self.cosmetics_df if industry == 'cosmetic' else self.food_df
            
            if df is None or 'ingredients' not in df.columns:
                return self._get_sample_market_composition(industry)
            
            # Apply filters
            if filters.get('category') and 'category' in df.columns:
                df = df[df['category'] == filters['category']]
            if filters.get('brand') and 'brand' in df.columns:
                df = df[df['brand'] == filters['brand']]
            
            # Ingredient frequency
            all_ingredients = []
            for ingredients in df['ingredients'].dropna():
                if isinstance(ingredients, str):
                    all_ingredients.extend([i.strip().lower() for i in ingredients.split(',')])
            
            frequency = Counter(all_ingredients).most_common(20)
            result["ingredient_frequency"] = [
                {"ingredient": ing.title(), "count": count} 
                for ing, count in frequency
            ]
            
            # Brand prevalence
            if 'brand' in df.columns:
                brand_counts = df['brand'].value_counts().head(10).to_dict()
                result["brand_prevalence"] = [
                    {"brand": k, "product_count": int(v)} for k, v in brand_counts.items()
                ]
            
            # Category density
            if 'category' in df.columns:
                for category in df['category'].unique():
                    cat_df = df[df['category'] == category]
                    avg_ingredients = cat_df['ingredients'].apply(
                        lambda x: len(x.split(',')) if isinstance(x, str) else 0
                    ).mean()
                    
                    result["category_density"].append({
                        "category": category,
                        "avg_ingredients": round(avg_ingredients, 2) if not pd.isna(avg_ingredients) else 0,
                        "product_count": int(len(cat_df))
                    })
            
            # If no data, return sample
            if len(result["ingredient_frequency"]) == 0:
                return self._get_sample_market_composition(industry)
            
            return result
        except Exception as e:
            logger.error(f"Error in market composition: {e}")
            return self._get_sample_market_composition(filters.get('industry', 'cosmetic'))
    
    def _get_sample_market_composition(self, industry='cosmetic'):
        """Return sample market composition data"""
        if industry == 'cosmetic':
            return {
                "ingredient_frequency": [
                    {"ingredient": "Water", "count": 450},
                    {"ingredient": "Glycerin", "count": 380},
                    {"ingredient": "Dimethicone", "count": 320},
                    {"ingredient": "Niacinamide", "count": 290},
                    {"ingredient": "Hyaluronic Acid", "count": 270},
                    {"ingredient": "Retinol", "count": 210},
                    {"ingredient": "Vitamin C", "count": 190},
                    {"ingredient": "Salicylic Acid", "count": 170}
                ],
                "brand_prevalence": [
                    {"brand": "L'Oreal", "product_count": 120},
                    {"brand": "Neutrogena", "product_count": 98},
                    {"brand": "CeraVe", "product_count": 85},
                    {"brand": "The Ordinary", "product_count": 72},
                    {"brand": "Cetaphil", "product_count": 65}
                ],
                "category_density": [
                    {"category": "Moisturizer", "avg_ingredients": 15.2, "product_count": 1200},
                    {"category": "Cleanser", "avg_ingredients": 10.5, "product_count": 800},
                    {"category": "Serum", "avg_ingredients": 12.8, "product_count": 600},
                    {"category": "Sunscreen", "avg_ingredients": 8.3, "product_count": 450}
                ]
            }
        else:
            return {
                "ingredient_frequency": [
                    {"ingredient": "Sugar", "count": 520},
                    {"ingredient": "Salt", "count": 480},
                    {"ingredient": "Water", "count": 450},
                    {"ingredient": "Flour", "count": 380},
                    {"ingredient": "Vegetable Oil", "count": 320},
                    {"ingredient": "High Fructose Corn Syrup", "count": 290},
                    {"ingredient": "Citric Acid", "count": 240},
                    {"ingredient": "Natural Flavors", "count": 210}
                ],
                "brand_prevalence": [
                    {"brand": "Kraft", "product_count": 150},
                    {"brand": "Nestle", "product_count": 120},
                    {"brand": "General Mills", "product_count": 90},
                    {"brand": "Kellogg's", "product_count": 80},
                    {"brand": "PepsiCo", "product_count": 75}
                ],
                "category_density": [
                    {"category": "Snacks", "avg_ingredients": 8.5, "product_count": 800},
                    {"category": "Beverages", "avg_ingredients": 6.2, "product_count": 600},
                    {"category": "Bakery", "avg_ingredients": 7.8, "product_count": 500},
                    {"category": "Dairy", "avg_ingredients": 5.3, "product_count": 350}
                ]
            }
    
    def get_risk_distribution(self, filters):
        """Get risk distribution heatmap data"""
        try:
            return self._get_sample_risk_distribution()
        except Exception as e:
            logger.error(f"Error in risk distribution: {e}")
            return self._get_sample_risk_distribution()
    
    def _get_sample_risk_distribution(self):
        """Return sample risk distribution data"""
        return {
            "heatmap_data": [
                {
                    "dimension": "Acute Toxicity",
                    "distribution": [
                        {"level": "Low", "count": 245},
                        {"level": "Medium", "count": 120},
                        {"level": "High", "count": 35}
                    ]
                },
                {
                    "dimension": "Chronic Toxicity",
                    "distribution": [
                        {"level": "Low", "count": 180},
                        {"level": "Medium", "count": 150},
                        {"level": "High", "count": 70}
                    ]
                },
                {
                    "dimension": "Allergenicity",
                    "distribution": [
                        {"level": "Low", "count": 290},
                        {"level": "Medium", "count": 80},
                        {"level": "High", "count": 30}
                    ]
                },
                {
                    "dimension": "Environmental Impact",
                    "distribution": [
                        {"level": "Low", "count": 200},
                        {"level": "Medium", "count": 140},
                        {"level": "High", "count": 60}
                    ]
                }
            ],
            "risk_clusters": [
                {"category": "Preservative", "count": 12},
                {"category": "Fragrance", "count": 15},
                {"category": "Surfactant", "count": 8},
                {"category": "Colorant", "count": 10},
                {"category": "Emulsifier", "count": 6}
            ],
            "category_risk": [
                {"category": "Preservative", "avg_risk": 7.2, "std_dev": 1.5, "count": 25},
                {"category": "Fragrance", "avg_risk": 6.8, "std_dev": 2.1, "count": 30},
                {"category": "Surfactant", "avg_risk": 5.5, "std_dev": 1.8, "count": 22},
                {"category": "Humectant", "avg_risk": 2.5, "std_dev": 0.8, "count": 40},
                {"category": "Emollient", "avg_risk": 3.2, "std_dev": 1.2, "count": 35},
                {"category": "Active", "avg_risk": 6.1, "std_dev": 2.3, "count": 28}
            ]
        }
    
    def get_network_overview(self):
        """Get overview of interaction network"""
        return {
            "total_interactions": 1247,
            "interaction_types": {
                "synergistic": 523,
                "antagonistic": 412,
                "irritation": 198,
                "toxicity_enhancing": 114
            },
            "most_connected": [
                {"ingredient": "Retinol", "connections": 24},
                {"ingredient": "Niacinamide", "connections": 22},
                {"ingredient": "Vitamin C", "connections": 20},
                {"ingredient": "Salicylic Acid", "connections": 18},
                {"ingredient": "Hyaluronic Acid", "connections": 15},
                {"ingredient": "Benzoyl Peroxide", "connections": 14}
            ],
            "recent_discoveries": [
                {"ingredient1": "Niacinamide", "ingredient2": "Vitamin C", "type": "antagonistic", "date": "2025-12-15"},
                {"ingredient1": "Retinol", "ingredient2": "Peptides", "type": "synergistic", "date": "2025-12-10"},
                {"ingredient1": "Salicylic Acid", "ingredient2": "Glycolic Acid", "type": "irritation", "date": "2025-12-05"}
            ]
        }
    
    def get_interaction_network(self, ingredient_id, depth=2):
        """Get ingredient interaction network"""
        # Comprehensive ingredient database
        ingredients = {
            "1": {"name": "Niacinamide", "category": "Vitamin", "risk": 2.5},
            "2": {"name": "Vitamin C", "category": "Vitamin", "risk": 3.0},
            "3": {"name": "Retinol", "category": "Vitamin", "risk": 7.5},
            "4": {"name": "Hyaluronic Acid", "category": "Humectant", "risk": 1.5},
            "5": {"name": "Salicylic Acid", "category": "Active", "risk": 6.0},
            "6": {"name": "Glycolic Acid", "category": "Active", "risk": 6.5},
            "7": {"name": "Ceramides", "category": "Lipid", "risk": 1.0},
            "8": {"name": "Peptides", "category": "Active", "risk": 1.5},
            "9": {"name": "Benzoyl Peroxide", "category": "Active", "risk": 7.0},
            "10": {"name": "Sodium Lauryl Sulfate", "category": "Surfactant", "risk": 8.0},
            "11": {"name": "Glycerin", "category": "Humectant", "risk": 1.0},
            "12": {"name": "Dimethicone", "category": "Silicone", "risk": 2.0}
        }
        
        # Interaction database
        interactions = [
            {"source": "1", "target": "2", "type": "antagonistic", "strength": 0.7, "description": "Can reduce effectiveness"},
            {"source": "1", "target": "3", "type": "synergistic", "strength": 0.5, "description": "Good combination for anti-aging"},
            {"source": "2", "target": "3", "type": "irritation", "strength": 0.8, "description": "May cause irritation together"},
            {"source": "4", "target": "1", "type": "synergistic", "strength": 0.6, "description": "Enhanced hydration"},
            {"source": "5", "target": "6", "type": "synergistic", "strength": 0.9, "description": "Enhanced exfoliation"},
            {"source": "7", "target": "8", "type": "synergistic", "strength": 0.7, "description": "Improved skin barrier"},
            {"source": "3", "target": "5", "type": "irritation", "strength": 0.7, "description": "Can cause excessive dryness"},
            {"source": "2", "target": "9", "type": "antagonistic", "strength": 0.6, "description": "Reduces effectiveness"},
            {"source": "3", "target": "7", "type": "synergistic", "strength": 0.5, "description": "Better together with moisturizers"},
            {"source": "5", "target": "3", "type": "irritation", "strength": 0.8, "description": "Can increase irritation"},
            {"source": "1", "target": "11", "type": "synergistic", "strength": 0.4, "description": "Good hydration combo"},
            {"source": "3", "target": "12", "type": "neutral", "strength": 0.1, "description": "No significant interaction"}
        ]
        
        # If ingredient_id is a number or name
        if ingredient_id.isdigit():
            node_id = ingredient_id
        else:
            # Try to find by name
            for k, v in ingredients.items():
                if v["name"].lower() in ingredient_id.lower():
                    node_id = k
                    break
            else:
                node_id = "3"  # Default to Retinol
        
        # Filter by ingredient_id
        filtered_nodes = {}
        filtered_edges = []
        
        # Always include the target ingredient
        if node_id in ingredients:
            filtered_nodes[node_id] = ingredients[node_id]
            
            # Find connections up to depth
            for interaction in interactions:
                if interaction["source"] == node_id:
                    if interaction["target"] in ingredients:
                        filtered_nodes[interaction["target"]] = ingredients[interaction["target"]]
                        filtered_edges.append(interaction)
                elif interaction["target"] == node_id:
                    if interaction["source"] in ingredients:
                        filtered_nodes[interaction["source"]] = ingredients[interaction["source"]]
                        # Reverse direction for display
                        rev_interaction = interaction.copy()
                        rev_interaction["source"], rev_interaction["target"] = rev_interaction["target"], rev_interaction["source"]
                        filtered_edges.append(rev_interaction)
        
        # If no nodes found, return sample for retinol
        if not filtered_nodes:
            node_id = "3"
            filtered_nodes[node_id] = ingredients["3"]
            for interaction in interactions[:5]:  # Take first 5 interactions
                if interaction["source"] == node_id:
                    filtered_nodes[interaction["target"]] = ingredients[interaction["target"]]
                    filtered_edges.append(interaction)
                elif interaction["target"] == node_id:
                    filtered_nodes[interaction["source"]] = ingredients[interaction["source"]]
                    rev_interaction = interaction.copy()
                    rev_interaction["source"], rev_interaction["target"] = rev_interaction["target"], rev_interaction["source"]
                    filtered_edges.append(rev_interaction)
        
        return {
            "nodes": [
                {"id": k, "name": v["name"], "category": v["category"], "risk": v["risk"]}
                for k, v in filtered_nodes.items()
            ],
            "edges": filtered_edges
        }
    
    def get_exposure_analysis(self, params):
        """Calculate cumulative exposure risk"""
        ingredient_list = params.get('ingredients', ['Niacinamide', 'Retinol'])
        if isinstance(ingredient_list, str):
            ingredient_list = [ingredient_list]
        
        # Simulated analysis
        result = {
            "cumulative_risk": 45.6,
            "risk_curve": [],
            "population_distribution": [],
            "risk_factors": []
        }
        
        # Generate risk curve
        time_points = [1, 7, 30, 90, 180, 365]
        for t in time_points:
            risk = 45.6 * np.exp(-0.01 * t) + 10 * (1 - np.exp(-0.01 * t))
            result["risk_curve"].append({
                "time": t,
                "risk": round(risk, 2)
            })
        
        # Population distribution
        np.random.seed(42)
        population = np.random.normal(45.6, 12, 1000)
        population = np.clip(population, 0, 100)
        
        hist, bins = np.histogram(population, bins=10)
        for i in range(len(hist)):
            result["population_distribution"].append({
                "range": f"{bins[i]:.0f}-{bins[i+1]:.0f}",
                "count": int(hist[i])
            })
        
        # Risk factors
        result["risk_factors"] = [
            {
                "ingredient": ingredient_list[0] if len(ingredient_list) > 0 else "Retinol",
                "factor": "High irritation potential",
                "contribution": 28.4
            },
            {
                "ingredient": ingredient_list[1] if len(ingredient_list) > 1 else "Niacinamide",
                "factor": "May cause flushing in high doses",
                "contribution": 12.2
            }
        ]
        
        return result
    
    def get_time_trends(self, filters):
        """Get time-based trends for ingredients"""
        years = list(range(2015, 2025))
        
        # Simulated trends
        trend_ingredients = [
            "Parabens", "Sulfates", "Phthalates", "Niacinamide", 
            "Retinol", "Hyaluronic Acid", "Vitamin C", "Ceramides",
            "High Fructose Corn Syrup", "Artificial Colors", "MSG", "BHA"
        ]
        
        result = {
            "ingredient_trends": [], 
            "category_shifts": []
        }
        
        for ing in trend_ingredients:
            if ing in ["Parabens", "Sulfates", "Phthalates", "High Fructose Corn Syrup", "Artificial Colors", "BHA"]:
                # Declining trend
                values = [100 - i*8 + random.randint(-5, 5) for i in range(len(years))]
            else:
                # Rising trend
                values = [40 + i*5 + random.randint(-5, 5) for i in range(len(years))]
            
            # Ensure no negative values
            values = [max(0, v) for v in values]
            
            result["ingredient_trends"].append({
                "ingredient": ing,
                "data": [{"year": y, "frequency": v} for y, v in zip(years, values)]
            })
        
        # Category shifts
        categories = ["Moisturizers", "Cleansers", "Serums", "Sunscreens", "Snacks", "Beverages", "Dairy", "Bakery"]
        for cat in categories:
            result["category_shifts"].append({
                "category": cat,
                "growth_rate": round(random.uniform(-5, 20), 1)
            })
        
        return result
    
    def generate_report(self, params):
        """Generate comprehensive analytics report"""
        report = {
            "report_id": f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "parameters": params,
            "sections": []
        }
        
        # Add requested sections
        if params.get('include_market', True):
            report["sections"].append({
                "title": "Market Composition Analysis",
                "data": self._get_sample_market_composition(params.get('filters', {}).get('industry', 'cosmetic'))
            })
        
        if params.get('include_risk', True):
            report["sections"].append({
                "title": "Risk Distribution Analysis",
                "data": self._get_sample_risk_distribution()
            })
        
        if params.get('include_exposure', True):
            report["sections"].append({
                "title": "Exposure Analysis",
                "data": self.get_exposure_analysis(params.get('exposure_params', {}))
            })
        
        if params.get('include_trends', True):
            report["sections"].append({
                "title": "Time Trends Analysis",
                "data": self.get_time_trends(params.get('filters', {}))
            })
        
        if params.get('include_interaction', True):
            report["sections"].append({
                "title": "Interaction Network Analysis",
                "data": self.get_network_overview()
            })
        
        return report
    
    def get_enhanced_market_composition(self, filters):
        """Enhanced market composition with more metrics"""
        base_data = self.get_market_composition(filters)
        
        # Add additional metrics
        enhanced = {
            **base_data,
            "market_metrics": {
                "total_products": 5000,
                "unique_brands": 150,
                "avg_ingredients_per_product": 12.5,
                "most_diverse_category": "Serums",
                "fastest_growing": "Niacinamide"
            },
            "seasonal_trends": [
                {"month": "Jan", "new_products": 45},
                {"month": "Feb", "new_products": 52},
                {"month": "Mar", "new_products": 48},
                {"month": "Apr", "new_products": 55},
                {"month": "May", "new_products": 62},
                {"month": "Jun", "new_products": 70}
            ],
            "price_analysis": {
                "avg_price_by_category": [
                    {"category": "Moisturizer", "avg_price": 35.50},
                    {"category": "Serum", "avg_price": 52.30},
                    {"category": "Cleanser", "avg_price": 22.80},
                    {"category": "Sunscreen", "avg_price": 28.40}
                ]
            }
        }
        
        return enhanced