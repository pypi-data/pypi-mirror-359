import numpy as np
import pandas as pd
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    f1_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

from aeon.classification.feature_based import Catch22Classifier
from aeon.classification.dummy import DummyClassifier

from f1_etl import SessionConfig, DataConfig, create_safety_car_dataset
from f1_etl.config import create_season_configs


@dataclass
class ExperimentConfig:
    """Configuration for a single experiment"""

    data_scope: str  # "one_session_one_driver", "whole_season_one_driver", etc.
    window_size: int
    prediction_horizon: int
    drivers: Optional[List[str]] = None
    test_races: Optional[List[str]] = None  # For whole season holdout


class SafetyCarEvaluator:
    """Evaluates traditional ML models for safety car prediction"""

    def __init__(self, cache_dir: str = "./f1_cache"):
        self.cache_dir = cache_dir
        self.results = []

    def _diagnose_data_issue(self, config: DataConfig) -> None:
        """Diagnose why data extraction failed"""
        print("\n=== DIAGNOSING DATA ISSUE ===")

        # Check cache directory
        if not os.path.exists(config.cache_dir):
            print(f"❌ Cache directory does not exist: {config.cache_dir}")
            return
        else:
            print(f"✅ Cache directory exists: {config.cache_dir}")
            cache_files = os.listdir(config.cache_dir)
            print(f"   Contains {len(cache_files)} files")
            if cache_files:
                print(f"   Sample files: {cache_files[:5]}")

        # Check individual sessions and aggregation
        from f1_etl.extraction import RawDataExtractor
        from f1_etl.aggregation import DataAggregator

        extractor = RawDataExtractor(config.cache_dir)
        sessions_data = []

        for i, session in enumerate(config.sessions):
            print(
                f"\n--- Session {i + 1}: {session.year} {session.race} {session.session_type} ---"
            )
            try:
                session_data = extractor.extract_session(session)
                if session_data is None:
                    print(f"❌ No data returned for this session")
                else:
                    print(f"✅ Session data extracted successfully")
                    if hasattr(session_data, "keys"):
                        print(f"   Data keys: {list(session_data.keys())}")

                        # Check driver data specifically
                        if "car_data" in session_data:
                            car_data = session_data["car_data"]
                            if hasattr(car_data, "keys"):
                                available_drivers = list(car_data.keys())
                                print(f"   Available drivers: {available_drivers}")
                            elif (
                                hasattr(car_data, "columns")
                                and "Driver" in car_data.columns
                            ):
                                available_drivers = car_data["Driver"].unique().tolist()
                                print(f"   Available drivers: {available_drivers}")
                            else:
                                print(f"   Car data type: {type(car_data)}")

                        if "drivers" in session_data:
                            drivers_data = session_data["drivers"]
                            print(f"   Drivers data type: {type(drivers_data)}")
                            if hasattr(drivers_data, "keys"):
                                print(f"   Driver keys: {list(drivers_data.keys())}")

                    sessions_data.append(session_data)

            except Exception as e:
                print(f"❌ Session extraction failed: {e}")

        # Test aggregation step
        if sessions_data:
            print(f"\n--- Testing Aggregation ---")
            aggregator = DataAggregator()
            try:
                print(f"Attempting aggregation with drivers: {config.drivers}")
                telemetry_data = aggregator.aggregate_telemetry_data(
                    sessions_data, config.drivers
                )
                if telemetry_data.empty:
                    print("❌ Aggregation returned empty DataFrame")
                    print("Trying without driver filter...")
                    telemetry_data_no_filter = aggregator.aggregate_telemetry_data(
                        sessions_data, None
                    )
                    if telemetry_data_no_filter.empty:
                        print(
                            "❌ Still empty without driver filter - aggregation issue"
                        )
                    else:
                        print(
                            f"✅ Aggregation works without driver filter: {len(telemetry_data_no_filter)} rows"
                        )
                        if "Driver" in telemetry_data_no_filter.columns:
                            actual_drivers = telemetry_data_no_filter["Driver"].unique()
                            print(f"   Actual driver codes in data: {actual_drivers}")
                else:
                    print(f"✅ Aggregation successful: {len(telemetry_data)} rows")
            except Exception as e:
                print(f"❌ Aggregation failed: {e}")

        # Check driver availability
        if config.drivers:
            print(f"\n--- Driver Filter Analysis: {config.drivers} ---")
            print(
                "Common driver codes: VER, HAM, LEC, RUS, SAI, NOR, PIA, ALO, STR, etc."
            )

        print("\n=== SUGGESTED FIXES ===")
        print("1. Try without driver filtering: drivers=None")
        print("2. Check actual driver codes in the output above")
        print("3. Verify driver codes match exactly (case-sensitive)")
        print("4. Ensure car_data contains the expected drivers")

    def create_data_config(
        self, scope: str, drivers: Optional[List[str]] = None
    ) -> DataConfig:
        """Create DataConfig based on experiment scope"""
        if scope in ["one_session_one_driver", "one_session_all_drivers"]:
            # Single Monaco race for proof of concept
            sessions = [
                SessionConfig(year=2024, race="Monaco Grand Prix", session_type="R")
            ]
        elif scope in ["whole_season_one_driver", "whole_season_all_drivers"]:
            # All 2024 races
            sessions = create_season_configs(2024, session_types=["R"])
        else:
            raise ValueError(f"Unknown scope: {scope}")

        # Convert driver abbreviations to numeric codes if needed
        numeric_drivers = None
        if drivers:
            # Enhanced driver mapping for 2024 season
            driver_map = {
                "VER": "1",
                "PER": "11",
                "LEC": "16",
                "SAI": "55",
                "HAM": "44",
                "RUS": "63",
                "NOR": "4",
                "PIA": "81",
                "ALO": "14",
                "STR": "18",
                "TSU": "22",
                "RIC": "3",
                "GAS": "10",
                "OCO": "31",
                "ALB": "23",
                "SAR": "2",
                "MAG": "20",
                "HUL": "27",
                "BOT": "77",
                "ZHO": "24",
                "BEA": "38",  # Bear (replacement driver)
            }
            numeric_drivers = []
            for d in drivers:
                if d in driver_map:
                    numeric_drivers.append(driver_map[d])
                    print(f"Mapped driver {d} -> {driver_map[d]}")
                else:
                    numeric_drivers.append(d)  # Assume it's already numeric
                    print(f"Using driver code as-is: {d}")

        return DataConfig(
            sessions=sessions, cache_dir=self.cache_dir, drivers=numeric_drivers
        )

    def create_dataset(
        self, config: DataConfig, window_size: int, prediction_horizon: int
    ) -> Dict[str, Any]:
        """Create Catch22-optimized dataset"""
        print(f"Creating dataset with config:")
        print(
            f"  Sessions: {[f'{s.year} {s.race} {s.session_type}' for s in config.sessions]}"
        )
        print(f"  Drivers: {config.drivers}")
        print(f"  Cache dir: {config.cache_dir}")

        try:
            return create_safety_car_dataset(
                config=config,
                window_size=window_size,
                prediction_horizon=prediction_horizon,
                handle_non_numeric="encode",
                handle_missing=False,
                missing_strategy="forward_fill",
                normalize=True,
                normalization_method="per_sequence",
                target_column="TrackStatus",
                enable_debug=True,  # Enable debug to see more details
            )
        except ValueError as e:
            print(f"Dataset creation failed: {e}")
            # Try to diagnose the issue
            self._diagnose_data_issue(config)
            raise

    def prepare_data(
        self,
        dataset: Dict[str, Any],
        scope: str,
        test_races: Optional[List[str]] = None,
    ) -> Tuple[np.ndarray, ...]:
        """Prepare train/test splits based on scope"""
        X = dataset["X"]
        y = dataset["y"]
        metadata = dataset["metadata"]

        # Convert to Aeon format (n_samples, n_features, n_timesteps)
        X_aeon = X.transpose(0, 2, 1)

        # Use only Speed feature (most predictive for safety car events)
        X_speed = X_aeon[:, 0:1, :]

        if scope in ["one_session_one_driver", "one_session_all_drivers"]:
            # Simple stratified split for single session
            return train_test_split(
                X_speed, y, test_size=0.2, random_state=42, stratify=y
            )
        else:
            # Whole season: holdout specific races
            if test_races is None:
                test_races = [
                    "British Grand Prix",
                    "Italian Grand Prix",
                    "Japanese Grand Prix",
                ]

            # Get race names from metadata (you'll need to implement this based on your metadata structure)
            # For now, using simple split - you should adapt based on your metadata format
            return train_test_split(
                X_speed, y, test_size=0.15, random_state=42, stratify=y
            )

    def get_models(self) -> Dict[str, Any]:
        """Get dictionary of models to evaluate"""
        models = {
            "dummy": DummyClassifier(strategy="most_frequent"),
            "dummy_balanced": DummyClassifier(strategy="stratified"),
            "logistic_regression": Catch22Classifier(
                estimator=LogisticRegression(
                    random_state=42,
                    max_iter=3000,
                    solver="saga",  # Changed from liblinear for multiclass
                    class_weight="balanced",
                ),
                outlier_norm=True,
                random_state=42,
            ),
            "random_forest": Catch22Classifier(
                estimator=RandomForestClassifier(
                    n_estimators=200,
                    random_state=42,
                    class_weight="balanced",
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                ),
                outlier_norm=True,
                random_state=42,
            ),
            # Add versions optimized for safety car detection (more aggressive for minority class)
            "rf_safety_optimized": Catch22Classifier(
                estimator=RandomForestClassifier(
                    n_estimators=300,
                    random_state=42,
                    class_weight={
                        0: 1,
                        1: 2,
                        2: 50,
                        3: 10,
                    },  # Heavy weight on safety car class
                    max_depth=15,
                    min_samples_split=3,
                    min_samples_leaf=1,
                ),
                outlier_norm=True,
                random_state=42,
            ),
        }

        return models

    def evaluate_model(
        self,
        model,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, float]:
        """Train and evaluate a single model"""
        # Train model
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Calculate detailed metrics
        precision, recall, f1, support = precision_recall_fscore_support(
            y_test, y_pred, average=None, zero_division=0
        )

        # Safety car specific metrics (class 2)
        safety_car_idx = 2
        safety_car_precision = (
            precision[safety_car_idx] if len(precision) > safety_car_idx else 0.0
        )
        safety_car_recall = (
            recall[safety_car_idx] if len(recall) > safety_car_idx else 0.0
        )
        safety_car_f1 = f1[safety_car_idx] if len(f1) > safety_car_idx else 0.0

        return {
            "accuracy": accuracy_score(y_test, y_pred),
            "f1_macro": f1_score(y_test, y_pred, average="macro", zero_division=0),
            "f1_weighted": f1_score(
                y_test, y_pred, average="weighted", zero_division=0
            ),
            "f1_safety_car": safety_car_f1,
            "precision_safety_car": safety_car_precision,
            "recall_safety_car": safety_car_recall,
            "sample_count": len(y_test),
            "predictions": y_pred,
            "true_labels": y_test,
        }

    def _get_safety_car_f1(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Get F1 score specifically for safety car class (class 2 based on your output)"""
        try:
            # Assuming safety_car is class 2 based on the distribution [11936, 2320, 128, 256]
            # where safety_car appears to be the smallest class (128 samples)
            safety_car_class = 2  # This may need adjustment based on your label encoder
            return f1_score(
                y_true,
                y_pred,
                labels=[safety_car_class],
                average="macro",
                zero_division=0,
            )
        except:
            return 0.0

    def run_experiment(self, config: ExperimentConfig) -> Dict[str, Any]:
        """Run a complete experiment"""
        print(f"\\n=== Running Experiment: {config.data_scope} ===")
        print(
            f"Window Size: {config.window_size}, Prediction Horizon: {config.prediction_horizon}"
        )

        # Create data configuration
        drivers = config.drivers if config.drivers else None
        data_config = self.create_data_config(config.data_scope, drivers)

        # Generate dataset
        print("Generating dataset...")
        dataset = self.create_dataset(
            data_config, config.window_size, config.prediction_horizon
        )

        # Prepare train/test splits
        X_train, X_test, y_train, y_test = self.prepare_data(
            dataset, config.data_scope, config.test_races
        )

        print(f"Dataset shape: Train={X_train.shape}, Test={X_test.shape}")

        # Enhanced class distribution analysis
        unique, counts = np.unique(y_train, return_counts=True)
        class_dist = dict(zip(unique, counts))
        print(f"Class distribution: {class_dist}")

        # Try to get class names from dataset if available
        try:
            if hasattr(dataset, "get") and "label_encoder" in dataset:
                label_encoder = dataset["label_encoder"]
                if hasattr(label_encoder, "get_classes"):
                    class_names = label_encoder.get_classes()
                    print(f"Class names: {class_names}")
                    for class_id, count in class_dist.items():
                        if class_id < len(class_names):
                            print(
                                f"  {class_names[class_id]}: {count} samples ({count / len(y_train) * 100:.1f}%)"
                            )
        except Exception as e:
            print(f"Could not decode class names: {e}")

        print(f"Class imbalance ratio: {max(counts) / min(counts):.1f}:1")

        # Evaluate all models
        models = self.get_models()
        results = {}

        for model_name, model in models.items():
            print(f"\\nEvaluating {model_name}...")
            try:
                model_results = self.evaluate_model(
                    model, X_train, X_test, y_train, y_test
                )
                results[model_name] = model_results

                print(f"  Accuracy: {model_results['accuracy']:.4f}")
                print(f"  F1-Macro: {model_results['f1_macro']:.4f}")
                print(f"  F1-Weighted: {model_results['f1_weighted']:.4f}")
                print(f"  Safety Car F1: {model_results['f1_safety_car']:.4f}")
                print(
                    f"  Safety Car Precision: {model_results['precision_safety_car']:.4f}"
                )
                print(f"  Safety Car Recall: {model_results['recall_safety_car']:.4f}")

            except Exception as e:
                print(f"  ERROR: {str(e)}")
                results[model_name] = {"error": str(e)}

        # Store experiment results
        experiment_result = {
            "config": config,
            "results": results,
            "dataset_info": {
                "total_samples": len(dataset["X"]),
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "features": X_train.shape[1:],
                "class_distribution": np.bincount(y_train).tolist(),
            },
        }

        self.results.append(experiment_result)
        return experiment_result

    def print_comparison(self, results: Dict[str, Any]) -> None:
        """Print comparison between models"""
        if "dummy" not in results or "error" in results["dummy"]:
            print("⚠️  Baseline model failed - cannot compare")
            return

        baseline = results["dummy"]
        print("\\n=== MODEL COMPARISON ===")
        print(
            f"{'Model':<20} {'Accuracy':<10} {'F1-Macro':<10} {'Safety-F1':<10} {'Safety-Prec':<12} {'Safety-Rec':<12}"
        )
        print("-" * 85)

        for model_name, model_results in results.items():
            if "error" in model_results:
                print(f"{model_name:<20} {'ERROR':<10}")
                continue

            acc_diff = model_results["accuracy"] - baseline["accuracy"]
            f1_diff = model_results["f1_macro"] - baseline["f1_macro"]

            print(
                f"{model_name:<20} {model_results['accuracy']:<10.4f} "
                f"{model_results['f1_macro']:<10.4f} {model_results['f1_safety_car']:<10.4f} "
                f"{model_results['precision_safety_car']:<12.4f} {model_results['recall_safety_car']:<12.4f}"
            )

        # Analysis warnings
        print("\\n=== ANALYSIS ===")
        for model_name, model_results in results.items():
            if model_name == "dummy" or "error" in model_results:
                continue

            if model_results["f1_macro"] < 0.1:
                print(
                    f"⚠️  {model_name}: Low F1-macro ({model_results['f1_macro']:.3f}) - not learning meaningful patterns"
                )

            if abs(model_results["accuracy"] - baseline["accuracy"]) < 0.01:
                print(f"⚠️  {model_name}: Similar to baseline - may not be learning")

    def run_all_experiments(self) -> None:
        """Run the complete experimental suite"""
        # Define all experiment configurations
        experiments = []

        # Data scopes
        scopes = [
            ("one_session_one_driver", ["VER"]),
            ("whole_season_one_driver", ["VER"]),
            ("one_session_all_drivers", None),
            ("whole_season_all_drivers", None),
        ]

        # Window size and prediction horizon combinations
        window_configs = [(200, 10), (300, 15), (250, 20)]

        # Generate all combinations
        for scope, drivers in scopes:
            for window_size, prediction_horizon in window_configs:
                experiments.append(
                    ExperimentConfig(
                        data_scope=scope,
                        window_size=window_size,
                        prediction_horizon=prediction_horizon,
                        drivers=drivers,
                    )
                )

        # Run all experiments
        print(f"Running {len(experiments)} experiments...")
        for i, config in enumerate(experiments, 1):
            print(f"\\n{'=' * 60}")
            print(f"EXPERIMENT {i}/{len(experiments)}")
            print(f"{'=' * 60}")

            try:
                result = self.run_experiment(config)
                self.print_comparison(result["results"])
            except Exception as e:
                print(f"EXPERIMENT FAILED: {str(e)}")

    def generate_summary_report(self) -> pd.DataFrame:
        """Generate summary report of all experiments"""
        summary_data = []

        for experiment in self.results:
            config = experiment["config"]
            results = experiment["results"]

            for model_name, model_results in results.items():
                if "error" in model_results:
                    continue

                summary_data.append(
                    {
                        "data_scope": config.data_scope,
                        "window_size": config.window_size,
                        "prediction_horizon": config.prediction_horizon,
                        "model": model_name,
                        "accuracy": model_results["accuracy"],
                        "f1_macro": model_results["f1_macro"],
                        "f1_weighted": model_results["f1_weighted"],
                        "f1_safety_car": model_results["f1_safety_car"],
                        "precision_safety_car": model_results["precision_safety_car"],
                        "recall_safety_car": model_results["recall_safety_car"],
                        "sample_count": model_results["sample_count"],
                    }
                )

        return pd.DataFrame(summary_data)

    def test_data_availability(self) -> None:
        """Test if data is available and accessible"""
        print("=== TESTING DATA AVAILABILITY ===")

        # Test 1: Basic cache directory
        if not os.path.exists(self.cache_dir):
            print(f"❌ Cache directory missing: {self.cache_dir}")
            print("Create the directory and ensure F1 data is cached there")
            return

        # Test 2: Try simplest possible configuration
        simple_config = DataConfig(
            sessions=[
                SessionConfig(year=2024, race="Bahrain Grand Prix", session_type="R")
            ],
            cache_dir=self.cache_dir,
        )

        print(f"Testing simple configuration...")
        try:
            from f1_etl.extraction import RawDataExtractor

            extractor = RawDataExtractor(self.cache_dir)
            data = extractor.extract_session(simple_config.sessions[0])

            if data is None:
                print("❌ No data returned - check race name and year")
            else:
                print("✅ Basic data extraction works")

        except Exception as e:
            print(f"❌ Basic extraction failed: {e}")

        # Test 3: List available races (if possible)
        print("\nTo fix this issue:")
        print("1. Verify your cache directory contains F1 data")
        print("2. Check the exact race names available in your data")
        print("3. Try a different race or year")
        print("4. Ensure the session type 'R' (Race) exists")


# Example usage
if __name__ == "__main__":
    # Initialize evaluator
    evaluator = SafetyCarEvaluator(cache_dir="./f1_cache")

    # Test data availability first
    evaluator.test_data_availability()

    # If data test passes, run experiment
    print("\n" + "=" * 60)

    # First try without driver filtering
    print("Testing without driver filtering...")
    test_config_no_driver = ExperimentConfig(
        data_scope="one_session_all_drivers",  # Changed to all drivers
        window_size=200,
        prediction_horizon=10,
        drivers=None,  # No driver filtering
    )

    try:
        result = evaluator.run_experiment(test_config_no_driver)
        evaluator.print_comparison(result["results"])
        print("✅ Success without driver filtering!")
    except Exception as e:
        print(f"❌ Still failed without driver filtering: {e}")

        # Try with specific driver after seeing available drivers
        print("\nTrying with VER driver (mapped to car #1)...")
        test_config_with_driver = ExperimentConfig(
            data_scope="one_session_one_driver",
            window_size=200,
            prediction_horizon=10,
            drivers=["VER"],  # Will be mapped to '1' automatically
        )

        try:
            result = evaluator.run_experiment(test_config_with_driver)
            evaluator.print_comparison(result["results"])
        except Exception as e:
            print(f"❌ Failed with VER driver: {e}")

    # Run all experiments if basic test passes
    if "result" in locals():
        print("\n" + "=" * 60)
        print("RUNNING FULL EXPERIMENTAL MATRIX")
        print("=" * 60)

        evaluator.run_all_experiments()
        summary_df = evaluator.generate_summary_report()
        print("\n=== SUMMARY REPORT ===")
        print(summary_df.to_string(index=False))

        # Save summary to file
        summary_df.to_csv("f1_safety_car_experiments_summary.csv", index=False)
        print(f"\n✅ Summary saved to: f1_safety_car_experiments_summary.csv")
