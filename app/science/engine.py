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

    def calculate_lighting_metrics(
        self,
        results: list[AnalysisResult],
    ) -> dict[str, float]:
        """
        Calculate terrain-aware illumination metrics from a real
        SPICE + LOLA mission timeline.

        Illumination percentage is based on the duration of timeline
        intervals during which the Sun is mission-visible.

        Longest dark period is the longest continuous interval during
        which the Sun is mission-blocked by the terrain-aware result.
        The precision therefore follows the selected timeline sampling.
        """

        if not results:
            raise ValueError(
                "results must contain at least one analysis result."
            )

        if len(results) == 1:
            return {
                "illumination_percent": (
                    100.0
                    if results[0].sun.mission_visible
                    else 0.0
                ),
                "longest_dark_hours": 0.0,
            }

        illuminated_hours = 0.0
        dark_hours = 0.0
        longest_dark_hours = 0.0
        current_dark_hours = 0.0

        for current, next_result in zip(
            results,
            results[1:],
        ):
            interval_hours = (
                next_result.time - current.time
            ).total_seconds() / 3600.0

            if current.sun.mission_visible:
                illuminated_hours += interval_hours
                current_dark_hours = 0.0
            else:
                dark_hours += interval_hours
                current_dark_hours += interval_hours
                longest_dark_hours = max(
                    longest_dark_hours,
                    current_dark_hours,
                )

        total_hours = (
            illuminated_hours + dark_hours
        )

        illumination_percent = (
            100.0 * illuminated_hours / total_hours
            if total_hours > 0.0
            else 0.0
        )

        return {
            "illumination_percent": illumination_percent,
            "longest_dark_hours": longest_dark_hours,
        }

    def calculate_communications_metrics(
        self,
        results: list[AnalysisResult],
    ) -> dict[str, float]:
        """
        Calculate terrain-aware Earth communication/contact metrics
        from a real SPICE + LOLA mission timeline.

        Earth contact is defined by terrain-aware Earth mission
        visibility. Contact hours are calculated from the duration
        of timeline intervals during which Earth is mission-visible.

        Longest communication blackout follows the same timeline
        sampling precision as the supplied results.
        """

        if not results:
            raise ValueError(
                "results must contain at least one analysis result."
            )

        if len(results) == 1:
            return {
                "contact_hours": 0.0,
                "contact_percent": (
                    100.0
                    if results[0].earth.mission_visible
                    else 0.0
                ),
                "longest_blackout_hours": 0.0,
            }

        contact_hours = 0.0
        blackout_hours = 0.0
        longest_blackout_hours = 0.0
        current_blackout_hours = 0.0

        for current, next_result in zip(
            results,
            results[1:],
        ):
            interval_hours = (
                next_result.time - current.time
            ).total_seconds() / 3600.0

            if current.earth.mission_visible:
                contact_hours += interval_hours
                current_blackout_hours = 0.0
            else:
                blackout_hours += interval_hours
                current_blackout_hours += interval_hours
                longest_blackout_hours = max(
                    longest_blackout_hours,
                    current_blackout_hours,
                )

        total_hours = (
            contact_hours + blackout_hours
        )

        contact_percent = (
            100.0 * contact_hours / total_hours
            if total_hours > 0.0
            else 0.0
        )

        return {
            "contact_hours": contact_hours,
            "contact_percent": contact_percent,
            "longest_blackout_hours": longest_blackout_hours,
        }


    def calculate_suitability_score(
        self,
        lighting_metrics: dict[str, float],
        communications_metrics: dict[str, float],
    ) -> dict[str, float]:
        """
        Calculate a transparent 100-point landing-site suitability score.

        The score combines terrain-aware illumination,
        Earth communication availability, and the longest
        continuous dark period.

        Weights:
        - Illumination: 40 points
        - Earth contact: 35 points
        - Maximum dark-period penalty: 25 points

        The darkness component is linearly scaled across
        a 7-day (168-hour) mission window.
        """

        illumination_percent = float(
            lighting_metrics["illumination_percent"]
        )

        contact_percent = float(
            communications_metrics["contact_percent"]
        )

        longest_dark_hours = float(
            lighting_metrics["longest_dark_hours"]
        )

        illumination_points = (
            illumination_percent * 0.40
        )

        contact_points = (
            contact_percent * 0.35
        )

        darkness_fraction = min(
            max(longest_dark_hours / 168.0, 0.0),
            1.0,
        )

        darkness_points = (
            (1.0 - darkness_fraction) * 25.0
        )

        total_score = (
            illumination_points
            + contact_points
            + darkness_points
        )

        return {
            "score": total_score,
            "illumination_points": illumination_points,
            "contact_points": contact_points,
            "darkness_points": darkness_points,
        }

    def calculate_next_events(
        self,
        results: list[AnalysisResult],
    ) -> dict[str, object | None]:
        """
        Identify the next sampled Sun and Earth visibility events
        from a real SPICE + LOLA mission timeline.

        Event definitions:
        - Sun Rise: terrain-aware Sun visibility changes False -> True
        - Sun Set: terrain-aware Sun visibility changes True -> False
        - Earth Contact: terrain-aware Earth visibility changes False -> True
        - Earth Contact Loss: terrain-aware Earth visibility changes True -> False

        Event times are the timestamps of the first timeline sample
        after the visibility transition. Countdown hours are measured
        from the first timeline timestamp.
        """

        if not results:
            raise ValueError(
                "results must contain at least one analysis result."
            )

        events = {
            "next_sun_event": None,
            "next_sun_event_time": None,
            "next_sun_countdown_hours": None,
            "next_earth_event": None,
            "next_earth_event_time": None,
            "next_earth_countdown_hours": None,
        }

        if len(results) < 2:
            return events

        start_time = results[0].time

        for current, next_result in zip(
            results,
            results[1:],
        ):
            sun_before = current.sun.mission_visible
            sun_after = next_result.sun.mission_visible

            if sun_before != sun_after:
                if sun_after:
                    events["next_sun_event"] = "Sun Rise"
                else:
                    events["next_sun_event"] = "Sun Set"

                events["next_sun_event_time"] = next_result.time

                events["next_sun_countdown_hours"] = (
                    next_result.time - start_time
                ).total_seconds() / 3600.0

                break

        for current, next_result in zip(
            results,
            results[1:],
        ):
            earth_before = current.earth.mission_visible
            earth_after = next_result.earth.mission_visible

            if earth_before != earth_after:
                if earth_after:
                    events["next_earth_event"] = "Earth Contact"
                else:
                    events["next_earth_event"] = "Earth Contact Loss"

                events["next_earth_event_time"] = next_result.time

                events["next_earth_countdown_hours"] = (
                    next_result.time - start_time
                ).total_seconds() / 3600.0

                break

        return events
