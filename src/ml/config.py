"""Centralized configuration for the ML training pipeline."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

# Resolve project root: src/ml/config.py -> src/ -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class DataConfig:
    """Data loading and preprocessing parameters."""
    features_train_path: str = str(PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "features_train.csv")
    labels_train_path: str = str(PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "labels_train.csv")
    features_test_path: str = str(PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "features_test.csv")
    labels_test_path: str = str(PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "labels_test.csv")
    target_column: str = "cuf"
    id_column: str = "district"
    categorical_column: str = "dominant_land_use"
    # Only CEA-actual labels may train a model. Physics-derived CUF is a function of
    # the features themselves (R^2 ~0.99 circularity) and is excluded by default;
    # `--cuf-source all` exists for ablation only.
    cuf_source_filter: str = "cea_plant"  # "cea_plant" | "all"
    # Unit of analysis: "district" = the pre-split 4-file frame in
    # backend/.../outputs/processed/; "plant" = data/plant_labels/plant_dataset.csv.
    # Defaults to the frame so bare DataConfig() keeps working — the CLI passes
    # --unit plant, which is the CEA-label training set.
    unit: str = "district"
    plant_dataset_path: str = str(PROJECT_ROOT / "data" / "plant_labels" / "plant_dataset.csv")


@dataclass
class ModelConfig:
    """Model-specific hyperparameters."""
    # Random Forest
    rf_n_estimators: int = 200
    rf_max_depth: int = 3
    rf_min_samples_split: int = 5
    rf_min_samples_leaf: int = 4
    
    # XGBoost
    xgb_n_estimators: int = 200
    xgb_max_depth: int = 3
    xgb_learning_rate: float = 0.05
    xgb_subsample: float = 0.8
    xgb_colsample_bytree: float = 0.8
    xgb_reg_alpha: float = 1.0
    xgb_reg_lambda: float = 1.0
    
    # Linear models
    ridge_alpha: float = 1e-4   # very low -- target std is ~0.0015 after scaling
    lasso_alpha: float = 1e-6   # minuscule -- near-constant target
    elastic_alpha: float = 1e-4
    elastic_l1_ratio: float = 0.5


@dataclass
class TrainerConfig:
    """Training and cross-validation parameters."""
    cv_folds: int = 5
    random_state: int = 42
    n_jobs: int = -1
    
    # Feature selection (Chakraborty et al. 2023: 40->9 funnel; RFE<=8 at n~160 keeps >=6 samples/feat)
    feature_selection_method: str = "rfe"  # "rfe", "lasso", "none"
    n_features_to_select: int = 8
    
    # Hyperparameter optimization
    enable_hpo: bool = False
    n_hpo_trials: int = 50
    hpo_timeout: int = 3600
    
    # Ensemble
    enable_stacking: bool = True


@dataclass
class Config:
    """Master configuration."""
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    trainer: TrainerConfig = field(default_factory=TrainerConfig)
    
    # Paths
    models_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "models")
    logs_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "ml_logs")
    reports_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "reports")
    
    def __post_init__(self):
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
