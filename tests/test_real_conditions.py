from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, os.getcwd())

from PySide6.QtWidgets import QApplication

from app.core.models import Site
from app.science.engine import LunarAnalysisEngine
from app.ui.analysis import AnalysisPage


def main():
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    print("=" * 60)
    print("REAL LANDING CONDITIONS TEST")
    print("=" * 60)

    engine = LunarAnalysisEngine()
    engine.load()

    try:
        site = Site(
            name="Shackleton Crater",
            latitude=-89.9,
            longitude=0.0,
        )

        analysis_time = datetime(
            2026,
            1,
            1,
            0,
            0,
            0,
            tzinfo=timezone.utc,
        )

        print()
        print("1. REAL SPICE + LOLA TIMELINE")
        print("-" * 60)

        series = engine.analyze_time_series(
            site=site,
            start_time=analysis_time,
            duration_hours=24.0,
            step_hours=6.0,
        )

        if not series:
            raise AssertionError(
                "Real analysis timeline returned no samples."
            )

        print(f"Samples: {len(series)}")

        print()
        print("2. REAL ENGINE METRICS")
        print("-" * 60)

        lighting = (
            engine.calculate_lighting_metrics(
                series
            )
        )

        communications = (
            engine.calculate_communications_metrics(
                series
            )
        )

        suitability = (
            engine.calculate_suitability_score(
                lighting_metrics=lighting,
                communications_metrics=communications,
            )
        )

        next_events = (
            engine.calculate_next_events(
                series
            )
        )

        print(
            "Illumination       : "
            f"{lighting['illumination_percent']:.6f}%"
        )

        print(
            "Longest dark       : "
            f"{lighting['longest_dark_hours']:.6f} h"
        )

        print(
            "Earth contact      : "
            f"{communications['contact_hours']:.6f} h"
        )

        print(
            "Contact percentage : "
            f"{communications['contact_percent']:.6f}%"
        )

        print(
            "Longest blackout   : "
            f"{communications['longest_blackout_hours']:.6f} h"
        )

        print(
            "Suitability        : "
            f"{suitability['score']:.6f}/100"
        )

        print()
        print("3. REAL RESULT CONTRACT")
        print("-" * 60)

        required_lighting = {
            "illumination_percent",
            "longest_dark_hours",
        }

        required_communications = {
            "contact_hours",
            "contact_percent",
            "longest_blackout_hours",
        }

        required_suitability = {
            "score",
            "illumination_points",
            "contact_points",
            "darkness_points",
        }

        if not required_lighting.issubset(
            lighting.keys()
        ):
            raise AssertionError(
                "Lighting metric contract is incomplete."
            )

        if not required_communications.issubset(
            communications.keys()
        ):
            raise AssertionError(
                "Communication metric contract is incomplete."
            )

        if not required_suitability.issubset(
            suitability.keys()
        ):
            raise AssertionError(
                "Suitability metric contract is incomplete."
            )

        if not 0.0 <= lighting[
            "illumination_percent"
        ] <= 100.0:
            raise AssertionError(
                "Illumination percentage is outside 0..100."
            )

        if not 0.0 <= communications[
            "contact_percent"
        ] <= 100.0:
            raise AssertionError(
                "Earth contact percentage is outside 0..100."
            )

        if not 0.0 <= suitability[
            "score"
        ] <= 100.0:
            raise AssertionError(
                "Suitability score is outside 0..100."
            )

        print("PASS: Real metric ranges are valid")

        print()
        print("4. ANALYSIS PAGE + LANDING CONDITIONS VIEW")
        print("-" * 60)

        page = AnalysisPage(engine=engine)

        production_results = {
            "site": {
                "name": series[0].site.name,
                "latitude": series[0].site.latitude,
                "longitude": series[0].site.longitude,
            },
            "time": series[0].time,
            "sun": {
                "elevation": series[0].sun.elevation,
                "azimuth": series[0].sun.azimuth,
                "visible": series[0].sun.visible,
                "status": series[0].sun.status,
                "terrain_horizon_elevation": (
                    series[0].sun.terrain_horizon_elevation
                ),
                "terrain_visible": (
                    series[0].sun.terrain_visible
                ),
                "terrain_status": (
                    series[0].sun.terrain_status
                ),
            },
            "earth": {
                "elevation": series[0].earth.elevation,
                "azimuth": series[0].earth.azimuth,
                "visible": series[0].earth.visible,
                "status": series[0].earth.status,
                "terrain_horizon_elevation": (
                    series[0].earth.terrain_horizon_elevation
                ),
                "terrain_visible": (
                    series[0].earth.terrain_visible
                ),
                "terrain_status": (
                    series[0].earth.terrain_status
                ),
            },
        }

        page.show_results(
            production_results
        )

        page.landing_conditions_view.set_metrics(
            lighting_metrics=lighting,
            communications_metrics=communications,
            suitability=suitability,
            next_events=next_events,
        )

        page.landing_conditions_view.show()
        app.processEvents()

        expected_score = (
            f"{suitability['score']:.2f}/100"
        )

        actual_score = (
            page.landing_conditions_view
            .suitability_value
            .text()
        )

        if actual_score != expected_score:
            raise AssertionError(
                "Suitability value was not propagated "
                "unchanged into the visualization."
            )

        expected_illumination = (
            f"{lighting['illumination_percent']:.2f}%"
        )

        actual_illumination = (
            page.landing_conditions_view
            .illumination_value
            .text()
        )

        if (
            actual_illumination
            != expected_illumination
        ):
            raise AssertionError(
                "Illumination value was not propagated "
                "unchanged into the visualization."
            )

        expected_contact = (
            f"{communications['contact_percent']:.2f}%"
        )

        actual_contact = (
            page.landing_conditions_view
            .contact_value
            .text()
        )

        if actual_contact != expected_contact:
            raise AssertionError(
                "Earth contact value was not propagated "
                "unchanged into the visualization."
            )

        print(
            "PASS: LandingConditionsView accepted "
            "real metric dictionaries"
        )

        print(
            "PASS: Real illumination value rendered"
        )

        print(
            "PASS: Real Earth contact value rendered"
        )

        print(
            "PASS: Real suitability value rendered"
        )

        print()
        print("5. WIDGET RENDER VALIDATION")
        print("-" * 60)

        if page.landing_conditions_view.width() <= 0:
            raise AssertionError(
                "LandingConditionsView has invalid width."
            )

        if page.landing_conditions_view.height() <= 0:
            raise AssertionError(
                "LandingConditionsView has invalid height."
            )

        print(
            "Rendered size: "
            f"{page.landing_conditions_view.width()}x"
            f"{page.landing_conditions_view.height()}"
        )

        print(
            "PASS: Landing Conditions widget rendered"
        )

        print()
        print("=" * 60)
        print("PHASE 4.3 REAL CONDITION TEST: PASS")
        print("=" * 60)

    finally:
        engine.unload()


if __name__ == "__main__":
    main()
