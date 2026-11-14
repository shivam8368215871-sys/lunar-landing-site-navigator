from datetime import datetime

from app.core.models import (
    AnalysisResult,
    CelestialResult,
    Site,
)
from app.science.lunar_observer import LunarObserver


class LunarAnalysisEngine:
    """
    Scientific calculation engine for lunar landing-site analysis.

    Uses NASA SPICE for real Sun/Earth positions and converts
    them into local lunar horizon coordinates.

    When LOLA terrain coverage is available, terrain-aware
    horizon information is also propagated into the result.
    """

    def __init__(self, kernel_directory: str = "data/kernels"):
        self.observer = LunarObserver(kernel_directory)

    def load(self) -> None:
        """Load NASA SPICE kernels and LOLA terrain."""
        self.observer.load()

    def unload(self) -> None:
        """Unload NASA SPICE kernels and LOLA terrain."""
        self.observer.unload()

    @staticmethod
    def _celestial_result(
        observer_result: dict,
        visible_status: str,
    ) -> CelestialResult:
        """
        Convert a LunarObserver result into the shared
        CelestialResult model.
        """

        return CelestialResult(
            elevation=observer_result["elevation"],
            azimuth=observer_result["azimuth"],
            visible=observer_result["visible"],
            status=(
                visible_status
                if observer_result["visible"]
                else "Below Horizon"
            ),

            terrain_horizon_elevation=(
                observer_result[
                    "terrain_horizon_elevation"
                ]
            ),
            terrain_visible=(
                observer_result[
                    "terrain_visible"
                ]
            ),
            terrain_status=(
                observer_result[
                    "terrain_status"
                ]
            ),
        )

    def analyze(
        self,
        site: Site,
        analysis_time: datetime,
    ) -> AnalysisResult:
        """
        Calculate real Sun and Earth observations for a lunar site.

        Geometric visibility continues to come from the existing
        SPICE + spherical lunar horizon calculation.

        Terrain-aware visibility is provided separately through
        the LOLA-derived terrain fields.
        """

        sun_result = self.observer.observe(
            target="SUN",
            latitude=site.latitude,
            longitude=site.longitude,
            analysis_time=analysis_time,
        )

        earth_result = self.observer.observe(
            target="EARTH",
            latitude=site.latitude,
            longitude=site.longitude,
            analysis_time=analysis_time,
        )

        sun = self._celestial_result(
            sun_result,
            visible_status="Above Horizon",
        )

        earth = self._celestial_result(
            earth_result,
            visible_status="Visible",
        )

        return AnalysisResult(
            site=site,
            time=analysis_time,
            sun=sun,
            earth=earth,
        )
