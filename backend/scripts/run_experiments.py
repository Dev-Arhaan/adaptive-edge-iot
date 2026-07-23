"""Phase 8 experiment suite: fixed-DTC baseline vs. adaptive+rule-based vs.
adaptive+ML, across low/medium/wildfire scenarios, plus large-scale and
stress runs. Writes one row per run to ml/data/experiment_results.csv —
analysis and graphs happen in Colab (analyze_experiments.ipynb).

Run: uv run python scripts/run_experiments.py
"""
import csv
from dataclasses import asdict
from pathlib import Path

import joblib

from app.core.config import settings
from app.services.adaptive_scheduler import AdaptiveScheduler
from app.services.experiments.experiment_runner import run_experiment
from app.services.experiments.scenarios import (
    large_scale_scenario, low_risk_scenario, medium_risk_scenario, stress_test_scenario, wildfire_scenario,
)
from app.services.fixed_interval_scheduler import FixedIntervalScheduler
from app.services.risk_assessment.ml_risk_assessor import MLRiskAssessor
from app.services.risk_assessment.rule_based_risk_assessor import RuleBasedRiskAssessor
from app.services.scheduling_policy import SchedulingPolicy

OUTPUT_PATH = Path(__file__).resolve().parent.parent.parent / "ml" / "data" / "experiment_results.csv"


def _load_ml_assessor() -> MLRiskAssessor:
    bundle = joblib.load(settings.model_artifact_path)
    return MLRiskAssessor(bundle["model"], bundle["feature_names"], bundle["label_classes"])


SCHEDULERS = {
    "fixed_dtc_baseline": lambda h, td: FixedIntervalScheduler(RuleBasedRiskAssessor(), h, tick_duration_seconds=td),
    "adaptive_rule_based": lambda h, td: AdaptiveScheduler(RuleBasedRiskAssessor(), SchedulingPolicy(), h, td),
    "adaptive_ml": lambda h, td: AdaptiveScheduler(_load_ml_assessor(), SchedulingPolicy(), h, td),
}

SCENARIOS = {"low_risk": low_risk_scenario, "medium_risk": medium_risk_scenario, "wildfire": wildfire_scenario}


def main() -> None:
    results = []

    for scenario_name, scenario_fn in SCENARIOS.items():
        for scheduler_name, scheduler_factory in SCHEDULERS.items():
            result = run_experiment(
                scenario_name=scenario_name, scheduler_name=scheduler_name,
                scheduler_factory=scheduler_factory, **scenario_fn(),
            )
            results.append(result)
            print(result)

    # Large-scale / stress: adaptive+rule only — the point is scale and
    # runtime performance, not another rule-vs-ML comparison.
    for scenario_name, scenario_fn in [("large_scale", large_scale_scenario), ("stress_test", stress_test_scenario)]:
        result = run_experiment(
            scenario_name=scenario_name, scheduler_name="adaptive_rule_based",
            scheduler_factory=SCHEDULERS["adaptive_rule_based"], **scenario_fn(),
        )
        results.append(result)
        print(result)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(r) for r in results)

    print(f"Wrote {len(results)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()