"""Evaluation metrics and utilities."""
import logging
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)


def compute_regression_metrics(y_true, y_pred) -> Dict[str, float]:
    """Compute comprehensive regression metrics."""
    return {
        "r2": r2_score(y_true, y_pred),
        "mse": mean_squared_error(y_true, y_pred),
        "mae": mean_absolute_error(y_true, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
        "mape": np.mean(np.abs((y_true - y_pred) / y_true)) * 100,
    }


def plot_prediction_vs_actual(y_true, y_pred, title="Predicted vs Actual", save_path=None):
    """Scatter plot of predictions vs actual."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_true, y_pred, alpha=0.7, edgecolors="k")
    
    # Perfect prediction line
    min_val, max_val = min(y_true.min(), y_pred.min()), max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], "r--", lw=2, label="Perfect")
    
    # Trend line
    z = np.polyfit(y_true, y_pred, 1)
    p = np.poly1d(z)
    ax.plot(sorted(y_true), p(sorted(y_true)), "b-", lw=1, alpha=0.5, label="Trend")
    
    ax.set_xlabel("Actual CUF")
    ax.set_ylabel("Predicted CUF")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        logger.info(f"Saved plot: {save_path}")
    plt.close()
    return fig


def plot_feature_importance(importances: pd.Series, save_path=None, top_n=15):
    """Bar plot of feature importances."""
    imp = importances.abs().sort_values(ascending=True).tail(top_n)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(imp)))
    bars = ax.barh(imp.index, imp.values, color=colors)
    ax.set_xlabel("Absolute Importance")
    ax.set_title(f"Top {top_n} Feature Importances")
    ax.grid(axis="x", alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        logger.info(f"Saved plot: {save_path}")
    plt.close()
    return fig


def plot_residuals(y_true, y_pred, save_path=None):
    """Residuals plot."""
    residuals = y_true - y_pred
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Residuals vs Predicted
    ax1.scatter(y_pred, residuals, alpha=0.7, edgecolors="k")
    ax1.axhline(y=0, color="r", linestyle="--")
    ax1.set_xlabel("Predicted CUF")
    ax1.set_ylabel("Residuals")
    ax1.set_title("Residuals vs Predicted")
    ax1.grid(True, alpha=0.3)
    
    # Histogram of residuals
    ax2.hist(residuals, bins=20, edgecolor="k", alpha=0.7)
    ax2.axvline(x=0, color="r", linestyle="--")
    ax2.set_xlabel("Residuals")
    ax2.set_ylabel("Count")
    ax2.set_title("Distribution of Residuals")
    ax2.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        logger.info(f"Saved plot: {save_path}")
    plt.close()
    return fig


def plot_model_comparison(results_df: pd.DataFrame, save_path=None):
    """Compare multiple models side-by-side."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    metrics = ["train_r2", "test_r2", "cv_r2_mean"]
    titles = ["Train R²", "Test R²", "CV R² (mean)"]
    
    for ax, metric, title in zip(axes, metrics, titles):
        ax.bar(results_df["model_name"], results_df[metric], alpha=0.7, edgecolor="k")
        ax.set_ylabel(metric)
        ax.set_title(title)
        ax.set_ylim(0, 1)
        ax.grid(axis="y", alpha=0.3)
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        logger.info(f"Saved plot: {save_path}")
    plt.close()
    return fig


C0_BASELINE_CSV = (
    Path(__file__).resolve().parents[3]
    / "backend" / "data_pipeline" / "outputs" / "processed" / "c0_baseline.csv"
)


def baseline_section(results: List[Dict]) -> List[str]:
    """Bar the models have to clear: the pvlib C0 physics baseline.

    C0 is scored on the same CEA-actual labels the models train on, so an ML model
    that cannot beat it has not learned anything the physics chain does not already
    know. Reported even when it is unflattering.
    """
    lines = ["\n## Baseline check (pvlib C0 physics chain)\n"]
    try:
        c0 = pd.read_csv(C0_BASELINE_CSV)
    except Exception as exc:
        lines.append(f"_baseline unavailable ({exc}); run `scripts/baseline_c0.py`._\n")
        return lines

    cea = c0[c0["cuf_source"] == "cea_plant"] if "cuf_source" in c0 else c0.iloc[0:0]
    if len(cea) < 3:
        lines.append(f"_only {len(cea)} CEA-labelled districts — not enough to score._\n")
        return lines

    base_mae = float((cea["c0_cuf"] - cea["label_cuf"]).abs().mean())
    base_rho = float(cea["c0_cuf"].corr(cea["label_cuf"], method="spearman"))
    lines.append(f"C0 vs CEA-actual ({len(cea)} districts): "
                 f"MAE={base_mae:.4f}, Spearman ρ={base_rho:.4f}\n\n")

    lines.append("| Model | CV MAE (pooled OOF) | Beats C0? |\n")
    lines.append("|-------|---------------------|-----------|\n")
    for r in results:
        mae = r.get("cv_mae_mean")
        if mae is None or (isinstance(mae, float) and np.isnan(mae)):
            continue
        lines.append(f"| {r['model_name']:15s} | {mae:.4f} | "
                     f"{'yes' if mae < base_mae else 'NO'} |\n")
    lines.append("\n_CV MAE is over plant rows; C0 MAE is over district rows — "
                 "different populations, same label definition. Negative CV R² on this "
                 "dataset mostly reflects a narrow target range, not a broken model._\n")
    return lines


def generate_report(results: List[Dict], save_path="reports/ml_report.md"):
    """Generate a markdown report from results."""
    lines = []
    lines.append("# ML Training Report\n")
    lines.append("## Model Comparison\n")
    lines.append(f"| Model | Train R² | Test R² | CV R² ± std | CV MAE | Test RMSE | Features |\n")
    lines.append(f"|-------|----------|---------|-------------|--------|-----------|----------|\n")

    for r in results:
        cv_r2 = r.get("cv_r2_mean", "N/A")
        cv_std = r.get("cv_r2_std", "N/A")
        n_feat = r.get("n_features_selected", "N/A")
        cv_mae = r.get("cv_mae_mean")
        cv_mae_s = f"{cv_mae:.4f}" if cv_mae is not None and not isinstance(cv_mae, str) else "N/A"
        lines.append(
            f"| {r['model_name']:15s} | "
            f"{r['train_r2']:.4f} | {r['test_r2']:.4f} | "
            f"{cv_r2:.4f}±{cv_std:.4f} | {cv_mae_s} | {r['test_rmse']:.6f} | {n_feat} |\n"
        )

    lines.append("\n")
    lines.extend(baseline_section(results))
    lines.append("## Top Features by Model")
    for r in results:
        if "top_10_features" in r:
            lines.append(f"\n### {r['model_name']}\n")
            for feat, imp in list(r["top_10_features"].items())[:10]:
                lines.append(f"- {feat}: {imp:.4f}\n")
    
    text = "".join(lines)
    
    with open(save_path, "w") as f:
        f.write(text)
    
    logger.info(f"Saved report: {save_path}")
    return text
