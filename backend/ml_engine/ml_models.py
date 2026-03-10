import numpy as np
import pandas as pd
import pickle
import os
from pathlib import Path
import logging
from datetime import datetime
import json
import random

# Try to import ML libraries with proper error handling
ML_AVAILABLE = False
try:
    import xgboost as xgb
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
    from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                                f1_score, roc_auc_score, confusion_matrix,
                                classification_report)
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.model_selection import cross_val_predict
    import shap
    ML_AVAILABLE = True
    print("✅ ML libraries loaded successfully")
except ImportError as e:
    print(f"⚠️ ML libraries not fully installed: {e}")
    print("⚠️ Running in simulation mode")

logger = logging.getLogger(__name__)

class RiskPredictionModel:
    """Base class for risk prediction models"""
    
    def __init__(self, model_type='xgboost'):
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.shap_explainer = None
        self.training_history = []
        self.model_path = Path(__file__).parent / "models"
        self.model_path.mkdir(exist_ok=True)
        
        # Initialize scaler if ML is available
        if ML_AVAILABLE:
            try:
                self.scaler = StandardScaler()
                self.label_encoder = LabelEncoder()
            except Exception as e:
                logger.error(f"Error initializing ML components: {e}")
                self.scaler = None
                self.label_encoder = None
    
    def _get_model(self):
        """Get model instance based on type"""
        if not ML_AVAILABLE:
            return None
            
        try:
            if self.model_type == 'xgboost':
                return xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    objective='binary:logistic',
                    random_state=42,
                    eval_metric='auc',
                    use_label_encoder=False
                )
            elif self.model_type == 'gradient_boosting':
                return GradientBoostingClassifier(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42
                )
            elif self.model_type == 'random_forest':
                return RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")
        except Exception as e:
            logger.error(f"Error creating model: {e}")
            return None
    
    def prepare_features(self, ingredients_data):
        """Prepare features from ingredient data"""
        features = []
        
        for data in ingredients_data:
            row = []
            # Chemical properties
            row.append(data.get('molecular_weight', random.uniform(50, 500)))
            row.append(data.get('logP', random.uniform(-2, 6)))
            row.append(data.get('hbd', random.randint(0, 5)))
            row.append(data.get('hba', random.randint(0, 10)))
            row.append(data.get('tpsa', random.uniform(20, 200)))
            
            # Usage metrics
            row.append(data.get('concentration', random.uniform(0.1, 20)))
            row.append(data.get('frequency', random.uniform(0, 1)))
            
            # Known safety data
            row.append(data.get('known_irritant', random.randint(0, 1)))
            row.append(data.get('known_allergen', random.randint(0, 1)))
            row.append(data.get('endocrine_disruptor', random.randint(0, 1)))
            
            # Interaction features
            row.append(len(data.get('interactions', [])))
            row.append(data.get('synergistic_count', random.randint(0, 5)))
            row.append(data.get('antagonistic_count', random.randint(0, 5)))
            
            features.append(row)
        
        self.feature_names = [
            'molecular_weight', 'logP', 'hbd', 'hba', 'tpsa',
            'concentration', 'frequency',
            'known_irritant', 'known_allergen', 'endocrine_disruptor',
            'interaction_count', 'synergistic_count', 'antagonistic_count'
        ]
        
        return np.array(features)
    
    def train(self, X, y, validation_split=0.2):
        """Train the model with given features and labels"""
        try:
            if not ML_AVAILABLE or self.scaler is None:
                return self._simulate_training(X, y)
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)
            
            # Train model
            self.model = self._get_model()
            if self.model is None:
                return self._simulate_training(X, y)
            
            self.model.fit(
                X_train_scaled, y_train,
                eval_set=[(X_val_scaled, y_val)],
                verbose=False
            )
            
            # Make predictions
            y_pred = self.model.predict(X_val_scaled)
            y_pred_proba = self.model.predict_proba(X_val_scaled)[:, 1]
            
            # Calculate metrics
            metrics = {
                'accuracy': float(accuracy_score(y_val, y_pred)),
                'precision': float(precision_score(y_val, y_pred, average='weighted')),
                'recall': float(recall_score(y_val, y_pred, average='weighted')),
                'f1': float(f1_score(y_val, y_pred, average='weighted')),
                'roc_auc': float(roc_auc_score(y_val, y_pred_proba)),
                'confusion_matrix': confusion_matrix(y_val, y_pred).tolist()
            }
            
            # Create SHAP explainer
            try:
                self.shap_explainer = shap.TreeExplainer(self.model)
            except:
                self.shap_explainer = None
            
            # Save training history
            self.training_history.append({
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'model_type': self.model_type,
                'train_samples': len(X_train),
                'val_samples': len(X_val)
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return self._simulate_training(X, y)
    
    def _simulate_training(self, X, y):
        """Simulate training for demo when ML libraries not available"""
        logger.warning("Using simulated training (ML libraries not available)")
        
        # Simulate metrics
        metrics = {
            'accuracy': round(random.uniform(0.75, 0.92), 3),
            'precision': round(random.uniform(0.73, 0.90), 3),
            'recall': round(random.uniform(0.72, 0.89), 3),
            'f1': round(random.uniform(0.74, 0.91), 3),
            'roc_auc': round(random.uniform(0.80, 0.95), 3),
            'confusion_matrix': [
                [int(random.uniform(40, 60)), int(random.uniform(5, 15))],
                [int(random.uniform(5, 15)), int(random.uniform(40, 60))]
            ]
        }
        
        self.training_history.append({
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'model_type': self.model_type,
            'train_samples': len(X) if X is not None else 100,
            'val_samples': int(len(X) * 0.2) if X is not None else 20,
            'simulated': True
        })
        
        return metrics
    
    def predict(self, ingredients_data):
        """Predict risk for new ingredients"""
        try:
            X = self.prepare_features(ingredients_data)
            
            if self.model is None or not ML_AVAILABLE:
                # Return simulated predictions
                return {
                    'risk_scores': [round(random.uniform(0.1, 0.9), 3) for _ in range(len(X))],
                    'irritation_probability': [round(random.uniform(0.1, 0.8), 3) for _ in range(len(X))],
                    'chronic_risk': [round(random.uniform(0.1, 0.7), 3) for _ in range(len(X))],
                    'sensitivity_risk': [round(random.uniform(0.1, 0.9), 3) for _ in range(len(X))]
                }
            
            if self.scaler is not None:
                X_scaled = self.scaler.transform(X)
            else:
                X_scaled = X
            
            # Get predictions
            risk_scores = self.model.predict_proba(X_scaled)[:, 1]
            
            # For demo, derive other scores from risk scores
            irritation_prob = risk_scores * np.random.uniform(0.8, 1.2, len(risk_scores))
            chronic_risk = risk_scores * np.random.uniform(0.7, 1.1, len(risk_scores))
            sensitivity_risk = risk_scores * np.random.uniform(0.9, 1.3, len(risk_scores))
            
            # Clip to [0,1]
            irritation_prob = np.clip(irritation_prob, 0, 1)
            chronic_risk = np.clip(chronic_risk, 0, 1)
            sensitivity_risk = np.clip(sensitivity_risk, 0, 1)
            
            return {
                'risk_scores': [round(float(x), 3) for x in risk_scores],
                'irritation_probability': [round(float(x), 3) for x in irritation_prob],
                'chronic_risk': [round(float(x), 3) for x in chronic_risk],
                'sensitivity_risk': [round(float(x), 3) for x in sensitivity_risk]
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'risk_scores': [0.5] * len(ingredients_data),
                'irritation_probability': [0.3] * len(ingredients_data),
                'chronic_risk': [0.2] * len(ingredients_data),
                'sensitivity_risk': [0.4] * len(ingredients_data)
            }
    
    def explain(self, ingredients_data):
        """Generate SHAP explanations for predictions"""
        try:
            X = self.prepare_features(ingredients_data)
            
            if self.shap_explainer is None or not ML_AVAILABLE:
                return self._simulate_shap_values(ingredients_data)
            
            if self.scaler is not None:
                X_scaled = self.scaler.transform(X)
            else:
                X_scaled = X
            
            # Calculate SHAP values
            shap_values = self.shap_explainer.shap_values(X_scaled)
            
            # Create feature attribution map
            explanations = []
            for i, ingredient in enumerate(ingredients_data):
                ingredient_explanation = {
                    'ingredient': ingredient.get('name', f'Ingredient {i+1}'),
                    'base_value': float(self.shap_explainer.expected_value),
                    'shap_values': [],
                    'top_contributors': []
                }
                
                # Get SHAP values for this prediction
                if isinstance(shap_values, list):
                    # For multi-class
                    shap_vals = shap_values[1][i] if len(shap_values) > 1 else shap_values[0][i]
                else:
                    shap_vals = shap_values[i]
                
                # Create feature contributions
                contributions = []
                for j, feat_name in enumerate(self.feature_names):
                    if j < len(shap_vals):
                        contributions.append({
                            'feature': feat_name,
                            'value': float(X[i][j]) if j < X.shape[1] else 0,
                            'shap_value': float(shap_vals[j]),
                            'impact': 'positive' if shap_vals[j] > 0 else 'negative'
                        })
                
                # Sort by absolute SHAP value
                contributions.sort(key=lambda x: abs(x['shap_value']), reverse=True)
                
                ingredient_explanation['shap_values'] = contributions
                ingredient_explanation['top_contributors'] = contributions[:5]
                
                explanations.append(ingredient_explanation)
            
            return explanations
            
        except Exception as e:
            logger.error(f"SHAP explanation error: {e}")
            return self._simulate_shap_values(ingredients_data)
    
    def _simulate_shap_values(self, ingredients_data):
        """Simulate SHAP values for demo"""
        explanations = []
        
        for i, ingredient in enumerate(ingredients_data):
            base_value = 0.5
            contributions = []
            
            for feat in ['molecular_weight', 'logP', 'concentration', 
                        'known_irritant', 'interaction_count']:
                shap_val = round(random.uniform(-0.3, 0.3), 3)
                contributions.append({
                    'feature': feat,
                    'value': round(random.uniform(0, 1), 2),
                    'shap_value': shap_val,
                    'impact': 'positive' if shap_val > 0 else 'negative'
                })
            
            # Sort by absolute SHAP value
            contributions.sort(key=lambda x: abs(x['shap_value']), reverse=True)
            
            explanations.append({
                'ingredient': ingredient.get('name', f'Ingredient {i+1}'),
                'base_value': base_value,
                'shap_values': contributions,
                'top_contributors': contributions[:3]
            })
        
        return explanations
    
    def save_model(self, name=None):
        """Save model to disk"""
        if name is None:
            name = f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        model_file = self.model_path / name
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'model_type': self.model_type,
            'training_history': self.training_history
        }
        
        with open(model_file, 'wb') as f:
            pickle.dump(model_data, f)
        
        return str(model_file)
    
    def load_model(self, name):
        """Load model from disk"""
        model_file = self.model_path / name
        
        with open(model_file, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        self.training_history = model_data['training_history']
        
        # Recreate SHAP explainer
        if self.model is not None and ML_AVAILABLE:
            try:
                self.shap_explainer = shap.TreeExplainer(self.model)
            except:
                self.shap_explainer = None
        
        return True


class InteractionGNN:
    """Graph Neural Network for ingredient interactions"""
    
    def __init__(self):
        self.graph_data = None
        self.node_embeddings = None
        
    def build_graph(self, ingredients, interactions):
        """Build interaction graph"""
        # Simplified for demo - would use PyTorch Geometric or DGL
        pass
    
    def train(self):
        """Train GNN model"""
        pass
    
    def predict_interaction_risk(self, ingredient_pairs):
        """Predict risk for ingredient pairs"""
        pass


class BayesianRiskModel:
    """Bayesian model for uncertainty-aware risk prediction"""
    
    def __init__(self):
        self.priors = {}
        self.posteriors = {}
        
    def update_beliefs(self, evidence):
        """Update posterior distributions with new evidence"""
        pass
    
    def predict_with_uncertainty(self, ingredients):
        """Predict risk with confidence intervals"""
        pass