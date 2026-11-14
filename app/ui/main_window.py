import sys

from app.ui.sites import SitesPage
from app.ui.dashboard import Dashboard
from app.ui.analysis import AnalysisPage
from app.ui.compare import ComparePage
from app.ui.settings import SettingsPage

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

        # Sidebar
        sidebar = QVBoxLayout()

        title = QLabel("Lunar Navigator")
        sidebar.addWidget(title)

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

        # Pages
        self.pages = QStackedWidget()

        self.dashboard_page = Dashboard()

        self.sites_page = SitesPage()

        self.analysis_page = AnalysisPage()

        self.compare_page = ComparePage()

        self.settings_page = SettingsPage()

        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.sites_page)
        self.pages.addWidget(self.analysis_page)
        self.pages.addWidget(self.compare_page)
        self.pages.addWidget(self.settings_page)

        main_layout.addLayout(sidebar, 1)
        main_layout.addWidget(self.pages, 4)

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
