from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QGroupBox,
    QGridLayout,
    QDialog,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from app.core.models import Site
from app.data.sites import LANDING_SITES
from app.ui.lunar_maps import LunarMapsWidget


class SitesPage(QWidget):

    site_changed = Signal(object)

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

        # --------------------------------------------------
        # Lunar Maps
        # --------------------------------------------------

        self.lunar_maps = LunarMapsWidget()

        main_layout.addWidget(
            self.lunar_maps,
            1
        )

        # Give the map area the remaining vertical space.
        main_layout.setStretch(2, 0)
        main_layout.setStretch(3, 1)

        # Select first site automatically
        self.site_list.setCurrentRow(0)

    # ------------------------------------------------------
    # Site selection
    # ------------------------------------------------------

    def site_selected(self, row):

        descriptions = {
            "Shackleton Crater": (
                "A crater near the lunar south pole "
                "considered relevant for polar landing analysis."
            ),

            "Cabeus Crater": (
                "A large crater in the lunar south-polar region."
            ),

            "Malapert Massif": (
                "A mountainous region near the lunar south pole."
            ),

            "Custom Location": (
                "Allows a user-defined lunar latitude "
                "and longitude."
            ),
        }

        if row < 0:
            return

        site_name = self.site_list.item(row).text()

        if site_name == "Custom Location":
            dialog = QDialog(self)
            dialog.setWindowTitle("Custom Lunar Location")
            dialog.setMinimumWidth(360)

            layout = QVBoxLayout(dialog)

            layout.addWidget(
                QLabel("Enter custom lunar coordinates:")
            )

            layout.addWidget(
                QLabel("Latitude (-90° to 90°)")
            )

            latitude_input = QLineEdit()
            latitude_input.setPlaceholderText(
                "-90 to 90"
            )
            layout.addWidget(latitude_input)

            layout.addWidget(
                QLabel("Longitude (-180° to 180°)")
            )

            longitude_input = QLineEdit()
            longitude_input.setPlaceholderText(
                "-180 to 180"
            )
            layout.addWidget(longitude_input)

            buttons = QHBoxLayout()

            cancel_button = QPushButton("Cancel")
            apply_button = QPushButton("Apply Location")

            buttons.addWidget(cancel_button)
            buttons.addWidget(apply_button)

            layout.addLayout(buttons)

            cancel_button.clicked.connect(
                dialog.reject
            )

            def apply_custom_location():
                try:
                    latitude = float(
                        latitude_input.text().strip()
                    )
                    longitude = float(
                        longitude_input.text().strip()
                    )
                except ValueError:
                    QMessageBox.warning(
                        dialog,
                        "Invalid Coordinates",
                        "Latitude and longitude must be numeric.",
                    )
                    return

                if not -90 <= latitude <= 90:
                    QMessageBox.warning(
                        dialog,
                        "Invalid Latitude",
                        "Latitude must be between -90° and 90°.",
                    )
                    return

                if not -180 <= longitude <= 180:
                    QMessageBox.warning(
                        dialog,
                        "Invalid Longitude",
                        "Longitude must be between -180° and 180°.",
                    )
                    return

                custom_site = Site(
                    name="Custom Location",
                    latitude=latitude,
                    longitude=longitude,
                )

                self.name_value.setText(
                    custom_site.name
                )

                self.latitude_value.setText(
                    f"{latitude:.2f}°"
                )

                self.longitude_value.setText(
                    f"{longitude:.2f}°"
                )

                self.description_value.setText(
                    descriptions[site_name]
                )

                self.lunar_maps.set_location(
                    latitude,
                    longitude,
                )

                self.site_changed.emit(
                    custom_site
                )

                dialog.accept()

            apply_button.clicked.connect(
                apply_custom_location
            )

            dialog.exec()

            return

        site = LANDING_SITES.get(site_name)

        if site is None:
            return

        self.name_value.setText(site.name)

        self.latitude_value.setText(
            f"{site.latitude:.2f}°"
        )

        self.longitude_value.setText(
            f"{site.longitude:.2f}°"
        )

        self.description_value.setText(
            descriptions[site_name]
        )

        # Update lunar maps for the selected site
        self.lunar_maps.set_location(
            site.latitude,
            site.longitude,
        )

        self.site_changed.emit(site)