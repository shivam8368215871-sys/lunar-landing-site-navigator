from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QGroupBox,
    QGridLayout,
)


class SitesPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        title = QLabel("Lunar Landing Sites")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        subtitle = QLabel(
            "Select a lunar location for analysis."
        )

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # --------------------------------------------------
        # Main Area
        # --------------------------------------------------

        content_layout = QHBoxLayout()

        # --------------------------------------------------
        # Site List
        # --------------------------------------------------

        self.site_list = QListWidget()

        self.site_list.addItems([
            "Shackleton Crater",
            "Cabeus Crater",
            "Malapert Massif",
            "Custom Location",
        ])

        self.site_list.currentRowChanged.connect(
            self.site_selected
        )

        content_layout.addWidget(
            self.site_list,
            1
        )

        # --------------------------------------------------
        # Site Information
        # --------------------------------------------------

        info_group = QGroupBox("Site Information")

        info_layout = QGridLayout()

        info_layout.addWidget(
            QLabel("Name:"), 0, 0
        )

        self.name_value = QLabel("--")

        info_layout.addWidget(
            self.name_value, 0, 1
        )

        info_layout.addWidget(
            QLabel("Latitude:"), 1, 0
        )

        self.latitude_value = QLabel("--")

        info_layout.addWidget(
            self.latitude_value, 1, 1
        )

        info_layout.addWidget(
            QLabel("Longitude:"), 2, 0
        )

        self.longitude_value = QLabel("--")

        info_layout.addWidget(
            self.longitude_value, 2, 1
        )

        info_layout.addWidget(
            QLabel("Description:"), 3, 0
        )

        self.description_value = QLabel("--")
        self.description_value.setWordWrap(True)

        info_layout.addWidget(
            self.description_value,
            3,
            1
        )

        info_group.setLayout(info_layout)

        content_layout.addWidget(
            info_group,
            2
        )

        main_layout.addLayout(
            content_layout
        )

        main_layout.addStretch()

        # Select first site automatically
        self.site_list.setCurrentRow(0)

    # ------------------------------------------------------
    # Site selection
    # ------------------------------------------------------

    def site_selected(self, row):

        sites = {
            0: {
                "name": "Shackleton Crater",
                "latitude": "-89.90°",
                "longitude": "0.00°",
                "description": (
                    "A crater near the lunar south pole "
                    "considered relevant for polar landing analysis."
                ),
            },

            1: {
                "name": "Cabeus Crater",
                "latitude": "-84.90°",
                "longitude": "-35.50°",
                "description": (
                    "A large crater in the lunar south-polar region."
                ),
            },

            2: {
                "name": "Malapert Massif",
                "latitude": "-86.00°",
                "longitude": "0.00°",
                "description": (
                    "A mountainous region near the lunar south pole."
                ),
            },

            3: {
                "name": "Custom Location",
                "latitude": "User defined",
                "longitude": "User defined",
                "description": (
                    "Allows a user-defined lunar latitude "
                    "and longitude."
                ),
            },
        }

        if row not in sites:
            return

        site = sites[row]

        self.name_value.setText(site["name"])
        self.latitude_value.setText(site["latitude"])
        self.longitude_value.setText(site["longitude"])
        self.description_value.setText(
            site["description"]
        )