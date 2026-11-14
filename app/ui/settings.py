from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QComboBox,
    QCheckBox,
    QPushButton,
)


class SettingsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        # Title
        title = QLabel("Settings")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        subtitle = QLabel(
            "Configure application and analysis preferences."
        )

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout()

        # Units
        units_layout = QHBoxLayout()

        units_label = QLabel("Angle Units:")

        self.units_combo = QComboBox()
        self.units_combo.addItems([
            "Degrees (°)",
            "Radians",
        ])

        units_layout.addWidget(units_label)
        units_layout.addWidget(self.units_combo)
        units_layout.addStretch()

        general_layout.addLayout(units_layout)

        # Auto update
        self.auto_update_check = QCheckBox(
            "Automatically update analysis results"
        )
        self.auto_update_check.setChecked(True)

        general_layout.addWidget(self.auto_update_check)

        # Remember site
        self.remember_site_check = QCheckBox(
            "Remember last selected landing site"
        )
        self.remember_site_check.setChecked(True)

        general_layout.addWidget(self.remember_site_check)

        general_group.setLayout(general_layout)

        main_layout.addWidget(general_group)

        # Analysis settings
        analysis_group = QGroupBox("Analysis Settings")
        analysis_layout = QVBoxLayout()

        self.sun_check = QCheckBox(
            "Include Sun analysis"
        )
        self.sun_check.setChecked(True)

        self.earth_check = QCheckBox(
            "Include Earth visibility analysis"
        )
        self.earth_check.setChecked(True)

        analysis_layout.addWidget(self.sun_check)
        analysis_layout.addWidget(self.earth_check)

        analysis_group.setLayout(analysis_layout)

        main_layout.addWidget(analysis_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save Settings")
        self.reset_button = QPushButton("Reset")

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # Status
        self.status_label = QLabel(
            "Settings are currently using default values."
        )

        main_layout.addWidget(self.status_label)

        # Connections
        self.save_button.clicked.connect(
            self.save_settings
        )

        self.reset_button.clicked.connect(
            self.reset_settings
        )

    def save_settings(self):

        self.status_label.setText(
            "Settings saved successfully."
        )

    def reset_settings(self):

        self.units_combo.setCurrentIndex(0)

        self.auto_update_check.setChecked(True)
        self.remember_site_check.setChecked(True)

        self.sun_check.setChecked(True)
        self.earth_check.setChecked(True)

        self.status_label.setText(
            "Settings have been reset to default values."
        )