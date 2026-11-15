import sys

from app.ui.sites import SitesPage
from app.ui.dashboard import Dashboard
from app.ui.analysis import AnalysisPage
from app.ui.compare import ComparePage
from app.ui.settings import SettingsPage
from app.data.sites import LANDING_SITES

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lunar Landing Site Navigator")
        self.resize(1200, 750)

        self.setup_ui()

    def setup_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------------------------------------------------
        # GLOBAL WINDOW STYLE
        # ---------------------------------------------------------
        self.setStyleSheet(
            """
            /* =====================================================
               FULL BLACK APPLICATION THEME
               ===================================================== */

            QMainWindow,
            QWidget,
            QStackedWidget,
            QStackedWidget > QWidget {
                background: #000000;
                color: #ffffff;
            }

            QScrollArea,
            QScrollArea > QWidget,
            QScrollArea > QWidget > QWidget {
                background: #000000;
                border: none;
            }

            QLabel {
                background: transparent;
                color: #ffffff;
            }

            QGroupBox {
                background: #000000;
                color: #ffffff;
                border: 1px solid #292929;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 8px;
                font-size: 13px;
                font-weight: 700;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                background: #000000;
                color: #ffffff;
            }

            QPushButton {
                min-height: 36px;
                padding: 0 15px;
                border: 1px solid #303030;
                border-radius: 7px;
                background: #111111;
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #202020;
                border-color: #505050;
            }

            QPushButton:pressed {
                background: #2b2b2b;
            }

            QLineEdit,
            QComboBox,
            QDateEdit,
            QTimeEdit {
                min-height: 36px;
                padding: 0 10px;
                border: 1px solid #303030;
                border-radius: 7px;
                background: #111111;
                color: #ffffff;
                selection-background-color: #444444;
                selection-color: #ffffff;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QDateEdit:focus,
            QTimeEdit:focus {
                border: 1px solid #666666;
            }

            QComboBox QAbstractItemView {
                background: #111111;
                color: #ffffff;
                border: 1px solid #303030;
                selection-background-color: #2a2a2a;
                selection-color: #ffffff;
            }

            QSpinBox,
            QDoubleSpinBox {
                background: #111111;
                color: #ffffff;
                border: 1px solid #303030;
            }

            QCheckBox,
            QRadioButton {
                background: transparent;
                color: #ffffff;
            }

            QTableWidget,
            QTableView,
            QListWidget,
            QListView,
            QTreeWidget,
            QTreeView {
                background: #000000;
                alternate-background-color: #111111;
                color: #ffffff;
                border: 1px solid #292929;
                gridline-color: #292929;
            }

            QHeaderView::section {
                background: #111111;
                color: #ffffff;
                border: none;
                border-bottom: 1px solid #292929;
                padding: 7px;
            }

            QProgressBar {
                background: #111111;
                border: 1px solid #292929;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
            }

            QSlider::groove:horizontal {
                background: #292929;
                height: 5px;
                border-radius: 2px;
            }

            QSlider::handle:horizontal {
                background: #ffffff;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }

            QToolTip {
                background: #111111;
                color: #ffffff;
                border: 1px solid #444444;
            }

            QMenu {
                background: #111111;
                color: #ffffff;
                border: 1px solid #303030;
            }

            QMenu::item:selected {
                background: #292929;
            }
            """
        )

        # ---------------------------------------------------------
        # SIDEBAR
        # ---------------------------------------------------------
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(185)
        sidebar_widget.setStyleSheet(
            """
            QWidget {
                background: #080808;
            }

            QLabel {
                color: #eeeeee;
            }

            QPushButton {
                text-align: left;
                min-height: 38px;
                padding: 0 12px;
                border: none;
                border-radius: 7px;
                background: transparent;
                color: #a8a8a8;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #1b1b1b;
                color: #ffffff;
            }

            QPushButton:pressed {
                background: #252525;
                color: #ffffff;
            }
            """
        )

        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setContentsMargins(12, 16, 12, 14)
        sidebar.setSpacing(4)

        brand = QLabel("🌙  LUNAR")
        brand.setStyleSheet(
            """
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: 800;
            }
            """
        )

        title = QLabel("Navigator")
        title.setStyleSheet(
            """
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: 700;
            }
            """
        )

        subtitle = QLabel("NASA Space Apps 2026")
        subtitle.setStyleSheet(
            """
            QLabel {
                color: #9fb2ca;
                font-size: 11px;
            }
            """
        )

        sidebar.addWidget(brand)
        sidebar.addWidget(title)
        sidebar.addSpacing(16)

        self.dashboard_button = QPushButton("Dashboard")
        self.sites_button = QPushButton("Sites")
        self.analysis_button = QPushButton("Analysis")
        self.compare_button = QPushButton("Compare")
        self.settings_button = QPushButton("Settings")

        sidebar.addWidget(self.dashboard_button)
        sidebar.addWidget(self.sites_button)
        sidebar.addWidget(self.analysis_button)
        sidebar.addWidget(self.compare_button)
        sidebar.addWidget(self.settings_button)

        sidebar.addStretch()

        footer = QLabel("NASA Space Apps 2026")
        footer.setStyleSheet(
            """
            QLabel {
                color: #777777;
                font-size: 9px;
                padding: 4px;
            }
            """
        )

        sidebar.addWidget(footer)

        # Pages
        self.pages = QStackedWidget()

        # Pages
        self.pages = QStackedWidget()

        self.dashboard_page = Dashboard()

        self.sites_page = SitesPage(
            engine=self.dashboard_page.engine,
            time_provider=self.dashboard_page.get_analysis_time,
        )

        self.analysis_page = AnalysisPage(
            engine=self.dashboard_page.engine
        )

        self.compare_page = ComparePage()

        self.settings_page = SettingsPage()

        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.sites_page)
        self.pages.addWidget(self.analysis_page)
        self.pages.addWidget(self.compare_page)
        self.pages.addWidget(self.settings_page)

        # Add the styled sidebar widget to the main window.
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.pages, 1)

        # Navigation
        self.dashboard_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(0)
        )

        self.sites_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(1)
        )

        self.analysis_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(2)
        )

        self.compare_button.clicked.connect(
            self.show_compare_page
        )

        self.settings_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(4)
        )

        # Dashboard → Analysis
        self.dashboard_page.analysis_completed.connect(
            self.show_analysis_results
        )

        # Sites → Dashboard
        self.sites_page.site_changed.connect(
            self.dashboard_page.set_location
        )

        # Showcase/default analysis site.
        # Keep the Dashboard on a predefined LOLA-covered site so
        # the terrain-aware visibility feature is demonstrated.
        self.dashboard_page.set_location(
            LANDING_SITES["Cabeus Crater"]
        )

    def show_compare_page(self):
        """Open Compare using the Dashboard's latest analysis timestamp."""

        if self.dashboard_page.last_analysis is not None:
            self.compare_page.set_analysis_time(
                self.dashboard_page.last_analysis.time
            )

        self.pages.setCurrentIndex(3)

    def show_analysis_results(self, results):

        self.analysis_page.show_results(results)

        # Automatically open Analysis page
        self.pages.setCurrentWidget(
            self.analysis_page
        )
