"""Preprocessing module: train/test split, imputation, winsorization, transform, encode, scale."""

from typing import Any, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

from solarpipeline.utils import PROCESSED_DIR, get_logger, CONFIG

TARGET_COL = "cuf"
logger = get_logger(__name__)

# ── Features to drop (kept composite infra index instead)
_INDIVIDUAL_DIST_COLS = [
    "dist_nearest_road_km",
    "dist_nearest_transmission_line_km",
    "dist_nearest_substation_km",
]


def _detect_skewed_features(df: pd.DataFrame, numeric_cols: list, threshold: float = None) -> list:
    """Return columns with abs(skewness) above threshold, computed on training data."""
    if threshold is None:
        threshold = CONFIG.skew_threshold
    skewed = []
    for col in numeric_cols:
        if df[col].nunique() <= 1:
            continue
        sk = df[col].skew()
        if abs(sk) > threshold:
            skewed.append(col)
    if skewed:
        logger.info("  Skewed features to log-transform: %s", skewed)
    return skewed


def _winsorize(X_train: pd.DataFrame, X_test: pd.DataFrame,
               numeric_cols: list, lower_q: float = None, upper_q: float = None) -> None:
    """In-place winsorization using train-only quantiles."""
    if lower_q is None:
        lower_q = CONFIG.winsor_lower_q
    if upper_q is None:
        upper_q = CONFIG.winsor_upper_q
    capped = []
    for col in numeric_cols:
        q_low = X_train[col].quantile(lower_q)
        q_high = X_train[col].quantile(upper_q)
        # Only cap if the quantiles are meaningfully different
        if q_low < q_high:
            X_train[col] = X_train[col].clip(lower=q_low, upper=q_high)
            X_test[col] = X_test[col].clip(lower=q_low, upper=q_high)
            capped.append(col)
    if capped:
        logger.info("  Winsorized (%.0f%%/%.0f%%): %s", lower_q * 100, upper_q * 100, capped)


def _impute(X_train: pd.DataFrame, X_test: pd.DataFrame,
            numeric_cols: list) -> None:
    """Median imputation using train-only statistics."""
    for col in numeric_cols:
        if X_train[col].isnull().any() or (col in X_test.columns and X_test[col].isnull().any()):
            median_val = X_train[col].median()
            X_train[col] = X_train[col].fillna(median_val)
            X_test[col] = X_test[col].fillna(median_val)
            logger.info("  Imputed %s <- %.4f (train median)", col, median_val)


def _encode(X_train: pd.DataFrame, X_test: pd.DataFrame,
            cat_cols: list) -> None:
    """Label-encode using train-only categories.

    Unseen test categories are mapped to the global UNKNOWN token (-1)."""
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        # Separate missing placeholder so it is not confused with a real category.
        X_train[col] = X_train[col].fillna("<NA>").astype(str)
        X_test[col] = X_test[col].fillna("<NA>").astype(str)

        # Ensure "Unknown" is in the vocabulary so we always have a fallback.
        train_vals = pd.concat([X_train[col], pd.Series(["Unknown"])], ignore_index=True)
        le.fit(train_vals)
        encoders[col] = le

        # Encode train ("Unknown" will be present, so transform succeeds).
        X_train[col] = le.transform(X_train[col].replace("<NA>", "Unknown"))

        # Handle unseen in test: replace with "Unknown" then encode.
        X_test[col] = X_test[col].replace("<NA>", "Unknown")
        unseen = ~X_test[col].isin([c for c in le.classes_ if c != "Unknown"])
        if unseen.any():
            X_test.loc[unseen, col] = "Unknown"
        X_test[col] = le.transform(X_test[col])
    if encoders:
        try:
            enc_df = pd.DataFrame({k: pd.Series(v.classes_) for k, v in encoders.items()})
            enc_df.to_csv(str(PROCESSED_DIR / "label_encoders.csv"), index=False)
        except Exception as exc:
            logger.warning("Could not save label_encoders: %s", exc)


