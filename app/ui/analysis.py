from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QGroupBox,
    QGridLayout,
    QScrollArea,
    QFileDialog,
)

from app.core.models import Site
from app.ui.time_series_plot import LunarTimeSeriesPlot
from app.ui.geometry_view import LunarGeometryView
from app.ui.condition_view import LandingConditionsView


class AnalysisPage(QWidget):

    def __init__(self, engine=None):
        super().__init__()

        self.engine = engine
        self.time_series_plot = None
        self.timeline_status = None

        self.setup_ui()

    def setup_ui(self):

        outer_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        main_layout = QVBoxLayout(content)

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        title = QLabel("Lunar Analysis")

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        subtitle = QLabel(
            "Detailed astronomical conditions for the selected lunar site."
        )

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # --------------------------------------------------
        # Sun and Earth panels
        # --------------------------------------------------

        celestial_layout = QHBoxLayout()

        # --------------------------------------------------
        # Sun
        # --------------------------------------------------

        sun_group = QGroupBox("Sun")

        sun_layout = QGridLayout()

        sun_layout.addWidget(
            QLabel("Elevation:"), 0, 0
        )

        self.sun_elevation = QLabel("--")

        sun_layout.addWidget(
            self.sun_elevation, 0, 1
        )

        sun_layout.addWidget(
            QLabel("Azimuth:"), 1, 0
        )

        self.sun_azimuth = QLabel("--")

        sun_layout.addWidget(
            self.sun_azimuth, 1, 1
        )

        sun_layout.addWidget(
            QLabel("Geometric Status:"), 2, 0
        )

        self.sun_status = QLabel("--")

        sun_layout.addWidget(
            self.sun_status, 2, 1
        )

        sun_layout.addWidget(
            QLabel("Terrain Horizon:"), 3, 0
        )

        self.sun_terrain_horizon = QLabel("--")

        sun_layout.addWidget(
            self.sun_terrain_horizon, 3, 1
        )

        sun_layout.addWidget(
            QLabel("Terrain Visibility:"), 4, 0
        )

        self.sun_terrain_visibility = QLabel("--")

        sun_layout.addWidget(
            self.sun_terrain_visibility, 4, 1
        )

        sun_group.setLayout(sun_layout)

        # --------------------------------------------------
        # Earth
        # --------------------------------------------------

        earth_group = QGroupBox("Earth")

        earth_layout = QGridLayout()

        earth_layout.addWidget(
            QLabel("Elevation:"), 0, 0
        )

        self.earth_elevation = QLabel("--")

        earth_layout.addWidget(
            self.earth_elevation, 0, 1
        )

        earth_layout.addWidget(
            QLabel("Azimuth:"), 1, 0
        )

        self.earth_azimuth = QLabel("--")

        earth_layout.addWidget(
            self.earth_azimuth, 1, 1
        )

        earth_layout.addWidget(
            QLabel("Geometric Status:"), 2, 0
        )

        self.earth_status = QLabel("--")

        earth_layout.addWidget(
            self.earth_status, 2, 1
        )

        earth_layout.addWidget(
            QLabel("Terrain Horizon:"), 3, 0
        )

        self.earth_terrain_horizon = QLabel("--")

        earth_layout.addWidget(
            self.earth_terrain_horizon, 3, 1
        )

        earth_layout.addWidget(
            QLabel("Terrain Visibility:"), 4, 0
        )

        self.earth_terrain_visibility = QLabel("--")

        earth_layout.addWidget(
            self.earth_terrain_visibility, 4, 1
        )

        earth_group.setLayout(earth_layout)

        celestial_layout.addWidget(sun_group)
        celestial_layout.addWidget(earth_group)

        main_layout.addLayout(celestial_layout)

        # --------------------------------------------------
        # Visibility
        # --------------------------------------------------

        visibility_group = QGroupBox("Visibility")

        visibility_layout = QHBoxLayout()

        sun_visibility_layout = QVBoxLayout()

        sun_visibility_title = QLabel("Sun Visibility")

        self.sun_visibility = QLabel("--")

        self.sun_visibility.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        sun_visibility_layout.addWidget(
            sun_visibility_title
        )

        sun_visibility_layout.addWidget(
            self.sun_visibility
        )

        earth_visibility_layout = QVBoxLayout()

        earth_visibility_title = QLabel(
            "Earth Visibility"
        )

        self.earth_visibility = QLabel("--")

        self.earth_visibility.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        earth_visibility_layout.addWidget(
            earth_visibility_title
        )

        earth_visibility_layout.addWidget(
            self.earth_visibility
        )

        visibility_layout.addLayout(
            sun_visibility_layout
        )

        visibility_layout.addLayout(
            earth_visibility_layout
        )

        visibility_group.setLayout(
            visibility_layout
        )

        main_layout.addWidget(
            visibility_group
        )

        # --------------------------------------------------
        # Local Lunar Horizon Geometry
        # --------------------------------------------------

        geometry_group = QGroupBox(
            "Local Lunar Horizon Geometry"
        )

        geometry_layout = QVBoxLayout()

        geometry_description = QLabel(
            "Real SPICE-derived Sun/Earth direction at the "
            "selected lunar site. The diagram shows local "
            "azimuth and elevation; terrain visibility uses "
            "the existing LOLA horizon calculation."
        )

        geometry_description.setWordWrap(True)

        geometry_layout.addWidget(
            geometry_description
        )

        self.geometry_view = LunarGeometryView()

        geometry_layout.addWidget(
            self.geometry_view
        )

        geometry_group.setLayout(
            geometry_layout
        )

        main_layout.addWidget(
            geometry_group
        )

        # --------------------------------------------------
        # Landing Conditions
        # --------------------------------------------------

        conditions_group = QGroupBox(
            "Landing Conditions"
        )

        conditions_layout = QVBoxLayout()

        conditions_description = QLabel(
            "Real terrain-aware mission conditions calculated "
            "from the selected timeline using SPICE and LOLA."
        )

        conditions_description.setWordWrap(True)

        conditions_layout.addWidget(
            conditions_description
        )

        self.landing_conditions_view = (
            LandingConditionsView()
        )

        conditions_layout.addWidget(
            self.landing_conditions_view
        )

        conditions_group.setLayout(
            conditions_layout
        )

        main_layout.addWidget(
            conditions_group
        )

        # --------------------------------------------------
        # Analysis status
        # --------------------------------------------------

        status_group = QGroupBox(
            "Analysis Status"
        )

        status_layout = QVBoxLayout()

        self.status_label = QLabel(
            "No analysis has been performed yet."
        )

        status_layout.addWidget(
            self.status_label
        )

        status_group.setLayout(
            status_layout
        )

        main_layout.addWidget(
            status_group
        )

        # --------------------------------------------------
        # Real Mission Timeline
        # --------------------------------------------------

        timeline_group = QGroupBox(
            "Real Mission Timeline"
        )

        timeline_layout = QVBoxLayout()

        # Timeline controls
        timeline_controls = QHBoxLayout()

        duration_label = QLabel("Duration:")

        self.timeline_duration_combo = QComboBox()
        self.timeline_duration_combo.addItem(
            "24 Hours", 24.0
        )
        self.timeline_duration_combo.addItem(
            "7 Days", 168.0
        )
        self.timeline_duration_combo.addItem(
            "Lunar Month", 27.321661 * 24.0
        )
        self.timeline_duration_combo.setCurrentIndex(1)

        sampling_label = QLabel("Sampling:")

        self.timeline_sampling_combo = QComboBox()
        self.timeline_sampling_combo.addItem(
            "1 Hour", 1.0
        )
        self.timeline_sampling_combo.addItem(
            "6 Hours", 6.0
        )
        self.timeline_sampling_combo.setCurrentIndex(1)

        self.update_timeline_button = QPushButton(
            "Update Timeline"
        )
        self.update_timeline_button.clicked.connect(
            self._refresh_timeline_from_current_analysis
        )

        timeline_controls.addWidget(
            duration_label
        )
        timeline_controls.addWidget(
            self.timeline_duration_combo
        )
        timeline_controls.addSpacing(20)
        timeline_controls.addWidget(
            sampling_label
        )
        timeline_controls.addWidget(
            self.timeline_sampling_combo
        )
        timeline_controls.addWidget(
            self.update_timeline_button
        )

        self.export_csv_button = QPushButton(
            "Export CSV"
        )
        self.export_csv_button.clicked.connect(
            self.export_timeline_csv
        )

        timeline_controls.addWidget(
            self.export_csv_button
        )

        self.export_pdf_button = QPushButton(
            "Export PDF"
        )
        self.export_pdf_button.clicked.connect(
            self.export_timeline_pdf
        )

        timeline_controls.addWidget(
            self.export_pdf_button
        )

        timeline_controls.addStretch()

        timeline_layout.addLayout(
            timeline_controls
        )

        self.timeline_status = QLabel(
            "Run an analysis to calculate the real timeline."
        )

        timeline_layout.addWidget(
            self.timeline_status
        )

        lighting_metrics_layout = QHBoxLayout()

        self.illumination_label = QLabel(
            "Illumination: --"
        )

        self.longest_dark_period_label = QLabel(
            "Longest Dark Period: --"
        )

        self.contact_hours_label = QLabel(
            "Earth Contact: --"
        )

        self.contact_percent_label = QLabel(
            "Contact: --"
        )

        self.longest_blackout_label = QLabel(
            "Longest Earth Blackout: --"
        )

        self.suitability_score_label = QLabel(
            "Suitability Score: --/100"
        )

        self.suitability_components_label = QLabel(
            "Suitability: Illumination --/40 | "
            "Contact --/35 | Darkness --/25"
        )

        self.next_sun_event_label = QLabel(
            "Next Sun Event: --"
        )

        self.next_earth_event_label = QLabel(
            "Next Earth Event: --"
        )

        lighting_metrics_layout.addWidget(
            self.illumination_label
        )

        lighting_metrics_layout.addSpacing(30)

        lighting_metrics_layout.addWidget(
            self.longest_dark_period_label
        )

        lighting_metrics_layout.addWidget(
            self.contact_hours_label
        )

        lighting_metrics_layout.addWidget(
            self.contact_percent_label
        )

        lighting_metrics_layout.addWidget(
            self.longest_blackout_label
        )

        lighting_metrics_layout.addWidget(
            self.suitability_score_label
        )

        lighting_metrics_layout.addWidget(
            self.suitability_components_label
        )

        lighting_metrics_layout.addWidget(
            self.next_sun_event_label
        )

        lighting_metrics_layout.addWidget(
            self.next_earth_event_label
        )

        lighting_metrics_layout.addStretch()

        timeline_layout.addLayout(
            lighting_metrics_layout
        )

        self.time_series_plot = LunarTimeSeriesPlot()

        timeline_layout.addWidget(
            self.time_series_plot
        )

        timeline_group.setLayout(
            timeline_layout
        )

        main_layout.addWidget(
            timeline_group
        )

        main_layout.addStretch()

        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)

    # ------------------------------------------------------
    # Display analysis results
    # ------------------------------------------------------

    def show_results(self, results):

        sun = results["sun"]
        earth = results["earth"]

        self.sun_elevation.setText(
            f'{sun["elevation"]:.2f}°'
        )

        self.sun_azimuth.setText(
            f'{sun["azimuth"]:.2f}°'
        )

        self.sun_status.setText(
            sun["status"]
        )

        self.earth_elevation.setText(
            f'{earth["elevation"]:.2f}°'
        )

        self.earth_azimuth.setText(
            f'{earth["azimuth"]:.2f}°'
        )

        self.earth_status.setText(
            earth["status"]
        )

        sun_horizon = sun.get(
            "terrain_horizon_elevation"
        )

        if sun_horizon is None:
            self.sun_terrain_horizon.setText(
                "Unavailable"
            )
        else:
            self.sun_terrain_horizon.setText(
                f'{sun_horizon:.2f}°'
            )

        sun_terrain_visible = sun.get(
            "terrain_visible"
        )

        if sun_terrain_visible is None:
            self.sun_terrain_visibility.setText(
                "Unavailable"
            )
        else:
            self.sun_terrain_visibility.setText(
                "Terrain Clear"
                if sun_terrain_visible
                else "Terrain Blocked"
            )

        earth_horizon = earth.get(
            "terrain_horizon_elevation"
        )

        if earth_horizon is None:
            self.earth_terrain_horizon.setText(
                "Unavailable"
            )
        else:
            self.earth_terrain_horizon.setText(
                f'{earth_horizon:.2f}°'
            )

        earth_terrain_visible = earth.get(
            "terrain_visible"
        )

        if earth_terrain_visible is None:
            self.earth_terrain_visibility.setText(
                "Unavailable"
            )
        else:
            self.earth_terrain_visibility.setText(
                "Terrain Clear"
                if earth_terrain_visible
                else "Terrain Blocked"
            )

        sun_mission_visible = (
            sun["terrain_visible"]
            if sun.get("terrain_visible") is not None
            else sun["visible"]
        )

        earth_mission_visible = (
            earth["terrain_visible"]
            if earth.get("terrain_visible") is not None
            else earth["visible"]
        )

        self.sun_visibility.setText(
            "Mission: Visible"
            if sun_mission_visible
            else "Mission: Blocked by Terrain"
        )

        self.earth_visibility.setText(
            "Mission: Visible"
            if earth_mission_visible
            else "Mission: Blocked by Terrain"
        )

        self.status_label.setText(
            f'Analysis results loaded for {results["site"]["name"]}. '
            f'Analysis time: {results["time"].strftime("%Y-%m-%d %H:%M:%S UTC")}.'
        )

        self.geometry_view.set_geometry(
            sun,
            earth,
        )

        self._current_analysis_results = results
        self.update_time_series(results)

    def _refresh_timeline_from_current_analysis(self):
        """Recalculate the timeline using the current analysis result."""

        if self.engine is None:
            self.timeline_status.setText(
                "Timeline unavailable: analysis engine not connected."
            )
            return

        if not hasattr(self, "_current_analysis_results"):
            self.timeline_status.setText(
                "Run an analysis before updating the timeline."
            )
            return

        self.update_time_series(
            self._current_analysis_results
        )

    def export_timeline_csv(self):
        """Export the currently displayed real mission timeline as CSV."""

        if not hasattr(self, "_current_timeline_series"):
            self.timeline_status.setText(
                "CSV export unavailable: run or update the timeline first."
            )
            return

        series = self._current_timeline_series

        if not series:
            self.timeline_status.setText(
                "CSV export unavailable: timeline contains no samples."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Mission Timeline CSV",
            "lunar_mission_timeline.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        import csv

        fieldnames = [
            "utc_time",
            "sun_elevation_deg",
            "sun_azimuth_deg",
            "sun_geometric_visible",
            "sun_terrain_horizon_deg",
            "sun_terrain_visible",
            "sun_mission_visible",
            "earth_elevation_deg",
            "earth_azimuth_deg",
            "earth_geometric_visible",
            "earth_terrain_horizon_deg",
            "earth_terrain_visible",
            "earth_mission_visible",
        ]

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for result in series:
                writer.writerow(
                    {
                        "utc_time": result.time.strftime(
                            "%Y-%m-%d %H:%M:%S UTC"
                        ),
                        "sun_elevation_deg": (
                            f"{result.sun.elevation:.6f}"
                        ),
                        "sun_azimuth_deg": (
                            f"{result.sun.azimuth:.6f}"
                        ),
                        "sun_geometric_visible": (
                            result.sun.visible
                        ),
                        "sun_terrain_horizon_deg": (
                            ""
                            if result.sun.terrain_horizon_elevation
                            is None
                            else f"{result.sun.terrain_horizon_elevation:.6f}"
                        ),
                        "sun_terrain_visible": (
                            ""
                            if result.sun.terrain_visible is None
                            else result.sun.terrain_visible
                        ),
                        "sun_mission_visible": (
                            result.sun.mission_visible
                        ),
                        "earth_elevation_deg": (
                            f"{result.earth.elevation:.6f}"
                        ),
                        "earth_azimuth_deg": (
                            f"{result.earth.azimuth:.6f}"
                        ),
                        "earth_geometric_visible": (
                            result.earth.visible
                        ),
                        "earth_terrain_horizon_deg": (
                            ""
                            if result.earth.terrain_horizon_elevation
                            is None
                            else f"{result.earth.terrain_horizon_elevation:.6f}"
                        ),
                        "earth_terrain_visible": (
                            ""
                            if result.earth.terrain_visible is None
                            else result.earth.terrain_visible
                        ),
                        "earth_mission_visible": (
                            result.earth.mission_visible
                        ),
                    }
                )

        self.timeline_status.setText(
            f"CSV exported: {len(series)} samples to "
            f"{file_path}"
        )

    def export_timeline_pdf(self):
        """Export the currently displayed real mission timeline as PDF."""

        if not hasattr(self, "_current_timeline_series"):
            self.timeline_status.setText(
                "PDF export unavailable: run or update the timeline first."
            )
            return

        series = self._current_timeline_series

        if not series:
            self.timeline_status.setText(
                "PDF export unavailable: timeline contains no samples."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Mission Timeline PDF",
            "lunar_mission_timeline.pdf",
            "PDF Files (*.pdf)",
        )

        if not file_path:
            return

        from pathlib import Path

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
            Image,
        )

        site = series[0].site
        start_time = series[0].time

        duration_hours = (
            series[-1].time - start_time
        ).total_seconds() / 3600.0

        # Keep the selected display timeline for the PDF graph/table.
        # Mission metrics and suitability use a full lunar-month
        # assessment window so a short display window cannot inflate
        # the mission score.
        mission_duration_hours = 29.5 * 24.0

        metric_series = self.engine.analyze_time_series(
            site=site,
            start_time=start_time,
            duration_hours=mission_duration_hours,
            step_hours=1.0,
        )

        lighting_metrics = (
            self.engine.calculate_lighting_metrics(
                metric_series
            )
        )

        communications_metrics = (
            self.engine.calculate_communications_metrics(
                metric_series
            )
        )

        suitability = (
            self.engine.calculate_suitability_score(
                lighting_metrics=lighting_metrics,
                communications_metrics=communications_metrics,
                mission_hours=mission_duration_hours,
            )
        )

        next_events = (
            self.engine.calculate_next_events_extended(
                site=site,
                start_time=start_time,
                initial_results=metric_series,
            )
        )

        # Report every terrain-aware Sun/Earth visibility transition
        # across the complete 29.5-day assessment window.
        # Transition times are refined by the engine from real
        # SPICE + LOLA evaluations; no interpolation is used here.
        visibility_events = self.engine.calculate_visibility_events(
            metric_series,
            site=site,
        )

        terrain_available = any(
            result.sun.terrain_horizon_elevation is not None
            or result.earth.terrain_horizon_elevation is not None
            for result in series
        )

        if terrain_available:
            terrain_status_text = (
                "LOLA terrain available; terrain-aware visibility applied."
            )
            suitability_score_text = (
                f"{suitability['score']:.2f}/100"
            )
            sun_mission_header = "Sun Mission"
            earth_mission_header = "Earth Mission"
        else:
            terrain_status_text = (
                "Terrain horizon mask unavailable for this location. "
                "Visibility is geometric only. "
                "Terrain masks available for: Shackleton Crater, "
                "Cabeus Crater, Malapert Massif."
            )
            suitability_score_text = (
                f"{suitability['score']:.2f}/100 "
                "(provisional — no terrain data)"
            )
            sun_mission_header = "Sun Mission (geometric)"
            earth_mission_header = "Earth Mission (geometric)"

        sampling_hours = (
            (series[1].time - series[0].time).total_seconds()
            / 3600.0
            if len(series) > 1
            else 0.0
        )

        document = SimpleDocTemplate(
            file_path,
            pagesize=landscape(A4),
            rightMargin=12 * mm,
            leftMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
        )

        styles = getSampleStyleSheet()

        story = []

        story.append(
            Paragraph(
                "Lunar Landing Site Navigator",
                styles["Title"],
            )
        )

        story.append(
            Paragraph(
                "Real SPICE + LOLA Mission Timeline Report",
                styles["Heading2"],
            )
        )

        story.append(Spacer(1, 6 * mm))

        summary_data = [
            ["Landing Site", site.name],
            [
                "Coordinates",
                f"{site.latitude:.4f}°, "
                f"{site.longitude:.4f}°",
            ],
            [
                "Timeline view",
                f"{series[0].time.strftime('%Y-%m-%d %H:%M UTC')} "
                f"to "
                f"{series[-1].time.strftime('%Y-%m-%d %H:%M UTC')} "
                f"({duration_hours:.0f} hours)",
            ],
            [
                "Display sampling",
                f"{sampling_hours:.2f} hours",
            ],
            [
                "Display samples",
                str(len(series)),
            ],
            [
                "Metrics window",
                f"29.5 days ({mission_duration_hours:.0f} hours)",
            ],
            [
                "Metrics sampling",
                "1.00 hour",
            ],
            [
                "Metrics samples",
                str(len(metric_series)),
            ],
        ]

        summary_table = Table(
            summary_data,
            colWidths=[45 * mm, 105 * mm],
        )

        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        story.append(summary_table)
        story.append(Spacer(1, 6 * mm))

        # ------------------------------------------------------------------
        # Landing Site Coordinates + Lunar Horizon Geometry
        #
        # Geometry is taken directly from the first real SPICE + LOLA
        # AnalysisResult in the selected timeline.  No separate/mock
        # astronomical values are generated for the PDF.
        # ------------------------------------------------------------------

        geometry_result = series[0]

        from app.data.sites import LANDING_SITE_HEIGHTS_KM

        site_height_km = LANDING_SITE_HEIGHTS_KM.get(
            site.name,
            None,
        )

        landing_coordinates_data = [
            ["Parameter", "Value"],
            ["Landing Site", site.name],
            [
                "Latitude",
                f"{site.latitude:.6f}°",
            ],
            [
                "Longitude",
                f"{site.longitude:.6f}°",
            ],
            [
                "Site Elevation",
                (
                    f"{site_height_km:.6f} km"
                    if site_height_km is not None
                    else "Unavailable"
                ),
            ],
        ]

        landing_coordinates_table = Table(
            landing_coordinates_data,
            colWidths=[55 * mm, 75 * mm],
        )

        landing_coordinates_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        story.append(
            Paragraph(
                "Landing Site Coordinates",
                styles["Heading2"],
            )
        )

        story.append(landing_coordinates_table)
        story.append(Spacer(1, 5 * mm))

        sun_geometry = geometry_result.sun
        earth_geometry = geometry_result.earth

        def terrain_clearance(result):
            if result.terrain_horizon_elevation is None:
                return None

            return (
                result.elevation
                - result.terrain_horizon_elevation
            )

        def visibility_text(result):
            mission_visible = result.mission_visible

            if result.terrain_visible is not None:
                return (
                    "Visible"
                    if mission_visible
                    else "Blocked by terrain"
                )

            return (
                "Visible"
                if mission_visible
                else "Below geometric horizon"
            )

        sun_clearance = terrain_clearance(sun_geometry)
        earth_clearance = terrain_clearance(earth_geometry)

        horizon_geometry_data = [
            [
                "Body",
                "Azimuth (°)",
                "Elevation (°)",
                "LOLA Horizon (°)",
                "Clearance (°)",
                "Mission Visibility",
            ],
            [
                "Sun",
                f"{sun_geometry.azimuth:.4f}",
                f"{sun_geometry.elevation:.4f}",
                (
                    f"{sun_geometry.terrain_horizon_elevation:.4f}"
                    if sun_geometry.terrain_horizon_elevation is not None
                    else "Unavailable"
                ),
                (
                    f"{sun_clearance:.4f}"
                    if sun_clearance is not None
                    else "Unavailable"
                ),
                visibility_text(sun_geometry),
            ],
            [
                "Earth",
                f"{earth_geometry.azimuth:.4f}",
                f"{earth_geometry.elevation:.4f}",
                (
                    f"{earth_geometry.terrain_horizon_elevation:.4f}"
                    if earth_geometry.terrain_horizon_elevation is not None
                    else "Unavailable"
                ),
                (
                    f"{earth_clearance:.4f}"
                    if earth_clearance is not None
                    else "Unavailable"
                ),
                visibility_text(earth_geometry),
            ],
        ]

        horizon_geometry_table = Table(
            horizon_geometry_data,
            repeatRows=1,
            colWidths=[
                22 * mm,
                27 * mm,
                27 * mm,
                32 * mm,
                30 * mm,
                48 * mm,
            ],
        )

        horizon_geometry_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 1), (-2, -1), "CENTER"),
                ]
            )
        )

        story.append(
            Paragraph(
                "Lunar Horizon Geometry",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                "The geometry below is taken from the first real "
                "SPICE + LOLA timeline sample at "
                f"{geometry_result.time.strftime('%Y-%m-%d %H:%M:%S UTC')}. "
                "Azimuth is measured clockwise from lunar north. "
                "Terrain clearance is the SPICE-derived body-center "
                "elevation minus the LOLA terrain-horizon elevation "
                "at the body's computed azimuth.",
                styles["Normal"],
            )
        )

        story.append(horizon_geometry_table)
        story.append(Spacer(1, 5 * mm))

        story.append(
            Paragraph(
                "A positive terrain clearance indicates that the "
                "body center is above the modeled local terrain "
                "horizon at that azimuth. A negative clearance "
                "indicates terrain obstruction. This is a "
                "terrain-aware geometric model and does not apply "
                "lunar-limb, atmospheric, or refraction corrections.",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 6 * mm))

        metrics_data = [
            ["Metric", "Value"],
            [
                "Illumination",
                f"{lighting_metrics['illumination_percent']:.2f}%",
            ],
            [
                "Longest Dark Period",
                f"{lighting_metrics['longest_dark_hours']:.0f} h (±1 h)",
            ],
            [
                "Earth Contact",
                f"{communications_metrics['contact_hours']:.0f} h (±1 h)",
            ],
            [
                "Earth Contact Percentage",
                f"{communications_metrics['contact_percent']:.2f}%",
            ],
            [
                "Longest Earth Blackout",
                f"{communications_metrics['longest_blackout_hours']:.0f} h "
                f"(±1 h)",
            ],
            [
                "Suitability Score",
                suitability_score_text,
            ],
            [
                "Illumination Points",
                f"{suitability['illumination_points']:.2f}/40",
            ],
            [
                "Contact Points",
                f"{suitability['contact_points']:.2f}/35",
            ],
            [
                "Darkness Points",
                f"{suitability['darkness_points']:.2f}/25",
            ],
        ]

        metrics_table = Table(
            metrics_data,
            colWidths=[70 * mm, 50 * mm],
        )

        metrics_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        story.append(
            Paragraph(
                "Mission Metrics",
                styles["Heading2"],
            )
        )
        story.append(metrics_table)
        story.append(Spacer(1, 6 * mm))

        events_data = [
            [
                "UTC",
                "Body",
                "Event",
                "Hours from assessment start",
            ]
        ]

        if visibility_events:
            for event in visibility_events:
                events_data.append(
                    [
                        event["time"].strftime(
                            "%Y-%m-%d %H:%M:%S UTC"
                        ),
                        str(event["body"]),
                        str(event["event"]),
                        f"{event['hours_from_start']:.0f} h "
                        f"(±1 h sample bracket)",
                    ]
                )
        else:
            events_data.append(
                [
                    "—",
                    "—",
                    "No terrain-aware visibility transitions",
                    "—",
                ]
            )

        events_table = Table(
            events_data,
            repeatRows=1,
            colWidths=[
                48 * mm,
                25 * mm,
                65 * mm,
                42 * mm,
            ],
        )

        events_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ]
            )
        )

        story.append(
            Paragraph(
                "Mission Events — 29.5-Day Assessment Window",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                "Events are detected from terrain-aware mission visibility "
                "transitions in the hourly real SPICE + LOLA assessment "
                "series. Transition times are refined from the surrounding "
                "hourly bracket using repeated real SPICE evaluations; "
                "no interpolated or mocked astronomical values are used.",
                styles["Normal"],
            )
        )

        story.append(events_table)
        story.append(Spacer(1, 6 * mm))

        story.append(
            Paragraph(
                "Suitability Method",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                "Suitability = 40% illumination + 35% Earth contact "
                "+ 25% darkness. Darkness contribution is based on "
                "1 − (longest dark period / 708-hour metrics window), "
                "bounded to the range 0–1. The assessment window is "
                "29.5 days and is sampled at 1-hour intervals.",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 4 * mm))

        story.append(
            Paragraph(
                "Terrain-Aware Visibility Model",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                "Mission visibility compares the SPICE-derived "
                "body-center elevation with the LOLA terrain horizon "
                "elevation at the body's computed azimuth. No lunar "
                "limb correction or atmospheric/refraction correction "
                "is applied. Therefore, a body center can remain "
                "geometrically above 0° while being blocked by terrain, "
                "or can be visible with a center below 0° where the "
                "terrain horizon is lower.",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 6 * mm))

        # Generate the real mission timeline graph from the same
        # SPICE + LOLA timeline series used by the analysis UI.
        graph_path = (
            Path(file_path).with_suffix(".timeline.png")
        )

        import matplotlib

        matplotlib.use("Agg")

        import matplotlib.pyplot as plt

        timeline_times = [
            result.time
            for result in series
        ]

        sun_elevation = [
            result.sun.elevation
            for result in series
        ]

        earth_elevation = [
            result.earth.elevation
            for result in series
        ]

        sun_horizon = [
            (
                result.sun.terrain_horizon_elevation
                if result.sun.terrain_horizon_elevation is not None
                else float("nan")
            )
            for result in series
        ]

        earth_horizon = [
            (
                result.earth.terrain_horizon_elevation
                if result.earth.terrain_horizon_elevation is not None
                else float("nan")
            )
            for result in series
        ]

        figure, axis = plt.subplots(
            figsize=(11, 5.5)
        )

        axis.plot(
            timeline_times,
            sun_elevation,
            label="Sun Elevation",
            linewidth=1.8,
        )

        axis.plot(
            timeline_times,
            earth_elevation,
            label="Earth Elevation",
            linewidth=1.8,
        )

        has_sun_horizon = any(
            result.sun.terrain_horizon_elevation is not None
            for result in series
        )

        has_earth_horizon = any(
            result.earth.terrain_horizon_elevation is not None
            for result in series
        )

        if has_sun_horizon:
            axis.plot(
                timeline_times,
                sun_horizon,
                label="Sun Terrain Horizon",
                linestyle="--",
                linewidth=1.3,
            )

        if has_earth_horizon:
            axis.plot(
                timeline_times,
                earth_horizon,
                label="Earth Terrain Horizon",
                linestyle="--",
                linewidth=1.3,
            )

        axis.axhline(
            0.0,
            linestyle=":",
            linewidth=1.0,
            label="Geometric Horizon (0°)",
        )

        axis.set_title(
            f"{site.name} — "
            f"{site.latitude:.4f}°, {site.longitude:.4f}° — "
            f"Real Lunar Mission Timeline ({duration_hours:.0f}-Hour View)"
        )

        axis.set_xlabel("UTC Time")
        axis.set_ylabel("Elevation (degrees)")
        axis.grid(True, alpha=0.3)
        axis.legend(loc="best")

        figure.autofmt_xdate()
        figure.tight_layout()

        figure.savefig(
            graph_path,
            dpi=180,
            bbox_inches="tight",
        )

        plt.close(figure)

        story.append(
            Paragraph(
                f"Mission Timeline Graph — {duration_hours:.0f}-Hour Display View",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                "The graph uses the selected display timeline "
                f"({duration_hours:.0f} hours at {sampling_hours:.2f}-hour "
                "sampling). Mission metrics and visibility events are "
                "calculated independently over the full 29.5-day "
                "assessment window at 1-hour sampling.",
                styles["Normal"],
            )
        )

        graph_image = Image(
            str(graph_path),
            width=245 * mm,
            height=112 * mm,
        )

        story.append(graph_image)

        story.append(PageBreak())

        story.append(
            Paragraph(
                "Mission Timeline Data",
                styles["Heading2"],
            )
        )

        timeline_data = [
            [
                "UTC",
                "Sun Elevation (°)",
                "Sun Azimuth (°)",
                "Sun Horizon (°)",
                sun_mission_header,
                "Earth Elevation (°)",
                "Earth Azimuth (°)",
                "Earth Horizon (°)",
                earth_mission_header,
            ]
        ]

        for result in series:
            sun_horizon = (
                "Unavailable"
                if result.sun.terrain_horizon_elevation is None
                else f"{result.sun.terrain_horizon_elevation:.2f}"
            )

            earth_horizon = (
                "Unavailable"
                if result.earth.terrain_horizon_elevation is None
                else f"{result.earth.terrain_horizon_elevation:.2f}"
            )

            timeline_data.append(
                [
                    result.time.strftime("%Y-%m-%d %H:%M"),
                    f"{result.sun.elevation:.2f}",
                    f"{result.sun.azimuth:.2f}",
                    sun_horizon,
                    (
                        "VISIBLE"
                        if result.sun.mission_visible
                        else "BLOCKED"
                    ),
                    f"{result.earth.elevation:.2f}",
                    f"{result.earth.azimuth:.2f}",
                    earth_horizon,
                    (
                        "VISIBLE"
                        if result.earth.mission_visible
                        else "BLOCKED"
                    ),
                ]
            )

        timeline_table = Table(
            timeline_data,
            repeatRows=1,
            colWidths=[
                28 * mm,
                15 * mm,
                15 * mm,
                20 * mm,
                22 * mm,
                17 * mm,
                15 * mm,
                20 * mm,
                22 * mm,
            ],
        )

        timeline_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                        colors.white,
                        colors.whitesmoke,
                    ]),
                ]
            )
        )

        story.append(timeline_table)

        story.append(Spacer(1, 5 * mm))

        story.append(
            Paragraph(
                f"Science source: real SPICE ephemeris calculations. "
                f"{terrain_status_text} "
                "The graph and timeline table use the display timeline; "
                "suitability metrics and mission-event assessment use "
                "the separate 29.5-day (708-hour), 1-hour series.",
                styles["Normal"],
            )
        )

        document.build(story)

        if graph_path.exists():
            graph_path.unlink()

        self.timeline_status.setText(
            f"PDF exported: {len(series)} samples to "
            f"{file_path}"
        )

    def update_time_series(self, results):
        """Calculate and display the real mission timeline."""

        if self.engine is None:
            self.timeline_status.setText(
                "Timeline unavailable: analysis engine not connected."
            )
            self.time_series_plot.clear()
            return

        site_data = results["site"]

        site = Site(
            name=site_data["name"],
            latitude=site_data["latitude"],
            longitude=site_data["longitude"],
        )

        start_time = results["time"]

        duration_hours = float(
            self.timeline_duration_combo.currentData()
        )

        step_hours = float(
            self.timeline_sampling_combo.currentData()
        )

        # Keep the user-selected timeline for the graph/table.
        series = self.engine.analyze_time_series(
            site=site,
            start_time=start_time,
            duration_hours=duration_hours,
            step_hours=step_hours,
        )

        self._current_timeline_series = series

        # Calculate mission metrics at hourly resolution so their
        # precision is independent of the display sampling interval.
        metric_series = self.engine.analyze_time_series(
            site=site,
            start_time=start_time,
            duration_hours=duration_hours,
            step_hours=1.0,
        )

        duration_text = (
            self.timeline_duration_combo.currentText()
        )

        plot_title = (
            "Lunar Month Mission Timeline"
            if duration_text == "Lunar Month"
            else f"{duration_text} Mission Timeline"
        )

        self.time_series_plot.plot(
            series,
            title=plot_title,
        )

        sampling_text = (
            self.timeline_sampling_combo.currentText()
        )

        lighting_metrics = (
            self.engine.calculate_lighting_metrics(
                metric_series
            )
        )

        self.illumination_label.setText(
            f"Illumination: "
            f"{lighting_metrics['illumination_percent']:.2f}%"
        )

        self.longest_dark_period_label.setText(
            f"Longest Dark Period: "
            f"{lighting_metrics['longest_dark_hours']:.2f} hours"
        )

        communications_metrics = (
            self.engine.calculate_communications_metrics(
                metric_series
            )
        )

        self.contact_hours_label.setText(
            f"Earth Contact: "
            f"{communications_metrics['contact_hours']:.2f} hours"
        )

        self.contact_percent_label.setText(
            f"Contact: "
            f"{communications_metrics['contact_percent']:.2f}%"
        )

        self.longest_blackout_label.setText(
            f"Longest Earth Blackout: "
            f"{communications_metrics['longest_blackout_hours']:.2f} hours"
        )

        suitability = (
            self.engine.calculate_suitability_score(
                lighting_metrics=lighting_metrics,
                communications_metrics=communications_metrics,
            )
        )

        self.suitability_score_label.setText(
            f"Suitability Score: "
            f"{suitability['score']:.2f}/100"
        )

        self.suitability_components_label.setText(
            f"Suitability: "
            f"Illumination {suitability['illumination_points']:.2f}/40 | "
            f"Contact {suitability['contact_points']:.2f}/35 | "
            f"Darkness {suitability['darkness_points']:.2f}/25"
        )

        next_events = (
            self.engine.calculate_next_events_extended(
                site=site,
                start_time=start_time,
                initial_results=metric_series,
            )
        )

        self.landing_conditions_view.set_metrics(
            lighting_metrics=lighting_metrics,
            communications_metrics=communications_metrics,
            suitability=suitability,
            next_events=next_events,
        )

        sun_event = next_events["next_sun_event"]
        sun_event_time = next_events["next_sun_event_time"]
        sun_countdown = next_events["next_sun_countdown_hours"]

        if (
            sun_event is not None
            and sun_event_time is not None
            and sun_countdown is not None
        ):
            self.next_sun_event_label.setText(
                f"Next Sun Event: {sun_event} "
                f"in {sun_countdown:.2f} hours "
                f"({sun_event_time.strftime('%Y-%m-%d %H:%M UTC')})"
            )
        else:
            self.next_sun_event_label.setText(
                "Next Sun Event: None found in the "
                "extended search window"
            )

        earth_event = next_events["next_earth_event"]
        earth_event_time = next_events["next_earth_event_time"]
        earth_countdown = next_events["next_earth_countdown_hours"]

        if (
            earth_event is not None
            and earth_event_time is not None
            and earth_countdown is not None
        ):
            self.next_earth_event_label.setText(
                f"Next Earth Event: {earth_event} "
                f"in {earth_countdown:.2f} hours "
                f"({earth_event_time.strftime('%Y-%m-%d %H:%M UTC')})"
            )
        else:
            self.next_earth_event_label.setText(
                "Next Earth Event: None found in the "
                "extended search window"
            )

        self.timeline_status.setText(
            f"Real SPICE + LOLA timeline: "
            f"{len(series)} samples from "
            f"{series[0].time.strftime('%Y-%m-%d %H:%M UTC')} "
            f"to "
            f"{series[-1].time.strftime('%Y-%m-%d %H:%M UTC')} "
            f"({duration_text}, {sampling_text} sampling)."
        )
