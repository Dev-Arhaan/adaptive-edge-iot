from dataclasses import dataclass


@dataclass
class SpatialAnchor:
    """A virtual weather station — a point the SpatialField samples
    independently, that node/cluster readings get interpolated between."""

    id: str
    x: float
    y: float