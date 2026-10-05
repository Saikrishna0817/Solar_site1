"""
SolarSite-India Data Pipeline Package.

Usage:
    from solarpipeline import merge_sources, engineer_features, run_eda, preprocess, run_pipeline
"""

from .utils import get_logger, normalize_district, safe_read_csv, compute_cuf_theoretical
from .data import merge_sources
from .features import engineer_features
from .exclusions import apply_exclusions
from .eda import run_eda
from .preprocess import preprocess
from .core import run_pipeline

__all__ = [
    "get_logger", "normalize_district", "safe_read_csv", "compute_cuf_theoretical",
    "merge_sources", "engineer_features", "run_eda", "preprocess", "run_pipeline",
]