"""Main ML pipeline orchestrator."""
import logging
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ml.config import Config
from src.ml.data_loader import SolarDataLoader
from src.ml.trainer import Trainer
from src.ml.evaluation import generate_report, plot_feature_importance, plot_model_comparison


logger = logging.getLogger(__name__)


def setup_logging(log_dir: Path, level=logging.INFO):
    """Configure logging."""
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
    file_handler = logging.FileHandler(log_dir / "ml_training.log")
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
    
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler, file_handler]
    return root


class MLPipeline:
    """End-to-end ML training pipeline."""

    def __init__(self, config: Config = None):
        self.cfg = config or Config()
        self.data_loader = SolarDataLoader(self.cfg.data)
        self.trainer = Trainer(self.cfg)
        setup_logging(self.cfg.logs_dir)
        self.results: List[Dict] = []

    def run(self, model_names: List[str] = None) -> List[Dict]:
        """Run the full training pipeline for specified models."""
        model_names = model_names or ["random_forest", "xgboost", "ridge", "lasso", "elastic_net"]
        
        # Load data
        X_train, y_train, X_test, y_test, feature_names = self.data_loader.load()
        
        # Scale features
        X_train_scaled, X_test_scaled = self.data_loader.fit_transform(X_train, X_test)
        # Persist the ONE scaler inference must reuse (kills train/serve skew).
        self.data_loader.save_preprocessor(str(self.cfg.models_dir / "preprocessor.joblib"))
        
        # Convert to DataFrames for feature selection compatibility
        X_train_df = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
        X_test_df = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
        
        self.results = []
        
        for model_name in model_names:
            logger.info(f"\n{'='*60}")
            logger.info(f"Training: {model_name.upper()}")
            logger.info(f"{'='*60}")
            
            try:
                results, model = self.trainer.train(
                    X_train_df, y_train, X_test_df, y_test, feature_names,
                    model_name=model_name
                )
                self.results.append(results)
                
                # Generate plots for each model
                if results.get("feature_importances") is not None:
                    plot_feature_importance(
                        results["feature_importances"],
                        save_path=self.cfg.reports_dir / "figures" / f"{model_name}_importance.png"
                    )
                
            except Exception as e:
                logger.error(f"Failed to train {model_name}: {e}", exc_info=True)
                continue
        
        # Comparison plot
        if len(self.results) > 1:
            comparison_df = pd.DataFrame(self.results)
            plot_model_comparison(
                comparison_df,
                save_path=self.cfg.reports_dir / "figures" / "model_comparison.png"
            )
        
        # Generate report
        generate_report(self.results, save_path=self.cfg.reports_dir / "ml_report.md")
        
        return self.results
