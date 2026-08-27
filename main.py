"""Main entry point for ML training."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ml.config import Config
from src.ml.pipelines.ml_pipeline import MLPipeline


def main():
    parser = argparse.ArgumentParser(description="SolarSite-India ML Training Pipeline")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["random_forest", "ridge", "lasso"],
        help="Models to train",
    )
    parser.add_argument(
        "--feature-selection",
        default="rfe",
        choices=["none", "rfe", "lasso"],
        help="Feature selection method",
    )
    parser.add_argument(
        "--n-features",
        type=int,
        default=15,
        help="Features to select",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )
    parser.add_argument(
        "--hpo",
        action="store_true",
        help="Run hyperparameter optimization (Optuna)",
    )
    parser.add_argument(
        "--hpo-trials",
        type=int,
        default=30,
        help="Trials per model for HPO",
    )
    
    args = parser.parse_args()
    
    # Setup configuration
    config = Config()
    config.trainer.random_state = args.seed
    config.trainer.feature_selection_method = args.feature_selection
    config.trainer.n_features_to_select = args.n_features
    
    # Run pipeline
    pipeline = MLPipeline(config)
    results = pipeline.run(model_names=args.models)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    for r in results:
        print(f"{r['model_name']:20s} | Train R²: {r['train_r2']:.4f} | Test R²: {r['test_r2']:.4f} | "
              f"CV R²: {r.get('cv_r2_mean', 0):.4f}±{r.get('cv_r2_std', 0):.4f}")
    
    if args.hpo:
        print("\n" + "=" * 60)
        print("HYPERPARAMETER OPTIMIZATION (CV on train only, no test leakage)")
        print("=" * 60)
        from src.ml.data_loader import SolarDataLoader
        import pandas as pd

        dl = SolarDataLoader(config.data)
        X_train, y_train, X_test, y_test, fnames = dl.load()
        X_train_scaled, X_test_scaled = dl.fit_transform(X_train, X_test)

        for model_name in args.models:
            try:
                from src.ml.optimization import optimize_hyperparameters
                hpo_result = optimize_hyperparameters(
                    model_name,
                    X_train_scaled,
                    y_train.values,
                    X_test_scaled,
                    y_test.values,
                    config,
                    n_trials=args.hpo_trials,
                )
                cv_score = hpo_result.get("best_cv_score", 0)
                test_score = hpo_result.get("test_r2", 0)
                print(f"{model_name:20s} | CV R²: {cv_score:.4f} | Test R²: {test_score:.4f} | Params: {hpo_result['best_params']}")
            except Exception as e:
                print(f"[{model_name}] HPO failed: {e}")
    
    print(f"\nReports saved to: {config.reports_dir}")
    print(f"Models saved to: {config.models_dir}")
    print(f"Logs saved to: {config.logs_dir}")


if __name__ == "__main__":
    main()
