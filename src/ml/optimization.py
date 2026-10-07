"""Hyperparameter optimization with Optuna."""
import logging
from typing import Dict

import numpy as np
import optuna
from sklearn.metrics import r2_score

from .config import Config
from .models import get_model

logger = logging.getLogger(__name__)
optuna.logging.set_verbosity(optuna.logging.WARNING)


def _suggest(trial, name: str, config):
    """Suggest model-specific params from a trial."""
    if name == "random_forest":
        return {
            "rf_n_estimators": trial.suggest_int("rf_n_estimators", 50, 500, step=50),
            "rf_max_depth": trial.suggest_int("rf_max_depth", 2, 10),
            "rf_min_samples_split": trial.suggest_int("rf_min_samples_split", 2, 10),
            "rf_min_samples_leaf": trial.suggest_int("rf_min_samples_leaf", 1, 10),
        }
    elif name == "ridge":
        # Shared space 1e-6..100; optimum lives near 1e-4.
        return {
            "ridge_alpha": trial.suggest_float("ridge_alpha", 1e-6, 100.0, log=True),
        }
    elif name == "lasso":
        return {
            "lasso_alpha": trial.suggest_float("lasso_alpha", 0.0001, 10.0, log=True),
        }
    elif name == "elastic_net":
        return {
            "elastic_alpha": trial.suggest_float("elastic_alpha", 0.0001, 10.0, log=True),
            "elastic_l1_ratio": trial.suggest_float("elastic_l1_ratio", 0.0, 1.0),
        }
    return {}


def _cv_score(
    model_name: str,
    hparams: Dict,
    X: np.ndarray,
    y: np.ndarray,
    base_config: Config,
    n_folds: int = 5,
) -> float:
    """Compute cross-validated R² on training data only (NO test set leakage)."""
    from sklearn.model_selection import KFold

    kf = KFold(n_splits=min(n_folds, len(y)), shuffle=True,
               random_state=base_config.trainer.random_state)
    cfg_dict = base_config.model.__dict__.copy()
    cfg_dict.update(hparams)
    cfg_dict["feature_names"] = list(range(X.shape[1]))

    scores = []
    for train_idx, val_idx in kf.split(X):
        model = get_model(model_name, cfg_dict, base_config.trainer.random_state)
        model.fit(X[train_idx], y[train_idx])
        y_pred = model.predict(X[val_idx])
        scores.append(r2_score(y[val_idx], y_pred))
    return float(np.mean(scores))


def objective(
    trial,
    model_name: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    base_config: Config,
) -> float:
    """Optuna objective: maximize CV R² on training data (NO test set leakage)."""
    hparams = _suggest(trial, model_name, base_config)
    cv_r2 = _cv_score(model_name, hparams, X_train, y_train, base_config)
    return cv_r2


def optimize_hyperparameters(
    model_name: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray = None,
    y_test: np.ndarray = None,
    config: Config = None,
    n_trials: int = 30,
) -> Dict:
    """Run Optuna HPO using CV on training data ONLY (no test set leakage).

    X_test and y_test are accepted for backward compatibility but NEVER used
    during hyperparameter optimization. Final evaluation is always on test set
    AFTER the best hyperparameters are found.
    """
    import numpy as np

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=config.trainer.random_state),
    )

    def _objective(trial):
        return objective(trial, model_name, X_train, y_train, config)

    study.optimize(_objective, n_trials=n_trials, show_progress_bar=False)

    best_params = study.best_params
    logger.info(f"[{model_name}] Best CV R²={study.best_value:.4f}: {best_params}")

    cfg_dict = config.model.__dict__.copy()
    cfg_dict.update(best_params)
    cfg_dict["feature_names"] = list(range(X_train.shape[1]))
    model = get_model(model_name, cfg_dict, config.trainer.random_state)
    model.fit(X_train, y_train)

    result = {
        "best_params": best_params,
        "best_cv_score": study.best_value,
        "model": model,
        "n_trials": n_trials,
    }
    if X_test is not None and y_test is not None:
        y_pred = model.predict(X_test)
        result["test_r2"] = r2_score(y_test, y_pred)
        logger.info(f"[{model_name}] Test R² (post-HPO, no leakage): {result['test_r2']:.4f}")

    return result
