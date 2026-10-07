"""Data loading and preprocessing utilities for the ML pipeline."""
import logging
from pathlib import Path
from typing import Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)


class SolarDataLoader:
    """Load and preprocess features/labels for train and test."""

    def __init__(self, data_cfg):
        self.cfg = data_cfg
        self._scaler: Optional[StandardScaler] = None
        self._label_encoder: Optional[LabelEncoder] = None

    def load(self) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, list]:
        """
        Returns X_train, y_train, X_test, y_test, feature_names.

        Also sets self.train_groups / self.test_groups (district per row) for
        spatial group CV, and self.train_ids / self.test_ids (row identity).
        """
        if getattr(self.cfg, "unit", "district") == "plant":
            return self._load_plant()
        return self._load_split()

    # ── plant-level unit (one row per CEA plant) ─────────────

    def _load_plant(self):
        path = Path(self.cfg.plant_dataset_path)
        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found — run: python scripts/build_plant_dataset.py"
            )
        df = pd.read_csv(path)

        filt = getattr(self.cfg, "cuf_source_filter", "all")
        if filt != "all" and "cuf_source" in df.columns:
            keep = df["cuf_source"] == filt
            logger.info("cuf_source=%s: kept %d/%d plant rows", filt, keep.sum(), len(keep))
            df = df[keep]
        if len(df) < 5:
            raise ValueError(f"Only {len(df)} labelled plant rows — too few to train.")

        # ponytail: 80/20 unstratified — with 13 rows a 2-class stratified split is
        # impossible (needs >=31% test). Group CV in the trainer is the real metric.
        train_df, test_df = train_test_split(
            df, test_size=0.2, random_state=42, shuffle=True
        )

        self.train_groups = train_df["district"].values
        self.test_groups = test_df["district"].values
        self.train_ids = train_df["plant_name"].values
        self.test_ids = test_df["plant_name"].values

        y_train = train_df[self.cfg.target_column]
        y_test = test_df[self.cfg.target_column]

        # String/identity columns drop out automatically; the builder never emits
        # capacity or generation, both of which reconstruct the CUF label.
        X_train = train_df.drop(columns=[self.cfg.target_column]).select_dtypes(include="number")
        X_test = test_df.drop(columns=[self.cfg.target_column]).select_dtypes(include="number")
        X_test = X_test[X_train.columns]

        feature_names = X_train.columns.tolist()
        logger.info(
            "Plant unit: train %d rows, test %d rows, %d features, target [%.4f, %.4f]",
            len(X_train), len(X_test), len(feature_names), y_train.min(), y_train.max(),
        )
        return X_train, y_train, X_test, y_test, feature_names

    # ── district unit (pre-split 4-file frame) ───────────────

    def _load_split(self) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, list]:
        train_df = pd.read_csv(self.cfg.features_train_path)
        train_labels = pd.read_csv(self.cfg.labels_train_path)
        test_df = pd.read_csv(self.cfg.features_test_path)
        test_labels = pd.read_csv(self.cfg.labels_test_path)

        logger.info(f"Loaded train: {train_df.shape}, test: {test_df.shape}")

        # Real-CUF filter: keep measured plant rows when the merge exports cuf_source.
        filt = getattr(self.cfg, "cuf_source_filter", "all")
        if filt != "all":
            if "cuf_source" in train_labels.columns:
                keep_tr = train_labels["cuf_source"] == filt
                keep_te = test_labels["cuf_source"] == filt
                logger.info(f"cuf_source={filt}: {keep_tr.sum()}/{len(keep_tr)} train, "
                            f"{keep_te.sum()}/{len(keep_te)} test rows kept")
                train_df, train_labels = train_df[keep_tr], train_labels[keep_tr]
                test_df, test_labels = test_df[keep_te], test_labels[keep_te]
            else:
                logger.warning("cuf_source_filter=%s but labels lack cuf_source column; "
                               "using all rows (run Phase-2 merge first)", filt)

        # Extract district IDs if needed
        self.train_ids = train_df[self.cfg.id_column].values if self.cfg.id_column in train_df.columns else None
        self.test_ids = test_df[self.cfg.id_column].values if self.cfg.id_column in test_df.columns else None
        # In the district frame the id IS the district, so groups come for free.
        self.train_groups, self.test_groups = self.train_ids, self.test_ids

        # Drop ID columns
        drop_cols = [c for c in [self.cfg.id_column, self.cfg.categorical_column] if c in train_df.columns]
        X_train = train_df.drop(columns=drop_cols)
        X_test = test_df.drop(columns=drop_cols)

        # Target
        y_train = train_labels[self.cfg.target_column]
        y_test = test_labels[self.cfg.target_column]

        feature_names = X_train.columns.tolist()
        logger.info(f"Features: {len(feature_names)}, target range: [{y_train.min():.4f}, {y_train.max():.4f}]")

        return X_train, y_train, X_test, y_test, feature_names

    def fit_transform(self, X_train: pd.DataFrame, X_test) -> Tuple[np.ndarray, np.ndarray]:
        """Standardize numeric features; fit on train, apply to test."""
        self._scaler = StandardScaler()
        X_train_scaled = self._scaler.fit_transform(X_train)
        X_test_scaled = self._scaler.transform(X_test)
        return X_train_scaled, X_test_scaled

    def save_preprocessor(self, path: str) -> None:
        joblib.dump(self._scaler, path)

    def load_preprocessor(self, path: str) -> None:
        self._scaler = joblib.load(path)
