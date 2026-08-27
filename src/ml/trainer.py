"""Cross-validation training with optional feature selection."""
import logging
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.feature_selection import RFECV
from sklearn.linear_model import LassoCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold

from .config import Config
from .models import get_model, BaseModel

logger = logging.getLogger(__name__)


class Trainer:
    """Orchestrates training with CV, feature selection, and checkpointing."""

    def __init__(self, config: Config):
        self.cfg = config
        self.history = []
        self.best_model = None

    # ── feature selection ─────────────────────────────────────

    def feature_selection(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        feature_names,
        method: str,
        n_features: int = 15,
    ):
        if method == "none" or X_train.shape[1] <= n_features:
            return X_train, list(range(X_train.shape[1]))

        if method == "lasso":
            selector = LassoCV(
                cv=5, random_state=self.cfg.trainer.random_state, max_iter=10000
            ).fit(X_train, y_train)
            mask = np.abs(selector.coef_) > 0
            selected_names = feature_names[mask]
            logger.info(f"LASSO selected {len(selected_names)}/{len(feature_names)}: {selected_names.tolist()}")
            return X_train.loc[:, mask], selected_names

        elif method == "rfe":
            from sklearn.ensemble import RandomForestRegressor

            estimator = RandomForestRegressor(
                n_estimators=100, max_depth=3, random_state=self.cfg.trainer.random_state
            )
            selector = RFECV(
                estimator,
                step=1,
                cv=min(5, len(y_train)),
                min_features_to_select=n_features,
                scoring="r2",
            )
            selector.fit(X_train, y_train)
            selected_names = feature_names[selector.support_]
            logger.info(
                f"RFE selected {len(selected_names)}/{len(feature_names)}: {selected_names.tolist()}"
            )
            return X_train.loc[:, selector.support_], selected_names

        return X_train, feature_names

    # ── cross-validation ────────────────────────────────────────

    def cross_validate(
        self,
        X: np.ndarray,
        y: pd.Series,
        model_name: str = "random_forest",
    ) -> Dict[str, List[float]]:
        k = min(self.cfg.trainer.cv_folds, len(y))
        kf = KFold(n_splits=k, shuffle=True, random_state=self.cfg.trainer.random_state)
        scores = {"r2": [], "mse": [], "mae": [], "rmse": []}

        for fold, (train_idx, val_idx) in enumerate(kf.split(X)):
            X_tr, X_val = X[train_idx], X[val_idx]
            y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

            fold_model = get_model(
                model_name,
                self.cfg.model.__dict__.copy(),
                self.cfg.trainer.random_state + fold,
            )
            fold_model.fit(X_tr, y_tr)
            y_pred = fold_model.predict(X_val)

            scores["r2"].append(r2_score(y_val, y_pred))
            scores["mse"].append(mean_squared_error(y_val, y_pred))
            scores["mae"].append(mean_absolute_error(y_val, y_pred))
            scores["rmse"].append(np.sqrt(mean_squared_error(y_val, y_pred)))

        return scores

    # ── training entrypoint ───────────────────────────────────

    def train(
        self, X_train, y_train, X_test, y_test, feature_names, *, model_name: str = "random_forest"
    ) -> Dict:
        # Feature selection
        X_train_sel, selected_names = self.feature_selection(
            X_train,
            y_train,
            pd.Index(feature_names),
            self.cfg.trainer.feature_selection_method,
            self.cfg.trainer.n_features_to_select,
        )
        X_test_sel = X_test[X_train_sel.columns]

        cfg_copy = self.cfg.model.__dict__.copy()
        cfg_copy["feature_names"] = selected_names.tolist() if hasattr(selected_names, "tolist") else selected_names
        model = get_model(model_name, cfg_copy, self.cfg.trainer.random_state)

        # Full train for final model
        model.fit(X_train_sel.values, y_train.values)

        # Predictions
        y_pred_train = model.predict(X_train_sel.values)
        y_pred_test = model.predict(X_test_sel.values)

        results = {
            "model_name": model_name,
            "n_features_selected": len(selected_names) if hasattr(selected_names, "__len__") else len(feature_names),
            "train_r2": r2_score(y_train, y_pred_train),
            "train_mse": mean_squared_error(y_train, y_pred_train),
            "train_mae": mean_absolute_error(y_train, y_pred_train),
            "train_rmse": np.sqrt(mean_squared_error(y_train, y_pred_train)),
            "test_r2": r2_score(y_test, y_pred_test),
            "test_mse": mean_squared_error(y_test, y_pred_test),
            "test_mae": mean_absolute_error(y_test, y_pred_test),
            "test_rmse": np.sqrt(mean_squared_error(y_test, y_pred_test)),
        }

        # CV scores
        scores = self.cross_validate(X_train_sel.values, y_train, model_name=model_name)
        for metric, vals in scores.items():
            results[f"cv_{metric}_mean"] = np.mean(vals)
            results[f"cv_{metric}_std"] = np.std(vals)

        results["feature_importances"] = model.feature_importances()

        # Save feature names alongside model for inference
        model_path = self.cfg.models_dir / f"{model_name}.joblib"
        model.save(str(model_path))
        results["model_path"] = str(model_path)

        # Save selected feature names for inference pipeline
        import json
        feat_path = self.cfg.models_dir / "feature_names.json"
        try:
            with open(feat_path, "w") as f:
                json.dump(selected_names.tolist() if hasattr(selected_names, "tolist") else list(selected_names), f)
            logger.info(f"Saved feature names to {feat_path}")
        except Exception:
            pass

        if results["feature_importances"] is not None:
            importances = results["feature_importances"].abs().sort_values(ascending=False)
            results["top_10_features"] = importances.head(10).to_dict()

        logger.info(
            f"[{model_name}] R²_train={results['train_r2']:.4f} "
            f"R²_test={results['test_r2']:.4f} "
            f"CV_R²={results.get('cv_r2_mean', 0):.4f}±{results.get('cv_r2_std', 0):.4f}"
        )

        return results, model
