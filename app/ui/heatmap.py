from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class MissionHeatmap(QTableWidget):
    """
    Color-coded mission geometry heatmap.

    Values are expected to be percentages from 0-100.
    This widget only handles presentation; scientific
    calculations remain in the analysis engine.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(
            [
                "Landing Site",
                "☀ Sun",
                "🌍 Earth",
                "Geometry",
            ]
        )

        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        for column in range(1, 4):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeToContents,
            )

        self.setMinimumHeight(190)

        self.setStyleSheet(
            """
            QTableWidget {
                background: #111827;
                color: #e5e7eb;
                border: 1px solid #263244;
                border-radius: 12px;
                gridline-color: #263244;
                font-size: 12px;
            }

            QHeaderView::section {
                background: #172033;
                color: #94a3b8;
                border: none;
                border-bottom: 1px solid #263244;
                padding: 10px;
                font-weight: 600;
            }

            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #1f2937;
            }
            """
        )

    def set_data(self, rows):
        """
        rows:
            [
                {
                    "site": "Shackleton Crater",
                    "sun": 82.5,
                    "earth": 64.2,
                },
                ...
            ]
        """

        self.setRowCount(0)

        for row in rows:
            row_index = self.rowCount()
            self.insertRow(row_index)

            sun = float(row["sun"])
            earth = float(row["earth"])

            geometry = (sun + earth) / 2.0

            values = [
                row["site"],
                f"{sun:.1f}°",
                f"{earth:.1f}°",
                self._geometry_label(geometry),
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(
                    Qt.AlignLeft | Qt.AlignVCenter
                    if column == 0
                    else Qt.AlignCenter
                )

                if column == 1:
                    item.setBackground(self._color_for_angle(sun))

                elif column == 2:
                    item.setBackground(self._color_for_angle(earth))

                elif column == 3:
                    item.setBackground(self._color_for_angle(geometry))

                self.setItem(row_index, column, item)

    @staticmethod
    def _color_for_angle(angle):
        if angle >= 30:
            return QColor("#166534")      # green

        if angle >= 10:
            return QColor("#a16207")      # yellow/orange

        if angle >= 0:
            return QColor("#c2410c")      # orange

        return QColor("#991b1b")          # red

    @staticmethod
    def _geometry_label(angle):
        if angle >= 30:
            return "GOOD"

        if angle >= 10:
            return "LIMITED"

        if angle >= 0:
            return "LOW"

        return "NO-GO"
