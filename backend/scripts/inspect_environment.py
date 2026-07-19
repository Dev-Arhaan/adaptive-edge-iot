"""Manual sanity-check for Phase 2 generators — not part of the automated
test suite (which checks determinism/bounds only), this is for eyeballing
that the numbers are actually plausible before trusting them in Phase 3+.

Run: uv run python scripts/inspect_environment.py
"""

from app.services.spatial_field import create_default_spatial_field, scatter_anchors

TICKS_TO_RUN = 1440 * 2  # 2 simulated days at 1-minute ticks
PRINT_EVERY = 60          # once per simulated hour


def main() -> None:
    anchors = scatter_anchors(count=5, width=1000, height=1000, seed=1)
    field = create_default_spatial_field(anchors, seed=1)

    print(f"{'tick':>5} {'temp':>6} {'humid':>6} {'wind':>6} {'rain':>5} {'smoke':>6}")
    for t in range(TICKS_TO_RUN):
        field.step()
        if t % PRINT_EVERY == 0:
            s = field.sample_at(500, 500)  # roughly between anchors
            print(
                f"{s.tick:>5} {s.ambient_temperature:>6.1f} {s.ambient_humidity:>6.1f} "
                f"{s.wind_speed:>6.1f} {str(s.is_raining):>5} {s.ambient_smoke:>6.2f}"
            )


if __name__ == "__main__":
    main()