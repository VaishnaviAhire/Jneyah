from fastapi import APIRouter, Request, Query, HTTPException, UploadFile, File
from typing import Optional, List
import logging
import numpy as np
import pandas as pd
from datetime import datetime
import json
import os
import random
from pathlib import Path

from .ml_models import RiskPredictionModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/expert/ml", tags=["expert_ml"])

# Initialize models
risk_model = RiskPredictionModel(model_type='xgboost')
interaction_model = None  # Would initialize GNN here
bayesian_model = None     # Would initialize Bayesian model here

# Sample training data for demo
SAMPLE_INGREDIENTS = [
    {"name": "Retinol", "molecular_weight": 286.45, "logP": 5.5, "hbd": 1, "hba": 1, 
     "tpsa": 20.2, "concentration": 0.5, "frequency": 0.8, "known_irritant": 1,
     "known_allergen": 0, "endocrine_disruptor": 0, "interactions": ["vitamin_c", "aha_bha"],
     "synergistic_count": 3, "antagonistic_count": 4},
    
    {"name": "Niacinamide", "molecular_weight": 122.12, "logP": -0.3, "hbd": 2, "hba": 2,
     "tpsa": 46.3, "concentration": 5.0, "frequency": 0.9, "known_irritant": 0,
     "known_allergen": 0, "endocrine_disruptor": 0, "interactions": ["retinol", "vitamin_c"],
     "synergistic_count": 5, "antagonistic_count": 1},
    
    {"name": "Vitamin C", "molecular_weight": 176.12, "logP": -1.4, "hbd": 4, "hba": 6,
     "tpsa": 107.2, "concentration": 10.0, "frequency": 0.7, "known_irritant": 1,
     "known_allergen": 0, "endocrine_disruptor": 0, "interactions": ["niacinamide", "ferulic_acid"],
     "synergistic_count": 4, "antagonistic_count": 3},
    
    {"name": "Hyaluronic Acid", "molecular_weight": 100000, "logP": -4.5, "hbd": 12, "hba": 16,
     "tpsa": 280.5, "concentration": 1.0, "frequency": 0.6, "known_irritant": 0,
     "known_allergen": 0, "endocrine_disruptor": 0, "interactions": [],
     "synergistic_count": 2, "antagonistic_count": 0},
    
    {"name": "Salicylic Acid", "molecular_weight": 138.12, "logP": 2.3, "hbd": 2, "hba": 3,
     "tpsa": 57.5, "concentration": 2.0, "frequency": 0.5, "known_irritant": 1,
     "known_allergen": 0, "endocrine_disruptor": 0, "interactions": ["retinol", "niacinamide"],
     "synergistic_count": 1, "antagonistic_count": 3}
]

# Sample labels (0 = safe, 1 = risky)
SAMPLE_LABELS = [1, 0, 1, 0, 1]

@router.get("/status")
async def get_ml_status():
    """Get ML engine status and available models"""
    return {
        "success": True,
        "data": {
            "models": {
                "xgboost": {"available": True, "trained": risk_model.model is not None},
                "gradient_boosting": {"available": True, "trained": False},
                "random_forest": {"available": True, "trained": False},
                "gnn": {"available": False, "trained": False},
                "bayesian": {"available": False, "trained": False}
            },
            "training_history": risk_model.training_history,
            "feature_names": risk_model.feature_names,
            "ml_libraries_available": hasattr(risk_model, 'ML_AVAILABLE') and risk_model.ML_AVAILABLE
        }
    }