def _scale(X_train: pd.DataFrame, X_test: pd.DataFrame,
           numeric_cols: list) -> bool:
    """Fit StandardScaler on X_train, transform both. Returns False on failure."""
    try:
        scaler = StandardScaler()
        X_train[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
        X_test[numeric_cols] = scaler.transform(X_test[numeric_cols])
        params = pd.DataFrame({
            "feature": numeric_cols,
            "mean": scaler.mean_,
            "scale": scaler.scale_,
        })
        params.to_csv(str(PROCESSED_DIR / "scaling_params.csv"), index=False)
        return True
    except Exception as exc:
        logger.error("Scaling failed: %s", exc)
        return False


def preprocess(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Pre-process for ML: split, impute, winsorize, transform, encode, scale.

    Drops non-feature columns (``district``, ``state``, ``source``, NASA AOD,
    individual distance columns), splits 80/20 stratified by state, median
    imputed with train-only statistics, winsorized, log-transformed for
    skewed features, label-encoded, then StandardScaled. All statistics
    (medians, quantiles, encoding maps, scaler) are derived exclusively
    from the training set to prevent data leakage.

    Parameters
    ----------
    df : pd.DataFrame
        Engineered dataset (output of ``engineer_features``).

    Returns
    -------
    (X_train_full, labels_train) or (None, None) on failure.
    """
    logger.info("Phase 3: Preprocessing")

    if TARGET_COL not in df.columns:
        logger.error("Target '%s' missing — cannot preprocess.", TARGET_COL)
        return None, None

    df = df.copy()

    # Drop non-feature columns
    drop = ["district", "state", "source", "state_x", "state_y", "state_name"]
    drop = [c for c in drop if c in df.columns]
    # Also drop near-zero-variance NASA AOD
    if "aerosol_optical_depth" in df.columns:
        drop.append("aerosol_optical_depth")
    features = df.drop(columns=drop + [TARGET_COL])

    # Drop individual distance features (keep composite infra index only)
    dist_to_drop = [c for c in _INDIVIDUAL_DIST_COLS if c in features.columns]
    if dist_to_drop:
        features = features.drop(columns=dist_to_drop)

    # Drop features with perfect multicollinearity (Audit Fix: avoid VIF = inf)
    collinear_drops = []
    if "peak_sun_hours" in features.columns:
        collinear_drops.append("peak_sun_hours")  # r ≈ 1.0 with avg_ghi_kwh_m2_day
    if "wasteland_builtup_pct" in features.columns:
        collinear_drops.append("wasteland_builtup_pct")  # r ≈ 0.997 with builtup_pct
    if "solar_variability" in features.columns and "solar_efficiency_index" in features.columns:
        collinear_drops.append("solar_efficiency_index")  # r ≈ 0.997 with solar_variability
    if collinear_drops:
        features = features.drop(columns=collinear_drops)
        logger.info("  Dropped collinear features: %s", collinear_drops)

    # Determine numeric / categorical (before split)
    numeric_cols = features.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = features.select_dtypes(exclude=[np.number]).columns.tolist()
    logger.info("Numeric features: %d  |  Categorical: %d", len(numeric_cols), len(cat_cols))

    # Train / test split (FIRST — before any imputation/encoding)
    districts = df["district"].values
    labels = df[["state", TARGET_COL]].copy() if "state" in df.columns else df[[TARGET_COL]].copy()
    stratify_col = df["state"].values if "state" in df.columns else None

    try:
        split = train_test_split(
            features, labels, districts, stratify_col,
            test_size=CONFIG.test_size, random_state=CONFIG.random_state,
            stratify=stratify_col,
        )
        X_train, X_test, y_train, y_test, dist_train, dist_test, _, _ = split
        logger.info("Train: %d rows  |  Test: %d rows", len(X_train), len(X_test))
    except Exception as exc:
        logger.warning("Stratified split failed, falling back to random: %s", exc)
        X_train, X_test, y_train, y_test, dist_train, dist_test = train_test_split(
            features, labels, districts,
            test_size=CONFIG.test_size, random_state=CONFIG.random_state,
        )
        logger.info("Train: %d rows  |  Test: %d rows (random split)", len(X_train), len(X_test))

    # ── 1. Impute (train-only medians)
    _impute(X_train, X_test, numeric_cols)

    # ── 2. Winsorize (train-only quantiles)
    # Caps extreme outliers BEFORE log-transform. This preserves the
    # interpretability of winsorization boundaries while allowing the
    # subsequent log-transform to further compress the right tail.
    logger.info("  Applying winsorization...")
    _winsorize(X_train, X_test, numeric_cols,
               lower_q=CONFIG.winsor_lower_q, upper_q=CONFIG.winsor_upper_q)

    # ── 3. Log-transform skewed features (train-detected)
    # Applied AFTER winsorization so that extreme values are first capped,
    # then compressed. This is standard for tree-based models; for linear
    # models you may prefer log-then-winsorize and should re-evaluate.
    skewed = _detect_skewed_features(X_train, numeric_cols)
    if skewed:
        logger.info("  Applying log1p transform to skewed features...")
        for col in skewed:
            X_train[col] = np.log1p(X_train[col].clip(lower=0))
            X_test[col] = np.log1p(X_test[col].clip(lower=0))

    # ── 4. Encode categoricals (train-only categories)
    if cat_cols:
        _encode(X_train, X_test, cat_cols)

    # ── 5. Scale (train-only fit)
    if numeric_cols:
        if not _scale(X_train, X_test, numeric_cols):
            return None, None

    # Save
    try:
        X_train.insert(0, "district", dist_train)
        y_train.insert(0, "district", dist_train)
        X_train.to_csv(str(PROCESSED_DIR / "features_train.csv"), index=False)
        y_train.to_csv(str(PROCESSED_DIR / "labels_train.csv"), index=False)
        logger.info("Saved: features_train.csv (%d x %d)", len(X_train), len(X_train.columns))
        logger.info("Saved: labels_train.csv (%d rows)", len(y_train))

        X_test.insert(0, "district", dist_test)
        y_test.insert(0, "district", dist_test)
        X_test.to_csv(str(PROCESSED_DIR / "features_test.csv"), index=False)
        y_test.to_csv(str(PROCESSED_DIR / "labels_test.csv"), index=False)
        logger.info("Saved: features_test.csv (%d x %d)", len(X_test), len(X_test.columns))
        logger.info("Saved: labels_test.csv (%d rows)", len(y_test))

        # Convenience single-file copies
        X_all = df[["district"] + [c for c in features.columns if c != "district"]]
        X_all.to_csv(str(PROCESSED_DIR / "features.csv"), index=False)
        df[["district", TARGET_COL]].to_csv(str(PROCESSED_DIR / "labels.csv"), index=False)
    except Exception as exc:
        logger.error("File save failed: %s", exc)
        return None, None

    return X_train, y_train
