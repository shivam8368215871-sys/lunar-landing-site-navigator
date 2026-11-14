from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QGridLayout,
)


class AnalysisPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

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
            QLabel("Status:"), 2, 0
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
            QLabel("Status:"), 2, 0
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

        main_layout.addStretch()

    # ------------------------------------------------------
    # Display analysis results
    # ------------------------------------------------------

    def show_results(self, results):

        sun = results["sun"]
        earth = results["earth"]

        self.sun_elevation.setText(
            f'{sun["elevation"]}°'
        )

        self.sun_azimuth.setText(
            f'{sun["azimuth"]}°'
        )

        self.sun_status.setText(
            sun["status"]
        )

        self.earth_elevation.setText(
            f'{earth["elevation"]}°'
        )

        self.earth_azimuth.setText(
            f'{earth["azimuth"]}°'
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
                f'{sun_horizon:.3f}°'
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
                "Visible"
                if sun_terrain_visible
                else "Blocked"
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
                f'{earth_horizon:.3f}°'
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
                "Visible"
                if earth_terrain_visible
                else "Blocked"
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
            "Visible" if sun_mission_visible else "Blocked by Terrain"
        )

        self.earth_visibility.setText(
            "Visible" if earth_mission_visible else "Blocked by Terrain"
        )

        self.status_label.setText(
            f'Analysis results loaded for {results["site"]["name"]}.'
        )