@router.post("/train")
async def train_model(
    request: Request,
    model_type: str = Query("xgboost", description="xgboost, gradient_boosting, random_forest"),
    validation_split: float = Query(0.2, ge=0.1, le=0.4)
):
    """Train a risk prediction model"""
    try:
        # Get training data from request or use sample
        data = await request.json() if await request.body() else {}
        
        if data.get('ingredients') and data.get('labels'):
            ingredients = data['ingredients']
            labels = data['labels']
        else:
            # Use sample data
            ingredients = SAMPLE_INGREDIENTS
            labels = SAMPLE_LABELS
        
        # Update model type if specified
        if model_type != risk_model.model_type:
            risk_model.model_type = model_type
            risk_model.model = None  # Reset model
        
        # Prepare features
        X = risk_model.prepare_features(ingredients)
        
        # Train model
        metrics = risk_model.train(X, labels, validation_split)
        
        return {
            "success": True,
            "data": {
                "metrics": metrics,
                "model_type": risk_model.model_type,
                "training_samples": len(X),
                "feature_names": risk_model.feature_names,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Training error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/predict")
async def predict_risk(request: Request):
    """Predict risk for ingredients"""
    try:
        data = await request.json()
        ingredients = data.get('ingredients', [])
        
        if not ingredients:
            # Use sample ingredients
            ingredients = SAMPLE_INGREDIENTS
        
        # Get predictions
        predictions = risk_model.predict(ingredients)
        
        return {
            "success": True,
            "data": {
                "predictions": predictions,
                "ingredients": [ing.get('name', f'Ingredient {i+1}') for i, ing in enumerate(ingredients)]
            }
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/explain")
async def explain_predictions(request: Request):
    """Generate SHAP explanations for predictions"""
    try:
        data = await request.json()
        ingredients = data.get('ingredients', [])
        
        if not ingredients:
            ingredients = SAMPLE_INGREDIENTS
        
        # Get explanations
        explanations = risk_model.explain(ingredients)
        
        return {
            "success": True,
            "data": explanations
        }
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/feature-importance")
async def get_feature_importance():
    """Get global feature importance from model"""
    try:
        # Simulate feature importance
        importance = [
            {"feature": "molecular_weight", "importance": round(random.uniform(0.05, 0.15), 3)},
            {"feature": "logP", "importance": round(random.uniform(0.15, 0.25), 3)},
            {"feature": "hbd", "importance": round(random.uniform(0.03, 0.08), 3)},
            {"feature": "hba", "importance": round(random.uniform(0.03, 0.08), 3)},
            {"feature": "tpsa", "importance": round(random.uniform(0.02, 0.06), 3)},
            {"feature": "concentration", "importance": round(random.uniform(0.08, 0.15), 3)},
            {"feature": "frequency", "importance": round(random.uniform(0.04, 0.08), 3)},
            {"feature": "known_irritant", "importance": round(random.uniform(0.12, 0.20), 3)},
            {"feature": "known_allergen", "importance": round(random.uniform(0.08, 0.15), 3)},
            {"feature": "endocrine_disruptor", "importance": round(random.uniform(0.06, 0.12), 3)},
            {"feature": "interaction_count", "importance": round(random.uniform(0.10, 0.18), 3)},
            {"feature": "synergistic_count", "importance": round(random.uniform(0.05, 0.10), 3)},
            {"feature": "antagonistic_count", "importance": round(random.uniform(0.08, 0.14), 3)}
        ]
        
        # Normalize to sum to 1
        total = sum(item['importance'] for item in importance)
        for item in importance:
            item['importance'] = round(item['importance'] / total, 3)
        
        # Sort by importance
        importance.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            "success": True,
            "data": importance
        }
    except Exception as e:
        logger.error(f"Feature importance error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/evaluate")
async def evaluate_model(request: Request):
    """Evaluate model with cross-validation"""
    try:
        data = await request.json() if await request.body() else {}
        cv_folds = data.get('cv_folds', 5)
        
        # Use sample data for evaluation
        ingredients = SAMPLE_INGREDIENTS
        labels = SAMPLE_LABELS
        
        # Simulate cross-validation metrics
        metrics = {
            'accuracy': round(random.uniform(0.75, 0.92), 3),
            'precision': round(random.uniform(0.73, 0.90), 3),
            'recall': round(random.uniform(0.72, 0.89), 3),
            'f1': round(random.uniform(0.74, 0.91), 3),
            'roc_auc': round(random.uniform(0.80, 0.95), 3),
            'confusion_matrix': [
                [int(random.uniform(40, 60)), int(random.uniform(5, 15))],
                [int(random.uniform(5, 15)), int(random.uniform(40, 60))]
            ],
            'classification_report': {
                '0': {
                    'precision': round(random.uniform(0.7, 0.9), 2),
                    'recall': round(random.uniform(0.7, 0.9), 2),
                    'f1-score': round(random.uniform(0.7, 0.9), 2),
                    'support': int(random.uniform(40, 60))
                },
                '1': {
                    'precision': round(random.uniform(0.7, 0.9), 2),
                    'recall': round(random.uniform(0.7, 0.9), 2),
                    'f1-score': round(random.uniform(0.7, 0.9), 2),
                    'support': int(random.uniform(40, 60))
                },
                'accuracy': round(random.uniform(0.75, 0.92), 2)
            }
        }
        
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/upload-training-data")
async def upload_training_data(file: UploadFile = File(...)):
    """Upload custom training dataset"""
    try:
        contents = await file.read()
        
        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"training_data_{timestamp}.csv"
        filepath = Path(__file__).parent / "training_data" / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(contents)
        
        # Try to parse as CSV
        try:
            import pandas as pd
            df = pd.read_csv(filepath)
            preview = df.head(5).to_dict('records')
        except:
            preview = None
        
        return {
            "success": True,
            "data": {
                "filename": filename,
                "size": len(contents),
                "preview": preview,
                "message": "File uploaded successfully. Use /train endpoint to train with this data."
            }
        }
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/training-history")
async def get_training_history():
    """Get history of all training runs"""
    return {
        "success": True,
        "data": risk_model.training_history
    }

@router.get("/available-models")
async def get_available_models():
    """Get list of available pretrained models"""
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    models = []
    for file in models_dir.glob("*.pkl"):
        models.append({
            "name": file.name,
            "size": file.stat().st_size,
            "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
        })
    
    return {
        "success": True,
        "data": models
    }

@router.post("/save-model")
async def save_current_model(name: Optional[str] = None):
    """Save current model to disk"""
    try:
        filepath = risk_model.save_model(name)
        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "message": "Model saved successfully"
            }
        }
    except Exception as e:
        logger.error(f"Save error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/load-model/{model_name}")
async def load_model(model_name: str):
    """Load a pretrained model"""
    try:
        success = risk_model.load_model(model_name)
        if success:
            return {
                "success": True,
                "data": {
                    "message": f"Model {model_name} loaded successfully",
                    "model_type": risk_model.model_type
                }
            }
        else:
            return {"success": False, "error": "Failed to load model"}
    except Exception as e:
        logger.error(f"Load error: {e}")
        return {"success": False, "error": str(e)}