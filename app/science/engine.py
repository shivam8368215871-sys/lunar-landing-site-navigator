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


    def calculate_next_events_extended(
        self,
        site: Site,
        start_time: datetime,
        initial_results: list[AnalysisResult],
        search_chunk_hours: float = 168.0,
        max_search_hours: float = 1440.0,
        step_hours: float = 1.0,
    ) -> dict[str, object | None]:
        """
        Find the next real Sun/Earth visibility events.

        The supplied initial timeline is searched first. If no event is
        found, additional future windows are analyzed in chunks until
        the first real visibility transition is found or the maximum
        search horizon is reached.

        This preserves the selected display timeline while allowing
        event detection beyond it without calculating the entire
        maximum horizon up front.
        """

        if not initial_results:
            raise ValueError(
                "initial_results must contain at least one analysis result."
            )

        events = self.calculate_next_events(
            initial_results,
            site=site,
        )

        events["search_horizon_hours"] = 0.0
        events["earth_always_visible"] = False
        earth_all_visible = all(
            result.earth.mission_visible
            for result in initial_results
        )

        if (
            events["next_sun_event"] is not None
            or events["next_earth_event"] is not None
        ):
            events["search_horizon_hours"] = (
                initial_results[-1].time - start_time
            ).total_seconds() / 3600.0

            return events

        search_start = initial_results[-1].time
        elapsed_hours = (
            search_start - start_time
        ).total_seconds() / 3600.0

        while elapsed_hours < max_search_hours:
            chunk_end = min(
                elapsed_hours + search_chunk_hours,
                max_search_hours,
            )

            chunk_start_time = search_start
            chunk_duration = chunk_end - elapsed_hours

            if chunk_duration <= 0.0:
                break

            chunk_results = self.analyze_time_series(
                site=site,
                start_time=chunk_start_time,
                duration_hours=chunk_duration,
                step_hours=step_hours,
            )

            earth_all_visible = (
                earth_all_visible
                and all(
                    result.earth.mission_visible
                    for result in chunk_results
                )
            )

            # Include the last sample from the previous window so a
            # visibility transition at the chunk boundary is detectable.
            combined_results = [
                initial_results[-1],
                *chunk_results,
            ]

            chunk_events = self.calculate_next_events(
                combined_results,
                site=site,
            )

            if (
                chunk_events["next_sun_event"] is not None
                or chunk_events["next_earth_event"] is not None
            ):
                for time_key, countdown_key in (
                    (
                        "next_sun_event_time",
                        "next_sun_countdown_hours",
                    ),
                    (
                        "next_earth_event_time",
                        "next_earth_countdown_hours",
                    ),
                ):
                    event_time = chunk_events[time_key]

                    if event_time is not None:
                        chunk_events[countdown_key] = (
                            event_time - start_time
                        ).total_seconds() / 3600.0

                chunk_events["search_horizon_hours"] = (
                    chunk_results[-1].time - start_time
                ).total_seconds() / 3600.0
                chunk_events["earth_always_visible"] = (
                    earth_all_visible
                )

                return chunk_events

            search_start = chunk_results[-1].time
            elapsed_hours = (
                search_start - start_time
            ).total_seconds() / 3600.0

        events["search_horizon_hours"] = (
            search_start - start_time
        ).total_seconds() / 3600.0

        # No Earth visibility transition occurred anywhere in the
        # searched real timeline. The stronger statement is only made
        # when Earth remained visible throughout every searched chunk.
        events["earth_always_visible"] = earth_all_visible

        return events

    def calculate_suitability_score(
        self,
        lighting_metrics: dict[str, float],
        communications_metrics: dict[str, float],
        mission_hours: float = 168.0,
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
        the supplied mission window. The default remains 7 days
        for compatibility with existing callers.
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

        mission_hours = max(
            float(mission_hours),
            1.0,
        )

        darkness_fraction = min(
            max(longest_dark_hours / mission_hours, 0.0),
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

    def _refine_visibility_event(
        self,
        site: Site,
        body: str,
        before: AnalysisResult,
        after: AnalysisResult,
        iterations: int = 40,
    ) -> datetime:
        """
        Refine a visibility transition between two real SPICE samples.

        The surrounding timeline samples provide a bracket.  A binary
        search repeatedly evaluates the real SPICE visibility state at
        the midpoint until the transition is localized to sub-second
        precision.

        No interpolated/mock astronomical values are used.
        """

        before_time = before.time
        after_time = after.time

        before_visible = (
            before.sun.mission_visible
            if body == "SUN"
            else before.earth.mission_visible
        )

        after_visible = (
            after.sun.mission_visible
            if body == "SUN"
            else after.earth.mission_visible
        )

        if before_visible == after_visible:
            raise ValueError(
                "Event refinement requires a visibility transition."
            )

        low_time = before_time
        high_time = after_time

        for _ in range(iterations):
            midpoint = (
                low_time
                + (high_time - low_time) / 2
            )

            midpoint_result = self.analyze(
                site=site,
                analysis_time=midpoint,
            )

            midpoint_visible = (
                midpoint_result.sun.mission_visible
                if body == "SUN"
                else midpoint_result.earth.mission_visible
            )

            if midpoint_visible == before_visible:
                low_time = midpoint
            else:
                high_time = midpoint

        return (
            low_time
            + (high_time - low_time) / 2
        )

    def calculate_visibility_events(
        self,
        results: list[AnalysisResult],
        site: Site | None = None,
    ) -> list[dict[str, object]]:
        """
        Find every real Sun/Earth visibility transition in a timeline.

        Event definitions:
        - Sun Rise: False -> True
        - Sun Set: True -> False
        - Earth Contact: False -> True
        - Earth Contact Loss: True -> False

        Each sampled transition supplies a bracket. When a site is
        provided, the transition is refined with repeated real SPICE
        evaluations between the surrounding samples.

        No interpolation or mock astronomical values are used.
        """

        if not results:
            raise ValueError(
                "results must contain at least one analysis result."
            )

        events = []

        for current, next_result in zip(
            results,
            results[1:],
        ):
            sun_before = current.sun.mission_visible
            sun_after = next_result.sun.mission_visible

            if sun_before != sun_after:
                event_name = (
                    "Sun Rise"
                    if sun_after
                    else "Sun Set"
                )

                if site is not None:
                    event_time = self._refine_visibility_event(
                        site=site,
                        body="SUN",
                        before=current,
                        after=next_result,
                    )
                else:
                    event_time = next_result.time

                events.append(
                    {
                        "body": "Sun",
                        "event": event_name,
                        "time": event_time,
                        "hours_from_start": (
                            event_time - results[0].time
                        ).total_seconds() / 3600.0,
                    }
                )

            earth_before = current.earth.mission_visible
            earth_after = next_result.earth.mission_visible

            if earth_before != earth_after:
                event_name = (
                    "Earth Contact"
                    if earth_after
                    else "Earth Contact Loss"
                )

                if site is not None:
                    event_time = self._refine_visibility_event(
                        site=site,
                        body="EARTH",
                        before=current,
                        after=next_result,
                    )
                else:
                    event_time = next_result.time

                events.append(
                    {
                        "body": "Earth",
                        "event": event_name,
                        "time": event_time,
                        "hours_from_start": (
                            event_time - results[0].time
                        ).total_seconds() / 3600.0,
                    }
                )

        events.sort(key=lambda item: item["time"])

        return events

    def calculate_next_events(
        self,
        results: list[AnalysisResult],
        site: Site | None = None,
    ) -> dict[str, object | None]:
        """
        Identify the next real Sun and Earth visibility events
        from a real SPICE + LOLA mission timeline.

        Event definitions:
        - Sun Rise: visibility changes False -> True
        - Sun Set: visibility changes True -> False
        - Earth Contact: visibility changes False -> True
        - Earth Contact Loss: visibility changes True -> False

        A sampled transition first supplies a bracket. When a site is
        provided, the transition is then refined by repeated real-SPICE
        evaluations between the two surrounding samples.
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

                if site is not None:
                    event_time = self._refine_visibility_event(
                        site=site,
                        body="SUN",
                        before=current,
                        after=next_result,
                    )
                else:
                    event_time = next_result.time

                events["next_sun_event_time"] = event_time

                events["next_sun_countdown_hours"] = (
                    event_time - start_time
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

                if site is not None:
                    event_time = self._refine_visibility_event(
                        site=site,
                        body="EARTH",
                        before=current,
                        after=next_result,
                    )
                else:
                    event_time = next_result.time

                events["next_earth_event_time"] = event_time

                events["next_earth_countdown_hours"] = (
                    event_time - start_time
                ).total_seconds() / 3600.0

                break

        return events
