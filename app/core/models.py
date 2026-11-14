from dataclasses import dataclass
from datetime import datetime


@dataclass
class Site:
    name: str
    latitude: float
    longitude: float


@dataclass
class CelestialResult:
    elevation: float
    azimuth: float
    visible: bool
    status: str

    # Terrain-aware visibility.
    #
    # These have defaults so the existing GUI/science code
    # remains compatible while terrain analysis is integrated.
    terrain_horizon_elevation: float | None = None
    terrain_visible: bool | None = None
    terrain_status: str | None = None

    @property
    def mission_visible(self) -> bool:
        """User-facing visibility: prefer terrain-aware visibility when available."""
        if self.terrain_visible is not None:
            return self.terrain_visible
        return self.visible


@dataclass
class AnalysisResult:
    site: Site
    time: datetime
    sun: CelestialResult
    earth: CelestialResult
