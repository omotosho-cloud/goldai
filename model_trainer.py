import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from processor import DataProcessor

class ModelTrainer:
    def __init__(self):
        # Optimized for professional trading
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1,
            bootstrap=True,
            oob_score=True
        )
        self.processor = DataProcessor()
        
    def prepare_data(self):
        """Prepare training data"""
        df = self.processor.process_data()
        feature_cols = self.processor.get_features(df)
        
        X = df[feature_cols]
        y = df['Label']
        
        # Remove samples where we can't calculate future returns
        valid_idx = ~df['Future_Return_4h'].isna()
        X = X[valid_idx]
        y = y[valid_idx]
        
        return X, y, feature_cols
    
    def train_model(self):
        """Train the model using time series split"""
        print("Preparing data...")
        X, y, feature_cols = self.prepare_data()
        
        print(f"Training on {len(X)} samples with {len(feature_cols)} features")
        
        # Professional validation with purged time series split
        tscv = TimeSeriesSplit(n_splits=10, gap=24)  # 24h gap to prevent data leakage
        scores = []
        precision_scores = []
        
        from sklearn.metrics import precision_score
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            # Train model
            temp_model = RandomForestClassifier(
                n_estimators=200, max_depth=15, min_samples_split=10,
                class_weight='balanced', random_state=42, n_jobs=-1
            )
            temp_model.fit(X_train, y_train)
            
            # Evaluate
            score = temp_model.score(X_val, y_val)
            precision = precision_score(y_val, temp_model.predict(X_val), average='weighted', zero_division=0)
            
            scores.append(score)
            precision_scores.append(precision)
            print(f"Fold {fold + 1} - Accuracy: {score:.4f}, Precision: {precision:.4f}")
        
        print(f"Average CV Accuracy: {np.mean(scores):.4f} (+/- {np.std(scores) * 2:.4f})")
        print(f"Average CV Precision: {np.mean(precision_scores):.4f} (+/- {np.std(precision_scores) * 2:.4f})")
        
        # Final training on all data with early stopping simulation
        print("Training final model on all data...")
        self.model.fit(X, y)
        
        # Out-of-bag score for model validation
        if hasattr(self.model, 'oob_score_'):
            print(f"Out-of-bag score: {self.model.oob_score_:.4f}")
        
        # Feature importance
        self.generate_feature_importance(feature_cols)
        
        # Save model
        self.save_model()
        
        return self.model
    
    def generate_feature_importance(self, feature_cols):
        """Generate and display feature importance report"""
        importances = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'Feature': feature_cols,
            'Importance': importances
        }).sort_values('Importance', ascending=False)
        
        print("\n=== FEATURE IMPORTANCE REPORT ===")
        print(feature_importance.to_string(index=False))
        
        # Save to file
        feature_importance.to_csv('feature_importance.csv', index=False)
        
    def save_model(self):
        """Save the trained model"""
        joblib.dump(self.model, 'gold_v1.joblib')
        print("\nModel saved as 'gold_v1.joblib'")
    
    def evaluate_model(self):
        """Evaluate model performance"""
        X, y, _ = self.prepare_data()
        
        # Use last 15% for testing (more training data)
        split_idx = int(len(X) * 0.85)
        X_test = X.iloc[split_idx:]
        y_test = y.iloc[split_idx:]
        
        predictions = self.model.predict(X_test)
        
        print("\n=== MODEL EVALUATION ===")
        print("Classification Report:")
        print(classification_report(y_test, predictions, 
                                  target_names=['Neutral', 'Buy', 'Sell']))
        
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, predictions))

if __name__ == "__main__":
    trainer = ModelTrainer()
    model = trainer.train_model()
    trainer.evaluate_model()