"""EDA visualisation module with per-plot error resilience."""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from solarpipeline.utils import PROCESSED_DIR, REPORTS_DIR, get_logger

logger = get_logger(__name__)

plt.style.use("seaborn-v0_8-whitegrid")


def _savefig(fig: plt.Figure, stem: str) -> None:
    """Save a figure to ``REPORTS_DIR / {stem}.png``."""
    path = REPORTS_DIR / f"{stem}.png"
    try:
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        logger.info("Saved: %s.png", stem)
    except Exception as exc:
        logger.warning("Failed to save %s.png: %s", stem, exc)


def run_eda(df: pd.DataFrame) -> None:
    """Generate EDA visualisations and summary reports (up to 8 outputs).

    Each visualisation is wrapped in try/except; one failure never halts the rest.
    """
    logger.info("Phase 2: EDA -- Generating visualisations")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for c in ("latitude", "longitude"):
        if c in numeric_cols:
            numeric_cols.remove(c)

    # 1. Feature distributions
    try:
        ncols = 4
        nrows = (len(numeric_cols) + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 4, nrows * 3))
        axes = axes.flatten() if hasattr(axes, "flatten") else [axes]
        for i, col in enumerate(numeric_cols):
            data = df[col].dropna()
            if len(data) == 0:
                continue
            sns.histplot(data, kde=True, ax=axes[i], color="steelblue")
            axes[i].set_title(col, fontsize=9)
            axes[i].set_xlabel("")
            axes[i].set_ylabel("Count")
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])
        _savefig(fig, "01_feature_distributions")
        plt.close(fig)
    except Exception as exc:
        logger.error("Distribution plot failed: %s", exc)

    # 2. Correlation heatmap
    try:
        ndf = df[numeric_cols].dropna(axis=1, how="all")
        if len(ndf.columns) > 1:
            corr = ndf.corr()
            w = max(10, len(ndf.columns) * 0.5)
            h = max(8, len(ndf.columns) * 0.4)
            fig, ax = plt.subplots(figsize=(w, h))
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
            _savefig(fig, "02_correlation_heatmap")
            plt.close(fig)
    except Exception as exc:
        logger.error("Correlation heatmap failed: %s", exc)

    # 3. Geospatial GHI
    try:
        required = ["avg_ghi_kwh_m2_day", "latitude", "longitude"]
        if all(c in df.columns for c in required):
            fig, ax = plt.subplots(figsize=(10, 8))
            sc = ax.scatter(df["longitude"], df["latitude"],
                            c=df["avg_ghi_kwh_m2_day"], cmap="YlOrRd",
                            s=100, edgecolors="k")
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            ax.set_title("Solar GHI across Telangana & Andhra Pradesh")
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label("GHI (kWh/m2/day)")
            _savefig(fig, "03_geospatial_ghi")
            plt.close(fig)
    except Exception as exc:
        logger.error("Geospatial map failed: %s", exc)

    # 4. Box plots by state
    try:
        if "state" in df.columns and "avg_ghi_kwh_m2_day" in df.columns:
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.boxplot(x="state", y="avg_ghi_kwh_m2_day", data=df,
                        ax=ax, hue="state", palette="Set2", legend=False)
            ax.set_title("GHI Distribution by State")
            ax.set_ylabel("GHI (kWh/m2/day)")
            _savefig(fig, "04_boxplot_ghi_by_state")
            plt.close(fig)
    except Exception as exc:
        logger.error("Box plot failed: %s", exc)

    # 5. Pairplot
    try:
        solar_opts = ["avg_ghi_kwh_m2_day", "avg_dni_kwh_m2_day", "avg_dhi_kwh_m2_day",
                      "avg_cloud_cover_pct", "elevation_m"]
        solar = [c for c in solar_opts if c in df.columns]
        if len(solar) >= 2:
            pair_df = df[solar].dropna()
            if len(pair_df) > 0:
                g = sns.pairplot(pair_df, diag_kind="kde", plot_kws={"alpha": 0.6})
                g.fig.suptitle("Solar Variable Relationships", y=1.02, fontsize=12)
                g.savefig(str(REPORTS_DIR / "05_pairplot_solar.png"), dpi=150)
                plt.close(g.fig)
                logger.info("Saved: 05_pairplot_solar.png")
    except Exception as exc:
        logger.error("Pairplot failed: %s", exc)

    # 6. Missing values heatmap
    try:
        null_count = df.isnull().sum().sum()
        if null_count > 0:
            w = max(10, df.shape[1] * 0.3)
            fig, ax = plt.subplots(figsize=(w, 6))
            sns.heatmap(df.isnull(), cbar=False, ax=ax, yticklabels=False, cmap="viridis")
            ax.set_title(f"Missing Values ({null_count} total)")
            _savefig(fig, "06_missing_values")
            plt.close(fig)
    except Exception as exc:
        logger.error("Missing heatmap failed: %s", exc)

    # 7. Summary statistics
    try:
        summary = df.describe().T
        summary["missing_count"] = len(df) - df.count()
        summary["missing_pct"] = (summary["missing_count"] / len(df) * 100).round(2)
        summary.to_csv(str(PROCESSED_DIR / "eda_summary_statistics.csv"))
        logger.info("Saved: eda_summary_statistics.csv")
    except Exception as exc:
        logger.error("Summary stats failed: %s", exc)

    # 8. Quality report
    try:
        lines = [
            "# SolarSite-India Data Quality Report",
            f"\nTotal districts: {len(df)}",
            f"Total features:  {len(df.columns)}",
            "\n--- Missing values ---",
        ]
        missing = df.isnull().sum()
        for col in missing[missing > 0].index:
            lines.append(f"  {col}: {missing[col]} ({missing[col]/len(df)*100:.1f}%)")
        with open(REPORTS_DIR / "data_quality_report.md", "w") as fh:
            fh.write("\n".join(lines))
        logger.info("Saved: data_quality_report.md")
    except Exception as exc:
        logger.error("Quality report failed: %s", exc)
