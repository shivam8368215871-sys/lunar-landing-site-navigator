from datetime import datetime, timezone

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QComboBox,
    QLabel,
    QSizePolicy,
    QScrollArea,
)

from app.data.sites import LANDING_SITES
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
        # Results
        # -------------------------------------------------

        comparison_group = QGroupBox(
            "Real-Time SPICE Comparison"
        )

        comparison_layout = QHBoxLayout(
            comparison_group
        )

        comparison_layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        comparison_layout.setSpacing(20)

        self.site_a_results = QLabel()
        self.site_b_results = QLabel()

        self._configure_result_label(
            self.site_a_results
        )

        self._configure_result_label(
            self.site_b_results
        )

        comparison_layout.addWidget(
            self.site_a_results,
            1,
        )

        comparison_layout.addWidget(
            self.site_b_results,
            1,
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
            list(LANDING_SITES.keys())
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

    def update_comparison(self):

        site_a_name = (
            self.site_a_combo.currentText()
        )

        site_b_name = (
            self.site_b_combo.currentText()
        )

        site_a = LANDING_SITES[
            site_a_name
        ]

        site_b = LANDING_SITES[
            site_b_name
        ]

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

        self.site_a_results.setText(
            self._format_result(
                result_a
            )
        )

        self.site_b_results.setText(
            self._format_result(
                result_b
            )
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

    @staticmethod
    def _format_result(result):

        return f"""
<b>{result.site.name}</b>

Latitude: {result.site.latitude:.2f}°

Longitude: {result.site.longitude:.2f}°

<b>Sun</b>

Elevation: {result.sun.elevation:.2f}°

Azimuth: {result.sun.azimuth:.2f}°

Visibility: {result.sun.status}

<b>Earth</b>

Elevation: {result.earth.elevation:.2f}°

Azimuth: {result.earth.azimuth:.2f}°

Visibility: {result.earth.status}
"""
