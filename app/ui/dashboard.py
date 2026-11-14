from datetime import datetime, timezone

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.core.models import Site
from app.data.sites import LANDING_SITES
from app.science.engine import LunarAnalysisEngine
from app.ui.moon_globe import MoonGlobeWidget


class MetricCard(QGroupBox):
    def __init__(self, title: str):
        super().__init__()

        self.setTitle(title)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)

        self.value = QLabel("--")
        self.value.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: 700;
            }
            """
        )

        self.detail = QLabel("--")
        self.detail.setWordWrap(True)
        self.detail.setStyleSheet(
            """
            QLabel {
                color: #555;
                font-size: 12px;
            }
            """
        )

        layout.addWidget(self.value)
        layout.addWidget(self.detail)


class Dashboard(QWidget):
    analysis_completed = Signal(dict)

    def __init__(self):
        super().__init__()

        self.engine = LunarAnalysisEngine()
        self.engine.load()

        self.moon_globe = None
        self.last_analysis = None

        self.setup_ui()

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_utc_clock)
        self.clock_timer.start(1000)

        self.update_utc_clock()

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        # ---------------------------------------------------------
        # HEADER
        # ---------------------------------------------------------
        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title = QLabel("Lunar Landing Site Navigator")
        title.setStyleSheet(
            """
            QLabel {
                font-size: 26px;
                font-weight: 800;
            }
            """
        )

        subtitle = QLabel(
            "NASA Space Apps 2026 • Lunar surface lighting "
            "and communication geometry"
        )
        subtitle.setStyleSheet(
            """
            QLabel {
                color: #666;
                font-size: 13px;
            }
            """
        )

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header.addLayout(title_box)
        header.addStretch()

        self.utc_clock = QLabel()
        self.utc_clock.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.utc_clock.setStyleSheet(
            """
            QLabel {
                color: #444;
                font-size: 12px;
                font-family: monospace;
            }
            """
        )

        header.addWidget(self.utc_clock)

        root.addLayout(header)

        # ---------------------------------------------------------
        # MAIN SCROLL AREA
        # ---------------------------------------------------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(14)

        scroll.setWidget(content)
        root.addWidget(scroll)

        # ---------------------------------------------------------
        # SITE EXPLORER
        # ---------------------------------------------------------
        site_group = QGroupBox("Site Explorer")
        site_layout = QVBoxLayout(site_group)
        site_layout.setSpacing(10)

        controls = QHBoxLayout()
        controls.setSpacing(10)

        site_form = QFormLayout()
        site_form.setLabelAlignment(Qt.AlignLeft)

        self.site_combo = QComboBox()
        self.site_combo.addItems(
            [
                "Shackleton Crater",
                "Cabeus Crater",
                "Malapert Massif",
                "Custom Location",
            ]
        )
        self.site_combo.setMinimumWidth(220)

        site_form.addRow("Landing Site:", self.site_combo)
        controls.addLayout(site_form)

        self.latitude_input = QLineEdit()
        self.latitude_input.setPlaceholderText("-90 to 90")
        self.latitude_input.setMinimumWidth(125)

        self.longitude_input = QLineEdit()
        self.longitude_input.setPlaceholderText("-180 to 180")
        self.longitude_input.setMinimumWidth(125)

        controls.addWidget(QLabel("Lat:"))
        controls.addWidget(self.latitude_input)

        controls.addWidget(QLabel("Lon:"))
        controls.addWidget(self.longitude_input)

        controls.addStretch()

        site_layout.addLayout(controls)

        # ---------------------------------------------------------
        # CUSTOM LOCATION GLOBE
        # ---------------------------------------------------------
        self.custom_controls = QWidget()
        custom_layout = QVBoxLayout(self.custom_controls)
        custom_layout.setContentsMargins(0, 4, 0, 0)
        custom_layout.setSpacing(8)

        self.globe_label = QLabel(
            "Select a location on the Moon"
        )
        self.globe_label.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: 600;
            }
            """
        )

        custom_layout.addWidget(self.globe_label)

        self.moon_globe = MoonGlobeWidget()
        self.moon_globe.setMinimumHeight(380)
        self.moon_globe.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        custom_layout.addWidget(self.moon_globe)

        coordinate_buttons = QHBoxLayout()

        self.apply_coordinates_button = QPushButton(
            "Apply Coordinates"
        )

        self.clear_coordinates_button = QPushButton(
            "Clear"
        )

        coordinate_buttons.addWidget(
            self.apply_coordinates_button
        )
        coordinate_buttons.addWidget(
            self.clear_coordinates_button
        )
        coordinate_buttons.addStretch()

        custom_layout.addLayout(coordinate_buttons)

        self.custom_controls.setVisible(True)
        site_layout.addWidget(self.custom_controls)

        # ---------------------------------------------------------
        # DATE / TIME
        # ---------------------------------------------------------
        date_time = QHBoxLayout()
        date_time.setSpacing(10)

        self.date_control = QLineEdit(
            datetime.now(timezone.utc).strftime("%Y-%m-%d")
        )
        self.date_control.setPlaceholderText("YYYY-MM-DD")

        self.time_control = QLineEdit(
            datetime.now(timezone.utc).strftime("%H:%M:%S")
        )
        self.time_control.setPlaceholderText("HH:MM:SS")

        date_time.addWidget(QLabel("UTC Date:"))
        date_time.addWidget(self.date_control)

        date_time.addWidget(QLabel("UTC Time:"))
        date_time.addWidget(self.time_control)

        date_time.addStretch()

        self.analyze_button = QPushButton(
            "Analyze Landing Site"
        )
        self.analyze_button.setMinimumHeight(38)

        date_time.addWidget(self.analyze_button)

        site_layout.addLayout(date_time)

        content_layout.addWidget(site_group)

        # ---------------------------------------------------------
        # RESULT SUMMARY
        # ---------------------------------------------------------
        result_title = QLabel("Current Analysis")
        result_title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: 700;
            }
            """
        )

        content_layout.addWidget(result_title)

        metrics = QGridLayout()
        metrics.setSpacing(10)

        self.sun_card = MetricCard("Sun")
        self.earth_card = MetricCard("Earth")
        self.site_card = MetricCard("Selected Site")
        self.time_card = MetricCard("Analysis Time")

        metrics.addWidget(self.site_card, 0, 0)
        metrics.addWidget(self.sun_card, 0, 1)
        metrics.addWidget(self.earth_card, 0, 2)
        metrics.addWidget(self.time_card, 0, 3)

        content_layout.addLayout(metrics)

        # ---------------------------------------------------------
        # BODY VISIBILITY
        # ---------------------------------------------------------
        visibility_group = QGroupBox("Body Visibility")
        visibility_layout = QVBoxLayout(visibility_group)

        self.visibility_label = QLabel(
            "Run an analysis to calculate Sun and Earth "
            "visibility from the selected lunar site."
        )
        self.visibility_label.setWordWrap(True)

        visibility_layout.addWidget(
            self.visibility_label
        )

        content_layout.addWidget(
            visibility_group
        )

        # ---------------------------------------------------------
        # GO / NO-GO
        # ---------------------------------------------------------
        decision_group = QGroupBox(
            "Initial Mission Geometry Assessment"
        )

        decision_layout = QHBoxLayout(
            decision_group
        )

        self.decision_label = QLabel(
            "NO ANALYSIS"
        )
        self.decision_label.setAlignment(
            Qt.AlignCenter
        )
        self.decision_label.setMinimumHeight(
            52
        )
        self.decision_label.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: 800;
                padding: 10px;
                border: 1px solid #bbb;
                border-radius: 8px;
            }
            """
        )

        decision_layout.addWidget(
            self.decision_label
        )

        content_layout.addWidget(
            decision_group
        )

        # ---------------------------------------------------------
        # SITE COMPARISON
        # ---------------------------------------------------------
        comparison_title = QLabel("Site Comparison")
        comparison_title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: 700;
            }
            """
        )

        content_layout.addWidget(
            comparison_title
        )

        comparison_group = QGroupBox(
            "Real SPICE comparison at current UTC analysis time"
        )

        comparison_layout = QVBoxLayout(
            comparison_group
        )

        self.comparison_grid = QGridLayout()
        self.comparison_grid.setSpacing(8)

        headers = [
            "Site",
            "Sun Elevation",
            "Sun Azimuth",
            "Earth Elevation",
            "Earth Azimuth",
            "Sun",
            "Earth",
        ]

        for column, text in enumerate(headers):
            label = QLabel(text)
            label.setStyleSheet(
                """
                QLabel {
                    font-weight: 700;
                }
                """
            )
            self.comparison_grid.addWidget(
                label,
                0,
                column,
            )

        self.comparison_rows = {}

        for row, site_name in enumerate(
            LANDING_SITES.keys(),
            start=1,
        ):
            self.add_comparison_row(
                row,
                site_name,
            )

        comparison_layout.addLayout(
            self.comparison_grid
        )

        content_layout.addWidget(
            comparison_group
        )

        # ---------------------------------------------------------
        # STATUS
        # ---------------------------------------------------------
        self.result_label = QLabel(
            "No analysis performed."
        )
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet(
            """
            QLabel {
                color: #666;
                font-size: 12px;
            }
            """
        )

        content_layout.addWidget(
            self.result_label
        )

        content_layout.addStretch()

        # ---------------------------------------------------------
        # SIGNALS
        # ---------------------------------------------------------
        self.site_combo.currentTextChanged.connect(
            self.update_site_coordinates
        )

        self.apply_coordinates_button.clicked.connect(
            self.apply_manual_coordinates
        )

        self.clear_coordinates_button.clicked.connect(
            self.clear_custom_coordinates
        )

        self.moon_globe.location_selected.connect(
            self.on_globe_location_selected
        )

        self.analyze_button.clicked.connect(
            self.run_analysis
        )

        self.update_site_coordinates(
            self.site_combo.currentText()
        )

    # =============================================================
    # HEADER
    # =============================================================

    def update_utc_clock(self):
        now = datetime.now(timezone.utc)

        self.utc_clock.setText(
            "UTC  "
            + now.strftime("%Y-%m-%d  %H:%M:%S")
        )

    # =============================================================
    # SITE / GLOBE
    # =============================================================

    def update_site_coordinates(
        self,
        site_name: str,
    ):
        is_custom = (
            site_name == "Custom Location"
        )

        self.custom_controls.setVisible(
            True
        )

        if is_custom:
            self.latitude_input.setReadOnly(
                False
            )
            self.longitude_input.setReadOnly(
                False
            )

            self.latitude_input.clear()
            self.longitude_input.clear()

            self.moon_globe.clear_location()

            self.globe_label.setText(
                "Select a location on the Moon"
            )

            return

        site = LANDING_SITES.get(
            site_name
        )

        if site is None:
            return

        self.latitude_input.setReadOnly(
            True
        )
        self.longitude_input.setReadOnly(
            True
        )

        self.latitude_input.setText(
            f"{site.latitude:.6f}"
        )

        self.longitude_input.setText(
            f"{site.longitude:.6f}"
        )

        self.moon_globe.set_location(
            site.latitude,
            site.longitude,
        )

        self.globe_label.setText(
            f"{site.name}: "
            f"{site.latitude:.4f}°, "
            f"{site.longitude:.4f}°"
        )

    def on_globe_location_selected(
        self,
        latitude: float,
        longitude: float,
    ):
        self.latitude_input.blockSignals(
            True
        )

        self.longitude_input.blockSignals(
            True
        )

        self.latitude_input.setText(
            f"{latitude:.6f}"
        )

        self.longitude_input.setText(
            f"{longitude:.6f}"
        )

        self.latitude_input.blockSignals(
            False
        )

        self.longitude_input.blockSignals(
            False
        )

        self.globe_label.setText(
            "Selected location: "
            f"{latitude:.4f}°, "
            f"{longitude:.4f}°"
        )

    def apply_manual_coordinates(self):
        latitude_text = (
            self.latitude_input.text().strip()
        )

        longitude_text = (
            self.longitude_input.text().strip()
        )

        if (
            not latitude_text
            or not longitude_text
        ):
            QMessageBox.warning(
                self,
                "Missing Coordinates",
                "Enter both latitude and longitude.",
            )
            return

        try:
            latitude = float(
                latitude_text
            )
            longitude = float(
                longitude_text
            )

        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Coordinates",
                "Latitude and longitude must be numeric.",
            )
            return

        if not -90 <= latitude <= 90:
            QMessageBox.warning(
                self,
                "Invalid Latitude",
                "Latitude must be between -90° and 90°.",
            )
            return

        if not -180 <= longitude <= 180:
            QMessageBox.warning(
                self,
                "Invalid Longitude",
                "Longitude must be between -180° and 180°.",
            )
            return

        self.moon_globe.set_location(
            latitude,
            longitude,
        )

        self.globe_label.setText(
            "Selected location: "
            f"{latitude:.4f}°, "
            f"{longitude:.4f}°"
        )

        self.moon_globe.canvas.draw_idle()
        self.moon_globe.canvas.flush_events()

    def clear_custom_coordinates(self):
        self.latitude_input.clear()
        self.longitude_input.clear()

        self.moon_globe.clear_location()

        self.globe_label.setText(
            "Select a location on the Moon"
        )

    # =============================================================
    # SITE OBJECT
    # =============================================================

    # =============================================================
    # EXTERNAL SITE SELECTION
    # =============================================================

    def set_location(self, site):
        """Update Dashboard from a Site selected elsewhere in the app."""

        if site is None:
            return

        self.site_combo.blockSignals(True)

        if site.name in [
            "Shackleton Crater",
            "Cabeus Crater",
            "Malapert Massif",
            "Custom Location",
        ]:
            self.site_combo.setCurrentText(site.name)
        else:
            self.site_combo.setCurrentText("Custom Location")

        self.site_combo.blockSignals(False)

        if site.name == "Custom Location":
            self.latitude_input.setReadOnly(False)
            self.longitude_input.setReadOnly(False)

            self.latitude_input.setText(
                f"{site.latitude:.6f}"
            )

            self.longitude_input.setText(
                f"{site.longitude:.6f}"
            )

            self.moon_globe.set_location(
                site.latitude,
                site.longitude,
            )

            self.globe_label.setText(
                "Selected location: "
                f"{site.latitude:.4f}°, "
                f"{site.longitude:.4f}°"
            )

        else:
            self.update_site_coordinates(site.name)

    def get_selected_site(self):
        site_name = (
            self.site_combo.currentText()
        )

        if site_name != "Custom Location":
            return LANDING_SITES.get(
                site_name
            )

        try:
            latitude = float(
                self.latitude_input.text()
            )

            longitude = float(
                self.longitude_input.text()
            )

        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Coordinates",
                "Please enter valid numeric "
                "latitude and longitude values.",
            )

            return None

        if not -90 <= latitude <= 90:
            QMessageBox.warning(
                self,
                "Invalid Latitude",
                "Latitude must be between -90° and 90°.",
            )
            return None

        if not -180 <= longitude <= 180:
            QMessageBox.warning(
                self,
                "Invalid Longitude",
                "Longitude must be between -180° and 180°.",
            )
            return None

        return Site(
            name="Custom Location",
            latitude=latitude,
            longitude=longitude,
        )

    # =============================================================
    # ANALYSIS
    # =============================================================

    def run_analysis(self):
        site = self.get_selected_site()

        if site is None:
            return

        try:
            analysis_time = datetime.strptime(
                self.date_control.text().strip()
                + " "
                + self.time_control.text().strip(),
                "%Y-%m-%d %H:%M:%S",
            ).replace(
                tzinfo=timezone.utc
            )

        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Date/Time",
                "Use YYYY-MM-DD and HH:MM:SS in UTC.",
            )
            return

        try:
            result = self.engine.analyze(
                site,
                analysis_time,
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Analysis Error",
                f"Scientific analysis failed:\n\n{exc}",
            )
            return

        self.last_analysis = result

        self.update_current_result(
            result
        )

        self.update_site_comparison(
            analysis_time
        )

        result_data = {
            "site": {
                "name": result.site.name,
                "latitude": result.site.latitude,
                "longitude": result.site.longitude,
            },
            "time": result.time,
            "sun": {
                "elevation": result.sun.elevation,
                "azimuth": result.sun.azimuth,
                "visible": result.sun.visible,
                "status": result.sun.status,
                "terrain_horizon_elevation":
                    result.sun.terrain_horizon_elevation,
                "terrain_visible":
                    result.sun.terrain_visible,
                "terrain_status":
                    result.sun.terrain_status,
            },
            "earth": {
                "elevation": result.earth.elevation,
                "azimuth": result.earth.azimuth,
                "visible": result.earth.visible,
                "status": result.earth.status,
                "terrain_horizon_elevation":
                    result.earth.terrain_horizon_elevation,
                "terrain_visible":
                    result.earth.terrain_visible,
                "terrain_status":
                    result.earth.terrain_status,
            },
        }

        self.analysis_completed.emit(
            result_data
        )

    # =============================================================
    # CURRENT RESULT
    # =============================================================

    def update_current_result(
        self,
        result,
    ):
        self.site_card.value.setText(
            result.site.name
        )

        self.site_card.detail.setText(
            f"{result.site.latitude:.4f}°, "
            f"{result.site.longitude:.4f}°"
        )

        self.sun_card.value.setText(
            f"{result.sun.elevation:.2f}°"
        )

        self.sun_card.detail.setText(
            f"Azimuth {result.sun.azimuth:.2f}° • "
            f"{result.sun.status}"
        )

        self.earth_card.value.setText(
            f"{result.earth.elevation:.2f}°"
        )

        self.earth_card.detail.setText(
            f"Azimuth {result.earth.azimuth:.2f}° • "
            f"{result.earth.status}"
        )

        self.time_card.value.setText(
            result.time.strftime(
                "%Y-%m-%d"
            )
        )

        self.time_card.detail.setText(
            result.time.strftime(
                "%H:%M:%S UTC"
            )
        )

        self.visibility_label.setText(
            "Sun: "
            f"{result.sun.status} "
            f"({result.sun.elevation:.2f}° elevation, "
            f"{result.sun.azimuth:.2f}° azimuth)\n"
            "Earth: "
            f"{result.earth.status} "
            f"({result.earth.elevation:.2f}° elevation, "
            f"{result.earth.azimuth:.2f}° azimuth)"
        )

        if (
            result.sun.visible
            and result.earth.visible
        ):
            decision = "GO — SUN + EARTH VISIBLE"
        elif result.sun.visible:
            decision = "LIMITED — SUN VISIBLE / EARTH BELOW HORIZON"
        elif result.earth.visible:
            decision = "LIMITED — EARTH VISIBLE / SUN BELOW HORIZON"
        else:
            decision = "NO-GO — SUN + EARTH BELOW HORIZON"

        self.decision_label.setText(
            decision
        )

        self.result_label.setText(
            "Analysis completed for "
            f"{result.site.name}. "
            "Results use the current spherical lunar-horizon "
            "geometry model with NASA SPICE ephemerides."
        )

    # =============================================================
    # COMPARISON TABLE
    # =============================================================

    def add_comparison_row(
        self,
        row: int,
        site_name: str,
    ):
        labels = []

        for column in range(7):
            label = QLabel("--")
            label.setWordWrap(True)
            label.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Preferred,
            )

            self.comparison_grid.addWidget(
                label,
                row,
                column,
            )

            labels.append(label)

        labels[0].setText(
            site_name
        )

        self.comparison_rows[
            site_name
        ] = labels

    def update_site_comparison(
        self,
        analysis_time,
    ):
        for site_name in LANDING_SITES:
            site = LANDING_SITES[
                site_name
            ]

            try:
                result = self.engine.analyze(
                    site,
                    analysis_time,
                )

            except Exception as exc:
                row = self.comparison_rows[
                    site_name
                ]

                row[1].setText(
                    "ERROR"
                )
                row[2].setText(
                    str(exc)
                )

                continue

            row = self.comparison_rows[
                site_name
            ]

            row[1].setText(
                f"{result.sun.elevation:.2f}°"
            )

            row[2].setText(
                f"{result.sun.azimuth:.2f}°"
            )

            row[3].setText(
                f"{result.earth.elevation:.2f}°"
            )

            row[4].setText(
                f"{result.earth.azimuth:.2f}°"
            )

            row[5].setText(
                "Visible"
                if result.sun.visible
                else "Below Horizon"
            )

            row[6].setText(
                "Visible"
                if result.earth.visible
                else "Below Horizon"
            )

    # =============================================================
    # CLEANUP
    # =============================================================

    def closeEvent(self, event):
        try:
            self.engine.unload()
        except Exception:
            pass

        event.accept()
