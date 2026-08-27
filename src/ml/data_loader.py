"""Data loading and preprocessing utilities for the ML pipeline."""
import logging
from pathlib import Path
from typing import Optional, Tuple

import joblib
import numpy as np
import pandas as pd
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
        """
        train_df = pd.read_csv(self.cfg.features_train_path)
        train_labels = pd.read_csv(self.cfg.labels_train_path)
        test_df = pd.read_csv(self.cfg.features_test_path)
        test_labels = pd.read_csv(self.cfg.labels_test_path)

        logger.info(f"Loaded train: {train_df.shape}, test: {test_df.shape}")

        # Extract district IDs if needed
        self.train_ids = train_df[self.cfg.id_column].values if self.cfg.id_column in train_df.columns else None
        self.test_ids = test_df[self.cfg.id_column].values if self.cfg.id_column in test_df.columns else None

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
