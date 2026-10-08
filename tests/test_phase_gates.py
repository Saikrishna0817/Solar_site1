"""Phase-6 gate tests: label provenance, district frame, feature-set hygiene.

Guards the plan's gates:
  * "Zero non-CEA labels in training" — the default filter drops physics rows
  * label = actual MWh / MW / 8760 — asserted against the CEA register itself
  * district frame is internally consistent (60 today, 61 when Polavaram lands)
  * collinear twins never reach the saved feature set (see test_ml_leakage)
"""
from pathlib import Path
import json
import math
import re

import pandas as pd
import pytest

from config.settings import DISTRICTS
from solarpipeline.utils import PipelineConfig
from src.ml.config import DataConfig
from src.ml.data_loader import SolarDataLoader

ROOT = Path(__file__).resolve().parents[1]
PLANT_DATASET = ROOT / "data" / "plant_labels" / "plant_dataset.csv"
PLANT_REGISTER = ROOT / "data" / "plant_cuf" / "solar_plants_india.csv"
SCOPE_STATES = ["Telangana", "Andhra Pradesh"]


def test_label_filter_defaults_to_cea_plant():
    """A bare DataConfig() must never train on physics-derived labels."""
    assert DataConfig().cuf_source_filter == "cea_plant"


def test_no_physics_rows_survive_default_filter(tmp_path):
    feats = pd.DataFrame({"district": ["a", "b", "c", "d"], "ghi": [5.0, 5.2, 5.4, 5.6]})
    labels = pd.DataFrame({
        "district": ["a", "b", "c", "d"],
        "cuf": [0.15, 0.16, 0.14, 0.155],
        "cuf_source": ["cea_plant", "physics", "cea_plant", "physics"],
    })
    fp, lp = str(tmp_path / "f.csv"), str(tmp_path / "l.csv")
    feats.to_csv(fp, index=False)
    labels.to_csv(lp, index=False)

    # cuf_source_filter deliberately NOT passed — the default is what we test
    cfg = DataConfig(features_train_path=fp, labels_train_path=lp,
                     features_test_path=fp, labels_test_path=lp)
    assert cfg.cuf_source_filter == "cea_plant"

    dl = SolarDataLoader(cfg)
    _, y_train, _, _, _ = dl.load()
    assert len(y_train) == 2, "physics-labelled rows must not reach training"
    assert list(dl.train_ids) == ["a", "c"]


def test_plant_dataset_is_pure_cea():
    if not PLANT_DATASET.exists():
        pytest.skip("plant dataset not built — run scripts/build_plant_dataset.py")
    df = pd.read_csv(PLANT_DATASET)
    assert set(df["cuf_source"].unique()) == {"cea_plant"}
    assert len(df) >= 10


def test_cea_register_obeys_hard_rule():
    """CUF = actual MU*1000 / MW / 8760, for every in-scope plant in the register."""
    if not PLANT_REGISTER.exists():
        pytest.skip("CEA plant register missing")
    reg = pd.read_csv(PLANT_REGISTER)
    inscope = reg[reg["state"].isin(SCOPE_STATES)]
    assert len(inscope) == 13, "in-scope register changed — recheck the label merge"
    recomputed = inscope["annual_generation_mu"] * 1000.0 / (inscope["installed_capacity_mw"] * 8760.0)
    assert (inscope["annual_cuf"] - recomputed).abs().max() < 0.01


def test_district_frame_matches_expected_count():
    """In-scope frame = TS 33 + AP 27 = 60 today; 61 the moment Polavaram has data."""
    in_scope = DISTRICTS["Telangana"] + DISTRICTS["Andhra Pradesh"]
    assert in_scope == PipelineConfig().expected_districts, (
        "settings.DISTRICTS and PipelineConfig.expected_districts disagree"
    )
    assert in_scope == 60, (
        "District frame changed — update PipelineConfig.expected_districts and the "
        "README in the same commit (61 when Polavaram lands)."
    )


# --- Gate 2 (Phase 2) + hygiene (Phase 7) -------------------------------------

LABEL_DERIVED = re.compile(
    r"(^|_)(mu|energy|generation|label|actual|installed_capacity)(_|$)", re.I
)


def _pre_registered() -> dict:
    path = ROOT / "models" / "pre_registered_features.json"
    assert path.exists(), "feature list not pre-registered — run scripts/phase3_residual_ci.py"
    return json.loads(path.read_text())


def test_feature_table_has_no_label_derived_columns():
    """Gate 2: no label-derived column may sit in the feature tables or the list."""
    pre = _pre_registered()
    df = pd.read_csv(PLANT_DATASET)
    bad = [c for c in df.columns if LABEL_DERIVED.search(c) and c != "cuf"]
    assert not bad, f"label-derived columns leaked into plant_dataset: {bad}"
    feats = pre["features"]
    assert not [f for f in feats if LABEL_DERIVED.search(f) or f == "cuf"], (
        "pre-registered feature list includes the target or a label-derived column"
    )
    report = ROOT / "reports" / "feature_sources.md"
    assert report.exists(), "every feature needs a source row (Phase 2 Gate 2)"
    txt = report.read_text()
    for f in feats:
        assert f in txt, f"feature '{f}' has no source row in feature_sources.md"


def test_pre_registered_feature_count_within_n_over_10():
    """Hygiene: model feature count <= ceil(n/10), rounding documented in the file."""
    pre = _pre_registered()
    n = int(pre["n"])
    cap = math.ceil(n / 10)
    assert len(pre["features"]) <= cap, (
        f"{len(pre['features'])} features for n={n} exceeds ceil(n/10)={cap}"
    )
    assert pre.get("committed_before_runs") is True
    assert pre.get("n_over_10") == round(n / 10, 1)


def test_gate_json_schema():
    """Gate 3 artefact carries the verdict, both checks, the interval and CI."""
    gate = json.loads((ROOT / "models" / "gate.json").read_text())
    required = {"generated_at", "cv", "n_rows", "n_districts",
                "pre_registered_features", "models", "heldout", "gate3_pass",
                "served_model", "artifact", "serving"}
    missing = required - set(gate)
    assert not missing, f"gate.json missing keys: {sorted(missing)}"
    served = gate["served_model"]
    lo, hi = gate["models"][served]["delta_ci95"]
    assert lo < hi, "CI ordering broken"
    if gate["gate3_pass"]:
        assert hi < 0, "Gate 3 passed without the CI excluding zero"
    assert "conformal90_halfwidth" in gate["models"][served]
    assert gate["heldout"]["winner"] in {"model", "c0"}


def test_label_csv_schemas():
    """Phase 1 outputs keep their provenance columns."""
    base = ROOT / "data" / "plant_labels"
    e = pd.read_csv(base / "plant_month_energy.csv")
    assert {"plant_name", "month", "mu", "source_file", "state", "source_url"} <= set(e.columns)
    assert e["mu"].notna().all()
    c = pd.read_csv(base / "plant_cuf.csv")
    assert set(c["cuf_source"]) == {"official_monthly"}
    i = pd.read_csv(base / "cea_isgs_month_energy.csv")
    assert {"station", "month", "generation_mwh", "alias_of"} <= set(i.columns)
