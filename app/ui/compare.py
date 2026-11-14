from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QComboBox,
    QLabel,
)


class ComparePage(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        # Title
        title = QLabel("Compare Landing Sites")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        subtitle = QLabel(
            "Compare environmental and visibility conditions between two lunar sites."
        )

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # Site selection
        selection_layout = QHBoxLayout()

        site_a_group = QGroupBox("Site A")
        site_a_layout = QVBoxLayout()

        self.site_a_combo = QComboBox()
        self.site_a_combo.addItems([
            "Shackleton Crater",
            "Cabeus Crater",
            "Malapert Massif",
        ])

        site_a_layout.addWidget(QLabel("Select landing site:"))
        site_a_layout.addWidget(self.site_a_combo)

        site_a_group.setLayout(site_a_layout)

        site_b_group = QGroupBox("Site B")
        site_b_layout = QVBoxLayout()

        self.site_b_combo = QComboBox()
        self.site_b_combo.addItems([
            "Shackleton Crater",
            "Cabeus Crater",
            "Malapert Massif",
        ])

        site_b_layout.addWidget(QLabel("Select landing site:"))
        site_b_layout.addWidget(self.site_b_combo)

        site_b_group.setLayout(site_b_layout)

        selection_layout.addWidget(site_a_group)
        selection_layout.addWidget(site_b_group)

        main_layout.addLayout(selection_layout)

        # Comparison results
        comparison_group = QGroupBox("Comparison Results")
        comparison_layout = QHBoxLayout()

        self.site_a_results = QLabel()
        self.site_b_results = QLabel()

        self.site_a_results.setStyleSheet("""
            font-size: 16px;
        """)

        self.site_b_results.setStyleSheet("""
            font-size: 16px;
        """)

        comparison_layout.addWidget(self.site_a_results)
        comparison_layout.addWidget(self.site_b_results)

        comparison_group.setLayout(comparison_layout)

        main_layout.addWidget(comparison_group)

        # Status
        self.status_label = QLabel("Select two sites to compare.")

        main_layout.addWidget(self.status_label)

        # Connect selection changes
        self.site_a_combo.currentTextChanged.connect(
            self.update_comparison
        )

        self.site_b_combo.currentTextChanged.connect(
            self.update_comparison
        )

        # Initial comparison
        self.update_comparison()

    def update_comparison(self):

        site_a = self.site_a_combo.currentText()
        site_b = self.site_b_combo.currentText()

        data = {
            "Shackleton Crater": {
                "sun_elevation": "12.4°",
                "earth_elevation": "8.2°",
                "sun_visibility": "Visible",
                "earth_visibility": "Visible",
            },

            "Cabeus Crater": {
                "sun_elevation": "7.8°",
                "earth_elevation": "5.6°",
                "sun_visibility": "Visible",
                "earth_visibility": "Visible",
            },

            "Malapert Massif": {
                "sun_elevation": "18.1°",
                "earth_elevation": "11.3°",
                "sun_visibility": "Visible",
                "earth_visibility": "Visible",
            },
        }

        a = data[site_a]
        b = data[site_b]

        self.site_a_results.setText(
            f"""
<b>{site_a}</b>

Sun Elevation: {a["sun_elevation"]}

Earth Elevation: {a["earth_elevation"]}

Sun Visibility: {a["sun_visibility"]}

Earth Visibility: {a["earth_visibility"]}
"""
        )

        self.site_b_results.setText(
            f"""
<b>{site_b}</b>

Sun Elevation: {b["sun_elevation"]}

Earth Elevation: {b["earth_elevation"]}

Sun Visibility: {b["sun_visibility"]}

Earth Visibility: {b["earth_visibility"]}
"""
        )

        if site_a == site_b:
            self.status_label.setText(
                "Select two different sites for a meaningful comparison."
            )
        else:
            self.status_label.setText(
                f"Comparing {site_a} with {site_b}."
            )