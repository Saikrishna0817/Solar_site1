"""ML leakage guards — run on data machine (needs pandas/sklearn/pytest).

Covers Phase-3 invariants with tmp fixtures only (no real data):
1. loader drops id + categorical cols (no target/id leakage into X)
2. cuf_source filter keeps measured rows; warns-and-keeps-all when column absent
3. scaler save/load round-trips the exact transform (train/serve parity)
4. HPO ridge space reaches the tiny-alpha regime (shared space, no 1.0 floor)
"""
import numpy as np
import pandas as pd
import pytest

from src.ml.config import DataConfig
from src.ml.data_loader import SolarDataLoader


def _make_csvs(tmp_path, with_source=True):
    feats = pd.DataFrame({
        "district": ["a", "b", "c", "d"],
        "dominant_land_use": ["crop", "crop", "barren", "barren"],
        "ghi": [5.0, 5.2, 5.4, 5.6],
        "temp": [27.0, 28.0, 29.0, 30.0],
    })
    labels = pd.DataFrame({
        "district": ["a", "b", "c", "d"],
        "state": ["TS", "TS", "AP", "AP"],
        "cuf": [0.15, 0.16, 0.14, 0.155],
    })
    if with_source:
        labels["cuf_source"] = ["cea_plant", "physics", "cea_plant", "physics"]
    fp, lp = str(tmp_path / "features_train.csv"), str(tmp_path / "labels_train.csv")
    feats.to_csv(fp, index=False)
    labels.to_csv(lp, index=False)
    return fp, lp


def _cfg(fp, lp, cuf_filter="all"):
    return DataConfig(features_train_path=fp, labels_train_path=lp,
                      features_test_path=fp, labels_test_path=lp,
                      cuf_source_filter=cuf_filter)


def test_no_id_or_categorical_leakage(tmp_path):
    dl = SolarDataLoader(_cfg(*_make_csvs(tmp_path)))
    X_train, y_train, _, _, fnames = dl.load()
    assert "district" not in X_train.columns
    assert "dominant_land_use" not in X_train.columns
    assert "cuf" not in fnames
    assert len(y_train) == 4


def test_cuf_source_filter(tmp_path):
    dl = SolarDataLoader(_cfg(*_make_csvs(tmp_path, with_source=True), cuf_filter="cea_plant"))
    X_train, y_train, _, _, _ = dl.load()
    assert len(y_train) == 2  # only measured rows
    assert set(X_train["ghi"].tolist()) == {5.0, 5.4}


def test_cuf_source_missing_warns_and_keeps_all(tmp_path, caplog):
    dl = SolarDataLoader(_cfg(*_make_csvs(tmp_path, with_source=False), cuf_filter="cea_plant"))
    X_train, y_train, _, _, _ = dl.load()
    assert len(y_train) == 4  # graceful fallback, no silent empty frame
    assert "lack cuf_source" in caplog.text


def test_scaler_roundtrip(tmp_path):
    dl = SolarDataLoader(_cfg(*_make_csvs(tmp_path)))
    X_train, _, X_test, _, _ = dl.load()
    _, Xs_te = dl.fit_transform(X_train, X_test)
    spath = str(tmp_path / "prep.joblib")
    dl.save_preprocessor(spath)
    dl2 = SolarDataLoader(_cfg(*_make_csvs(tmp_path)))
    dl2.load_preprocessor(spath)
    np.testing.assert_allclose(dl2._scaler.transform(X_test), Xs_te)


def test_hpo_ridge_space_reaches_tiny_alpha():
    from src.ml.optimization import _suggest

    class Trial:
        def suggest_float(self, name, lo, hi, log=False):
            assert lo <= 1e-4, f"ridge space floor {lo} excludes optimum regime"
            return lo
        def suggest_int(self, *a, **k):
            return 0

    assert _suggest(Trial(), "ridge", None)["ridge_alpha"] <= 1e-4


def test_collinear_drop_keeps_first(tmp_path):
    from src.ml.trainer import Trainer
    from src.ml.config import Config
    import json
    import pandas as pd

    X = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
                      "b": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],  # r=1.0 with a
                      "c": [6.0, 1.0, 4.0, 2.0, 5.0, 3.0]})
    y = pd.Series([0.1, 0.2, 0.15, 0.25, 0.2, 0.3])
    cfg = Config()
    cfg.models_dir = tmp_path  # never touch real artifacts
    t = Trainer(cfg)
    res, _ = t.train(X, y, X, y, list(X.columns), model_name="ridge")
    assert res["n_features_selected"] <= 2

    # the twin b must be gone before selection runs, and must never be persisted
    saved = json.loads((tmp_path / "feature_names.json").read_text())
    assert saved == ["a", "c"], f"collinear twin leaked into the feature set: {saved}"

    # one scaler artifact, fitted on train rows only
    import joblib
    scaler = joblib.load(tmp_path / "scaler_selected.joblib")
    assert scaler.n_features_in_ == len(saved)
    # fitted means it carries training means, not identity zeros/ones-from-nothing
    assert not (scaler.mean_ == 0).all()
