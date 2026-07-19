"""Generates the labeled wildfire-risk dataset for Phase 5.

Ground truth comes from FireEpisodeInjector's authoritative multiplier,
NOT from RuleBasedRiskAssessor — see feature_engineering.py / ground_truth.py
docstrings for why. Both models have to infer the same hidden signal from
noisy sensed values, which is what makes a rule-vs-ML comparison meaningful.

Run: uv run python scripts/generate_dataset.py
"""

import csv
from pathlib import Path

import numpy as np

from app.domain.sensor_reading import SensorReading
from app.services.dataset_generation.fire_episode_injector import FireEpisodeInjector
from app.services.dataset_generation.ground_truth import severity_to_risk_level
from app.services.risk_assessment.feature_engineering import FEATURE_NAMES, extract_features
from app.services.spatial_field import create_default_spatial_field, scatter_anchors

EPISODES = 40
EPISODE_LENGTH_TICKS = 1440  # one simulated day per episode
SAMPLES_PER_TICK = 5
OUTPUT_PATH = Path(__file__).resolve().parent.parent.parent / "ml" / "data" / "wildfire_risk_dataset.csv"


def generate() -> None:
    rng = np.random.default_rng(0)
    rows = []

    for episode_id in range(EPISODES):
        anchors = scatter_anchors(count=5, width=1000, height=1000, seed=episode_id)
        field = create_default_spatial_field(anchors, seed=episode_id)
        injector = FireEpisodeInjector(anchors, EPISODE_LENGTH_TICKS, seed=episode_id)

        for tick in range(EPISODE_LENGTH_TICKS):
            multipliers = injector.multiplier_at(tick)
            field.step(fire_risk_by_anchor=multipliers)

            for _ in range(SAMPLES_PER_TICK):
                x, y = float(rng.uniform(0, 1000)), float(rng.uniform(0, 1000))
                env = field.sample_at(x, y)
                reading = SensorReading(
                    temperature=env.ambient_temperature,
                    humidity=env.ambient_humidity,
                    smoke=env.ambient_smoke,
                )
                features = extract_features(reading)
                label = severity_to_risk_level(field.interpolate_scalar(x, y, multipliers))
                rows.append({**features, "label": label.value, "episode_id": episode_id, "tick": tick})

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[*FEATURE_NAMES, "label", "episode_id", "tick"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    generate()