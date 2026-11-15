from datetime import datetime, timedelta

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

    def analyze_time_series(
        self,
        site: Site,
        start_time: datetime,
        duration_hours: float = 168.0,
        step_hours: float = 6.0,
    ) -> list[AnalysisResult]:
        """
        Calculate a real time series of Sun/Earth conditions.

        Every sample is calculated through the same SPICE + LOLA
        observation pipeline used by analyze(). No interpolation
        or mock values are introduced.
        """

        if duration_hours <= 0:
            raise ValueError(
                "duration_hours must be greater than zero."
            )

        if step_hours <= 0:
            raise ValueError(
                "step_hours must be greater than zero."
            )

        results = []

        elapsed_hours = 0.0

        while elapsed_hours <= duration_hours:
            analysis_time = (
                start_time
                + timedelta(hours=elapsed_hours)
            )

            results.append(
                self.analyze(
                    site,
                    analysis_time,
                )
            )

            elapsed_hours += step_hours

        if results[-1].time < (
            start_time
            + timedelta(hours=duration_hours)
        ):
            results.append(
                self.analyze(
                    site,
                    start_time
                    + timedelta(hours=duration_hours),
                )
            )

        return results
