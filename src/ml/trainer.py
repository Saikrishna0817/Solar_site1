"""Cross-validation training with optional feature selection."""
import json
import logging
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_selection import RFECV
from sklearn.linear_model import LassoCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

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

    @staticmethod
    def drop_collinear(X: pd.DataFrame, max_r: float = 0.95):
        """Pearson>0.95 drop-one (Chakraborty §3.2.2): greedy, keeps first column.

        ponytail: greedy not optimal-subset; optimal search when n allows exact methods.
        Returns (X with dropped columns removed, sorted list of dropped names).
        """
        corr = X.corr().abs()
        drop = set()
        cols = list(X.columns)
        for i in range(len(cols)):
            if cols[i] in drop:
                continue
            for j in range(i + 1, len(cols)):
                if corr.iloc[i, j] > max_r:
                    drop.add(cols[j])
        dropped = sorted(drop)
        return (X.drop(columns=dropped) if dropped else X), dropped

    def fit_selector(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        feature_names,
        method: str,
        n_features: int = 15,
    ):
        """Fit selection on X/y only — callers pass the slice they want it fitted to.

        Returns (boolean mask over X.columns, selected names).
        """
        n = X.shape[1]
        if method == "none" or n <= n_features:
            return np.ones(n, dtype=bool), pd.Index(feature_names)

        mask = np.ones(n, dtype=bool)
        if method == "lasso":
            selector = LassoCV(
                cv=min(5, len(y)), random_state=self.cfg.trainer.random_state, max_iter=10000
            ).fit(X, y)
            mask = np.abs(selector.coef_) > 0
        elif method == "rfe":
            from sklearn.ensemble import RandomForestRegressor

            estimator = RandomForestRegressor(
                n_estimators=100, max_depth=3, random_state=self.cfg.trainer.random_state
            )
            selector = RFECV(
                estimator,
                step=1,
                cv=min(5, len(y)),
                min_features_to_select=n_features,
                scoring="r2",
            )
            selector.fit(X, y)
            mask = selector.support_

        if mask.sum() == 0:
            logger.warning("Selector picked 0 features on a fold; keeping all %d", n)
            mask = np.ones(n, dtype=bool)
        return mask, pd.Index(feature_names)[mask]

    def feature_selection(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        feature_names,
        method: str,
        n_features: int = 15,
    ):
        """Selection for the final model (fitted on all of X_train). CV uses
        `fit_selector` per fold — see `cross_validate`."""
        mask, selected = self.fit_selector(X_train, y_train, feature_names, method, n_features)
        if method not in ("none",) and X_train.shape[1] > n_features:
            logger.info(
                "%s selected %d/%d: %s",
                method.upper(), len(selected), X_train.shape[1], selected.tolist(),
            )
        return X_train.loc[:, mask], selected

    # ── cross-validation ────────────────────────────────────────

    def cross_validate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        model_name: str = "random_forest",
        groups=None,
    ) -> Dict[str, List[float]]:
        """Leave-one-district-out CV with **selection re-fitted inside every fold**.

        Collinear filtering and feature selection see only the fold's train slice,
        so the CV score cannot be propped up by a selector that peeked at the
        held-out rows. When `groups` is given (district per row) the split is
        spatial: all rows of a district are held out together, so no district both
        trains and tests the same model.

        R² is pooled over the out-of-fold predictions — with leave-one-out each fold
        holds a single row, where per-fold R² is undefined.
        """
        if groups is not None and len(set(np.asarray(groups))) >= 2:
            from sklearn.model_selection import LeaveOneGroupOut

            splits = list(LeaveOneGroupOut().split(X, y, groups))
            logger.info("CV: leave-one-group-out over %d districts", len(set(groups)))
        else:
            k = min(self.cfg.trainer.cv_folds, len(y))
            splits = list(
                KFold(n_splits=k, shuffle=True,
                      random_state=self.cfg.trainer.random_state).split(X)
            )
            logger.info("CV: %d-fold KFold (no groups supplied)", k)

        scores = {"r2": [], "mse": [], "mae": [], "rmse": []}
        method = self.cfg.trainer.feature_selection_method
        n_sel = self.cfg.trainer.n_features_to_select
        fold_features: List[int] = []
        oof = np.full(len(y), np.nan)

        for fold, (train_idx, val_idx) in enumerate(splits):
            X_tr, X_va = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_va = y.iloc[train_idx], y.iloc[val_idx]

            X_tr, _ = self.drop_collinear(X_tr)
            X_va = X_va[X_tr.columns]
            mask, _ = self.fit_selector(X_tr, y_tr, pd.Index(X_tr.columns), method, n_sel)
            fold_features.append(int(mask.sum()))

            fold_model = get_model(
                model_name,
                self.cfg.model.__dict__.copy(),
                self.cfg.trainer.random_state + fold,
            )
            # Scaler fitted on the fold's train rows only — a scaler that saw the
            # held-out rows is the same leak as a selector that saw them.
            scaler = StandardScaler().fit(X_tr.values[:, mask])
            fold_model.fit(scaler.transform(X_tr.values[:, mask]), y_tr.values)
            y_pred = fold_model.predict(scaler.transform(X_va.values[:, mask]))
            oof[val_idx] = y_pred

            scores["mse"].append(mean_squared_error(y_va, y_pred))
            scores["mae"].append(mean_absolute_error(y_va, y_pred))
            scores["rmse"].append(np.sqrt(mean_squared_error(y_va, y_pred)))

        valid = ~np.isnan(oof)
        scores["r2"] = [r2_score(np.asarray(y)[valid], oof[valid])]

        logger.info(
            "CV (selection inside folds): %s features/fold; pooled OOF R²=%.4f, "
            "per-fold MAE=%.4f±%.4f (%s)",
            fold_features, scores["r2"][0],
            float(np.mean(scores["mae"])), float(np.std(scores["mae"])), model_name,
        )
        return scores

    # ── training entrypoint ───────────────────────────────────

    def train(
        self, X_train, y_train, X_test, y_test, feature_names, *,
        model_name: str = "random_forest", groups=None,
    ) -> Dict:
        # Pearson>0.95 drop-one, fitted on the training rows only (val rows must not
        # influence which columns survive).
        X_train, dropped = self.drop_collinear(X_train)
        if dropped:
            logger.info(f"Collinear drop (|r|>0.95): {dropped}")
            X_test = X_test[X_train.columns]
            feature_names = pd.Index([c for c in feature_names if c not in dropped])

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

        # ONE scaler: fit on train rows only, applied before fit and reused as-is by
        # inference. Replaces the old double-scale path (CLI scaled, then trainer
        # refit a second scaler on the selected features).
        scaler = StandardScaler().fit(X_train_sel.values)
        X_tr_s = scaler.transform(X_train_sel.values)
        X_te_s = scaler.transform(X_test_sel.values)

        # Full train for final model
        model.fit(X_tr_s, y_train.values)

        # Predictions
        y_pred_train = model.predict(X_tr_s)
        y_pred_test = model.predict(X_te_s)

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

        # CV scores: selection re-fitted per fold, districts held out together
        scores = self.cross_validate(X_train, y_train, model_name=model_name, groups=groups)
        for metric, vals in scores.items():
            results[f"cv_{metric}_mean"] = np.mean(vals)
            results[f"cv_{metric}_std"] = np.std(vals)

        results["feature_importances"] = model.feature_importances()

        # Save feature names alongside model for inference
        model_path = self.cfg.models_dir / f"{model_name}.joblib"
        model.save(str(model_path))
        results["model_path"] = str(model_path)

        # Persist that SAME scaler so inference applies the exact transform
        # (train/serve parity by construction).
        # ponytail: one StandardScaler, fitted once — not an sklearn Pipeline object,
        # because BaseModel is a plain ABC without get_params/set_params. Upgrade path:
        # make the model classes sklearn BaseEstimators, then fit one
        # Pipeline(StandardScaler, model) and ship it as a single artifact.
        scaler_path = self.cfg.models_dir / "scaler_selected.joblib"
        joblib.dump(scaler, scaler_path)
        results["scaler_path"] = str(scaler_path)

        # Save selected feature names for inference pipeline
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
