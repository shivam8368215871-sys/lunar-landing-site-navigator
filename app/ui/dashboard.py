
from PySide6.QtCore import QDate, QTime, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QDateEdit,
    QTimeEdit,
    QPushButton,
    QGroupBox,
    QGridLayout,
)


class Dashboard(QWidget):

    analysis_completed = Signal(dict)

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        title = QLabel("Lunar Landing Site Analysis")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        subtitle = QLabel(
            "Select a lunar site and analysis time to begin."
        )

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # --------------------------------------------------
        # Site Selection
        # --------------------------------------------------

        site_group = QGroupBox("Landing Site")

        site_layout = QGridLayout()

        site_layout.addWidget(
            QLabel("Site:"), 0, 0
        )

        self.site_combo = QComboBox()

        self.site_combo.addItems([
            "Shackleton Crater",
            "Cabeus Crater",
            "Malapert Massif",
            "Custom Location",
        ])

        site_layout.addWidget(
            self.site_combo, 0, 1
        )

        site_layout.addWidget(
            QLabel("Latitude:"), 1, 0
        )

        self.latitude_label = QLabel("-89.90°")

        site_layout.addWidget(
            self.latitude_label, 1, 1
        )

        site_layout.addWidget(
            QLabel("Longitude:"), 2, 0
        )

        self.longitude_label = QLabel("0.00°")

        site_layout.addWidget(
            self.longitude_label, 2, 1
        )

        site_group.setLayout(site_layout)

        main_layout.addWidget(site_group)

        # --------------------------------------------------
        # Analysis Time
        # --------------------------------------------------

        time_group = QGroupBox("Analysis Time")

        time_layout = QHBoxLayout()

        date_layout = QVBoxLayout()

        date_layout.addWidget(QLabel("Date"))

        self.date_edit = QDateEdit()

        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        date_layout.addWidget(self.date_edit)

        time_layout.addLayout(date_layout)

        clock_layout = QVBoxLayout()

        clock_layout.addWidget(QLabel("Time"))

        self.time_edit = QTimeEdit()

        self.time_edit.setTime(QTime.currentTime())

        clock_layout.addWidget(self.time_edit)

        time_layout.addLayout(clock_layout)

        time_group.setLayout(time_layout)

        main_layout.addWidget(time_group)

        # --------------------------------------------------
        # Analyze Button
        # --------------------------------------------------

        self.analyze_button = QPushButton(
            "Analyze Landing Site"
        )

        self.analyze_button.clicked.connect(
            self.run_analysis
        )

        main_layout.addWidget(self.analyze_button)

        # --------------------------------------------------
        # Results
        # --------------------------------------------------

        results_group = QGroupBox("Analysis Results")

        results_layout = QGridLayout()

        results_layout.addWidget(
            QLabel("Sun Elevation:"), 0, 0
        )

        self.sun_elevation = QLabel("--")

        results_layout.addWidget(
            self.sun_elevation, 0, 1
        )

        results_layout.addWidget(
            QLabel("Sun Azimuth:"), 1, 0
        )

        self.sun_azimuth = QLabel("--")

        results_layout.addWidget(
            self.sun_azimuth, 1, 1
        )

        results_layout.addWidget(
            QLabel("Earth Elevation:"), 2, 0
        )

        self.earth_elevation = QLabel("--")

        results_layout.addWidget(
            self.earth_elevation, 2, 1
        )

        results_layout.addWidget(
            QLabel("Earth Azimuth:"), 3, 0
        )

        self.earth_azimuth = QLabel("--")

        results_layout.addWidget(
            self.earth_azimuth, 3, 1
        )

        results_layout.addWidget(
            QLabel("Sun Visibility:"), 0, 2
        )

        self.sun_visibility = QLabel("--")

        results_layout.addWidget(
            self.sun_visibility, 0, 3
        )

        results_layout.addWidget(
            QLabel("Earth Visibility:"), 1, 2
        )

        self.earth_visibility = QLabel("--")

        results_layout.addWidget(
            self.earth_visibility, 1, 3
        )

        results_group.setLayout(results_layout)

        main_layout.addWidget(results_group)

        # --------------------------------------------------
        # Status
        # --------------------------------------------------

        self.status_label = QLabel(
            "Ready for analysis."
        )

        main_layout.addWidget(
            self.status_label
        )

        main_layout.addStretch()

    # ------------------------------------------------------
    # Temporary analysis
    # ------------------------------------------------------

    def run_analysis(self):

        site_name = self.site_combo.currentText()

        # Temporary/mock analysis values.
        # These will later come from the scientific engine.

        results = {
            "site": {
                "name": site_name,
                "latitude": -89.90,
                "longitude": 0.00,
            },

            "time": {
                "date": self.date_edit.date().toString(
                    "yyyy-MM-dd"
                ),
                "time": self.time_edit.time().toString(
                    "HH:mm:ss"
                ),
            },

            "sun": {
                "elevation": 12.4,
                "azimuth": 180.0,
                "status": "Above Horizon",
                "visible": True,
            },

            "earth": {
                "elevation": 8.2,
                "azimuth": 95.0,
                "status": "Visible",
                "visible": True,
            },
        }

        # Update Dashboard results
        self.sun_elevation.setText(
            f'{results["sun"]["elevation"]}°'
        )

        self.sun_azimuth.setText(
            f'{results["sun"]["azimuth"]}°'
        )

        self.earth_elevation.setText(
            f'{results["earth"]["elevation"]}°'
        )

        self.earth_azimuth.setText(
            f'{results["earth"]["azimuth"]}°'
        )

        self.sun_visibility.setText(
            "Visible"
            if results["sun"]["visible"]
            else "Not Visible"
        )

        self.earth_visibility.setText(
            "Visible"
            if results["earth"]["visible"]
            else "Not Visible"
        )

        self.status_label.setText(
            f"Analysis completed for {site_name}."
        )

        # Send structured results to MainWindow
        self.analysis_completed.emit(results)
