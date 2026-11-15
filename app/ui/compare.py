from datetime import datetime, timezone

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QComboBox,
    QLabel,
    QGridLayout,
    QSizePolicy,
    QScrollArea,
    QLineEdit,
    QPushButton,
)

from app.data.sites import LANDING_SITES
from app.core.models import Site
from app.science.engine import LunarAnalysisEngine


class ComparePage(QWidget):

    def __init__(self):
        super().__init__()

        self.engine = LunarAnalysisEngine()
        self.engine.load()

        # Dashboard-selected UTC analysis time.
        # None means Compare may use the current UTC time as a fallback.
        self.analysis_time = None

        self.setup_ui()

    def set_analysis_time(self, analysis_time):
        """Set the UTC timestamp used for all site comparisons."""
        self.analysis_time = analysis_time

        # Refresh only when the page is already initialized.
        if hasattr(self, "site_a_combo") and hasattr(self, "site_b_combo"):
            self.update_comparison()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        title = QLabel("Compare Landing Sites")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        title.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        subtitle = QLabel(
            "Compare real Sun and Earth conditions between two lunar sites."
        )

        subtitle.setWordWrap(True)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # -------------------------------------------------
        # Site selection
        # -------------------------------------------------

        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(16)

        site_a_group = self._create_site_selector(
            "Site A",
            self.site_a_combo_placeholder(),
        )

        site_b_group = self._create_site_selector(
            "Site B",
            self.site_b_combo_placeholder(),
        )

        selection_layout.addWidget(
            site_a_group,
            1,
        )

        selection_layout.addWidget(
            site_b_group,
            1,
        )


        main_layout.addLayout(
            selection_layout
        )

        # -------------------------------------------------
        # Compare action
        # -------------------------------------------------

        self.compare_button = QPushButton(
            "Compare Landing Sites"
        )

        self.compare_button.setMinimumHeight(42)

        self.compare_button.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: bold;
                padding: 8px 18px;
            }

            QPushButton:hover {
                background-color: #e8f0fe;
            }

            QPushButton:pressed {
                background-color: #dbe7f9;
            }
        """)

        self.compare_button.clicked.connect(
            self.update_comparison
        )

        main_layout.addWidget(
            self.compare_button
        )

        # -------------------------------------------------
        # Results
        # -------------------------------------------------

        comparison_group = QGroupBox(
            "Real-Time SPICE + LOLA Comparison"
        )

        comparison_layout = QVBoxLayout(
            comparison_group
        )

        comparison_layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        self.comparison_grid = QGridLayout()
        self.comparison_grid.setHorizontalSpacing(18)
        self.comparison_grid.setVerticalSpacing(8)

        headers = [
            "Metric",
            "Site A",
            "Site B",
            "Difference",
        ]

        for column, header in enumerate(headers):
            label = QLabel(header)
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 14px;
                    padding: 6px;
                }
            """)
            self.comparison_grid.addWidget(
                label,
                0,
                column,
            )

        self.comparison_rows = {}

        metrics = [
            ("Sun elevation", "sun_elevation"),
            ("Sun azimuth", "sun_azimuth"),
            ("Sun terrain horizon", "sun_horizon"),
            ("Sun visibility", "sun_visibility"),
            ("Earth elevation", "earth_elevation"),
            ("Earth azimuth", "earth_azimuth"),
            ("Earth terrain horizon", "earth_horizon"),
            ("Earth visibility", "earth_visibility"),
        ]

        for row, (title, key) in enumerate(metrics, start=1):
            metric_label = QLabel(title)
            metric_label.setStyleSheet(
                "font-weight: bold; padding: 5px;"
            )

            site_a_label = QLabel("--")
            site_b_label = QLabel("--")
            difference_label = QLabel("--")

            for label in (
                site_a_label,
                site_b_label,
                difference_label,
            ):
                label.setStyleSheet(
                    "padding: 5px;"
                )

            self.comparison_grid.addWidget(
                metric_label,
                row,
                0,
            )
            self.comparison_grid.addWidget(
                site_a_label,
                row,
                1,
            )
            self.comparison_grid.addWidget(
                site_b_label,
                row,
                2,
            )
            self.comparison_grid.addWidget(
                difference_label,
                row,
                3,
            )

            self.comparison_rows[key] = (
                site_a_label,
                site_b_label,
                difference_label,
            )

        comparison_layout.addLayout(
            self.comparison_grid
        )

        main_layout.addWidget(
            comparison_group,
            1,
        )

        # -------------------------------------------------
        # Time
        # -------------------------------------------------

        self.time_label = QLabel()

        self.time_label.setWordWrap(True)

        self.time_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        main_layout.addWidget(
            self.time_label
        )

        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        self.status_label = QLabel(
            "Select two sites to compare."
        )

        self.status_label.setWordWrap(True)

        self.status_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        main_layout.addWidget(
            self.status_label
        )

        # -------------------------------------------------
        # Connections
        # -------------------------------------------------

        self.site_a_combo.currentTextChanged.connect(
            self.update_comparison
        )

        self.site_b_combo.currentTextChanged.connect(
            self.update_comparison
        )

        # Start with two different sites.
        if self.site_b_combo.count() > 1:
            self.site_b_combo.setCurrentIndex(1)

        self.update_comparison()

    def site_a_combo_placeholder(self):
        return "site_a"

    def site_b_combo_placeholder(self):
        return "site_b"

    def _create_site_selector(
        self,
        title,
        identifier,
    ):
        group = QGroupBox(title)

        layout = QVBoxLayout(group)

        layout.setSpacing(8)

        combo = QComboBox()

        combo.addItems(
            [
                *LANDING_SITES.keys(),
                "Custom Location",
            ]
        )

        combo.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        combo.setMinimumHeight(38)

        if identifier == "site_a":
            self.site_a_combo = combo
        else:
            self.site_b_combo = combo

        label = QLabel(
            "Select landing site:"
        )

        label.setWordWrap(True)

        layout.addWidget(label)
        layout.addWidget(combo)

        custom_widget = QWidget()
        custom_layout = QVBoxLayout(custom_widget)
        custom_layout.setContentsMargins(0, 4, 0, 0)
        custom_layout.setSpacing(6)

        name_label = QLabel("Location name:")
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Custom landing location")

        latitude_label = QLabel("Latitude (°):")
        latitude_edit = QLineEdit()
        latitude_edit.setPlaceholderText("-90 to 90")

        longitude_label = QLabel("Longitude (°):")
        longitude_edit = QLineEdit()
        longitude_edit.setPlaceholderText("-180 to 180")

        custom_layout.addWidget(name_label)
        custom_layout.addWidget(name_edit)
        custom_layout.addWidget(latitude_label)
        custom_layout.addWidget(latitude_edit)
        custom_layout.addWidget(longitude_label)
        custom_layout.addWidget(longitude_edit)

        custom_widget.setVisible(False)
        layout.addWidget(custom_widget)

        if identifier == "site_a":
            self.site_a_combo = combo
            self.site_a_custom_widget = custom_widget
            self.site_a_name_edit = name_edit
            self.site_a_latitude_edit = latitude_edit
            self.site_a_longitude_edit = longitude_edit
        else:
            self.site_b_combo = combo
            self.site_b_custom_widget = custom_widget
            self.site_b_name_edit = name_edit
            self.site_b_latitude_edit = latitude_edit
            self.site_b_longitude_edit = longitude_edit

        combo.currentTextChanged.connect(
            lambda value, widget=custom_widget: (
                widget.setVisible(value == "Custom Location")
            )
        )

        return group

    @staticmethod
    def _configure_result_label(label):

        label.setWordWrap(True)

        label.setAlignment(
            Qt.AlignTop | Qt.AlignLeft
        )

        label.setTextFormat(
            Qt.RichText
        )

        label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        label.setMinimumWidth(0)

        label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                padding: 8px;
            }
        """)

    def _resolve_selected_site(self, identifier):
        """Return a predefined or custom Site for a Compare selector."""

        if identifier == "site_a":
            combo = self.site_a_combo
            name_edit = self.site_a_name_edit
            latitude_edit = self.site_a_latitude_edit
            longitude_edit = self.site_a_longitude_edit
        else:
            combo = self.site_b_combo
            name_edit = self.site_b_name_edit
            latitude_edit = self.site_b_latitude_edit
            longitude_edit = self.site_b_longitude_edit

        selected_name = combo.currentText()

        if selected_name != "Custom Location":
            return LANDING_SITES[selected_name]

        location_name = name_edit.text().strip()
        latitude_text = latitude_edit.text().strip()
        longitude_text = longitude_edit.text().strip()

        if not location_name:
            self.status_label.setText(
                f"{'Site A' if identifier == 'site_a' else 'Site B'}: "
                "enter a location name."
            )
            return None

        try:
            latitude = float(latitude_text)
        except ValueError:
            self.status_label.setText(
                f"{'Site A' if identifier == 'site_a' else 'Site B'}: "
                "latitude must be a valid number."
            )
            return None

        try:
            longitude = float(longitude_text)
        except ValueError:
            self.status_label.setText(
                f"{'Site A' if identifier == 'site_a' else 'Site B'}: "
                "longitude must be a valid number."
            )
            return None

        if not -90.0 <= latitude <= 90.0:
            self.status_label.setText(
                f"{'Site A' if identifier == 'site_a' else 'Site B'}: "
                "latitude must be between -90° and 90°."
            )
            return None

        if not -180.0 <= longitude <= 180.0:
            self.status_label.setText(
                f"{'Site A' if identifier == 'site_a' else 'Site B'}: "
                "longitude must be between -180° and 180°."
            )
            return None

        return Site(
            name=location_name,
            latitude=latitude,
            longitude=longitude,
        )

    def update_comparison(self):

        site_a_name = (
            self.site_a_combo.currentText()
        )

        site_b_name = (
            self.site_b_combo.currentText()
        )

        site_a = self._resolve_selected_site(
            "site_a",
        )

        site_b = self._resolve_selected_site(
            "site_b",
        )

        if site_a is None or site_b is None:
            return

        if self.analysis_time is None:
            analysis_time = datetime.now(
                timezone.utc
            ).replace(
                tzinfo=None
            )
        else:
            analysis_time = self.analysis_time

            # LunarAnalysisEngine expects a UTC datetime.
            # Keep the timestamp explicitly UTC and remove timezone
            # information only if the supplied value is timezone-aware.
            if analysis_time.tzinfo is not None:
                analysis_time = analysis_time.astimezone(
                    timezone.utc
                ).replace(
                    tzinfo=None
                )

        try:

            result_a = self.engine.analyze(
                site_a,
                analysis_time,
            )

            result_b = self.engine.analyze(
                site_b,
                analysis_time,
            )

        except Exception as error:

            self.site_a_results.setText(
                f"<b>{site_a_name}</b><br><br>"
                "Analysis failed."
            )

            self.site_b_results.setText(
                f"<b>{site_b_name}</b><br><br>"
                "Analysis failed."
            )

            self.status_label.setText(
                f"SPICE analysis error: {error}"
            )

            return

        self._update_comparison_grid(
            result_a,
            result_b,
        )

        self.time_label.setText(
            "Analysis time (UTC): "
            + analysis_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        if site_a_name == site_b_name:

            self.status_label.setText(
                "Select two different sites for a meaningful comparison."
            )

        else:

            self.status_label.setText(
                f"Comparing {site_a_name} with "
                f"{site_b_name} using real NASA SPICE data."
            )

    def _update_comparison_grid(
        self,
        result_a,
        result_b,
    ):
        """Populate the structured site comparison."""

        def visibility_text(result):
            return (
                "Visible"
                if result.mission_visible
                else "Blocked by Terrain"
            )

        def horizon_text(result):
            if result.terrain_horizon_elevation is None:
                return "Unavailable"
            return f"{result.terrain_horizon_elevation:.2f}°"

        rows = {
            "sun_elevation": (
                f"{result_a.sun.elevation:.2f}°",
                f"{result_b.sun.elevation:.2f}°",
                f"{result_b.sun.elevation - result_a.sun.elevation:+.2f}°",
            ),
            "sun_azimuth": (
                f"{result_a.sun.azimuth:.2f}°",
                f"{result_b.sun.azimuth:.2f}°",
                f"{result_b.sun.azimuth - result_a.sun.azimuth:+.2f}°",
            ),
            "sun_horizon": (
                horizon_text(result_a.sun),
                horizon_text(result_b.sun),
                (
                    f"{result_b.sun.terrain_horizon_elevation - result_a.sun.terrain_horizon_elevation:+.2f}°"
                    if (
                        result_a.sun.terrain_horizon_elevation is not None
                        and result_b.sun.terrain_horizon_elevation is not None
                    )
                    else "—"
                ),
            ),
            "sun_visibility": (
                visibility_text(result_a.sun),
                visibility_text(result_b.sun),
                "—",
            ),
            "earth_elevation": (
                f"{result_a.earth.elevation:.2f}°",
                f"{result_b.earth.elevation:.2f}°",
                f"{result_b.earth.elevation - result_a.earth.elevation:+.2f}°",
            ),
            "earth_azimuth": (
                f"{result_a.earth.azimuth:.2f}°",
                f"{result_b.earth.azimuth:.2f}°",
                f"{result_b.earth.azimuth - result_a.earth.azimuth:+.2f}°",
            ),
            "earth_horizon": (
                horizon_text(result_a.earth),
                horizon_text(result_b.earth),
                (
                    f"{result_b.earth.terrain_horizon_elevation - result_a.earth.terrain_horizon_elevation:+.2f}°"
                    if (
                        result_a.earth.terrain_horizon_elevation is not None
                        and result_b.earth.terrain_horizon_elevation is not None
                    )
                    else "—"
                ),
            ),
            "earth_visibility": (
                visibility_text(result_a.earth),
                visibility_text(result_b.earth),
                "—",
            ),
        }

        for key, values in rows.items():
            labels = self.comparison_rows[key]

            for label, value in zip(labels, values):
                label.setText(value)

    @staticmethod
    def _format_result(result):

        return f"""
<b>{result.site.name}</b>

Latitude: {result.site.latitude:.2f}°

Longitude: {result.site.longitude:.2f}°

<b>Sun</b>

Elevation: {result.sun.elevation:.2f}°

Azimuth: {result.sun.azimuth:.2f}°

Visibility: {
    "Visible"
    if result.sun.mission_visible
    else "Blocked by Terrain"
}

<b>Earth</b>

Elevation: {result.earth.elevation:.2f}°

Azimuth: {result.earth.azimuth:.2f}°

Visibility: {
    "Visible"
    if result.earth.mission_visible
    else "Blocked by Terrain"
}
"""
