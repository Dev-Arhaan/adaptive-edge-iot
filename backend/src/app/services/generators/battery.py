class BatteryDrainModel:
    """Pure function of node state — deterministic, no RNG. Kept separate
    from node scheduling (Phase 3): *how much* a wake costs is a hardware
    question, *when* a node wakes is a scheduling question."""

    def __init__(self, awake_drain_per_tick: float = 0.05, asleep_drain_per_tick: float = 0.002):
        self._awake_drain = awake_drain_per_tick
        self._asleep_drain = asleep_drain_per_tick

    def drain(self, current_battery: float, is_awake: bool) -> float:
        cost = self._awake_drain if is_awake else self._asleep_drain
        return max(0.0, current_battery - cost)