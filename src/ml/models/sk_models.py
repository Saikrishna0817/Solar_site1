"""Base model interface and factory."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd


class BaseModel(ABC):
    """Abstract base for all ML models."""

    def __init__(self, name: str, config: Dict[str, Any], random_state: int = 42):
        self.name = name
        self.config = config
        self.random_state = random_state
        self.model = None

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        ...

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        ...

    @abstractmethod
    def feature_importances(self) -> Optional[pd.Series]:
        ...

    def save(self, path: str) -> None:
        import joblib
        joblib.dump(self.model, path)

    def load(self, path: str) -> None:
        import joblib
        self.model = joblib.load(path)


class RandomForestModel(BaseModel):
    """Random Forest regressor with aggressive regularization for small data."""

    def __init__(self, config, random_state=42):
        super().__init__("RandomForest", config, random_state)
        from sklearn.ensemble import RandomForestRegressor
        self.model = RandomForestRegressor(
            n_estimators=config["rf_n_estimators"],
            max_depth=config["rf_max_depth"],
            min_samples_split=config["rf_min_samples_split"],
            min_samples_leaf=config["rf_min_samples_leaf"],
            random_state=random_state,
            n_jobs=config.get("n_jobs", -1),
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def feature_importances(self) -> pd.Series:
        return pd.Series(self.model.feature_importances_, index=self.config["feature_names"])


class XGBoostModel(BaseModel):
    """XGBoost regressor with strong regularization."""

    def __init__(self, config, random_state=42):
        super().__init__("XGBoost", config, random_state)
        try:
            from xgboost import XGBRegressor
            self.model = XGBRegressor(
                n_estimators=config["xgb_n_estimators"],
                max_depth=config["xgb_max_depth"],
                learning_rate=config["xgb_learning_rate"],
                subsample=config["xgb_subsample"],
                colsample_bytree=config["xgb_colsample_bytree"],
                reg_alpha=config["xgb_reg_alpha"],
                reg_lambda=config["xgb_reg_lambda"],
                random_state=random_state,
                n_jobs=config.get("n_jobs", -1),
            )
        except ImportError:
            raise ImportError("xgboost is not installed. Run: pip install xgboost")

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def feature_importances(self) -> pd.Series:
        return pd.Series(self.model.feature_importances_, index=self.config["feature_names"])


class RidgeModel(BaseModel):
    """Ridge regression with standardization."""

    def __init__(self, config, random_state=42):
        super().__init__("Ridge", config, random_state)
        from sklearn.linear_model import Ridge
        self.model = Ridge(alpha=config["ridge_alpha"], random_state=random_state)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def feature_importances(self) -> Optional[pd.Series]:
        if hasattr(self.model, "coef_"):
            return pd.Series(self.model.coef_, index=self.config["feature_names"])
        return None


class LassoModel(BaseModel):
    """Lasso regression for feature selection."""

    def __init__(self, config, random_state=42):
        super().__init__("Lasso", config, random_state)
        from sklearn.linear_model import Lasso
        self.model = Lasso(alpha=config["lasso_alpha"], random_state=random_state, max_iter=10000)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def feature_importances(self) -> Optional[pd.Series]:
        if hasattr(self.model, "coef_"):
            return pd.Series(self.model.coef_, index=self.config["feature_names"])
        return None


class ElasticNetModel(BaseModel):
    """Elastic Net regression."""

    def __init__(self, config, random_state=42):
        super().__init__("ElasticNet", config, random_state)
        from sklearn.linear_model import ElasticNet
        self.model = ElasticNet(
            alpha=config["elastic_alpha"],
            l1_ratio=config["elastic_l1_ratio"],
            random_state=random_state,
            max_iter=10000,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def feature_importances(self) -> Optional[pd.Series]:
        if hasattr(self.model, "coef_"):
            return pd.Series(self.model.coef_, index=self.config["feature_names"])
        return None


def get_model(name: str, config: Dict[str, Any], random_state: int = 42) -> BaseModel:
    """Factory to create model instances by name."""
    models = {
        "random_forest": RandomForestModel,
        "xgboost": XGBoostModel,
        "ridge": RidgeModel,
        "lasso": LassoModel,
        "elastic_net": ElasticNetModel,
    }
    if name not in models:
        raise ValueError(f"Unknown model: {name}. Available: {list(models.keys())}")
    return models[name](config, random_state=random_state)
