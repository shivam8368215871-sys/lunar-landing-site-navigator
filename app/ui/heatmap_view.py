from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont
from PySide6.QtWidgets import QWidget


class VisibilityHeatmapView(QWidget):
    """Render terrain-aware visibility on the LOLA polar raster."""

    RASTER_SIZE = 7584
    CENTER = 3791.5
    PIXEL_SIZE_KM = 0.04
    MOON_RADIUS_KM = 1737.4

    def __init__(self, parent=None):
        super().__init__(parent)

        self.result = None
        self.target = "sun"
        self.latitude = None
        self.longitude = None

        self.setMinimumSize(260, 260)

        self.setStyleSheet("""
            background: #10141b;
            border: 1px solid #303844;
        """)

    def set_result(self, result):
        self.result = result
        self.update()

    def set_target(self, target):
        if target not in ("sun", "earth"):
            raise ValueError("Target must be 'sun' or 'earth'.")

        self.target = target
        self.update()

    def set_location(self, latitude, longitude):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.update()

    def clear_location(self):
        self.latitude = None
        self.longitude = None
        self.update()

    def _coordinate_to_pixel(self):
        if self.latitude is None or self.longitude is None:
            return None

        if not -90.0 <= self.latitude <= -85.0:
            return None

        import math

        phi = math.radians(self.latitude)
        lam = math.radians(self.longitude)

        rho = (
            2.0
            * self.MOON_RADIUS_KM
            * math.tan(math.pi / 4.0 + phi / 2.0)
        )

        x = rho * math.sin(lam)
        y = -rho * math.cos(lam)

        column = self.CENTER + x / self.PIXEL_SIZE_KM
        row = self.CENTER + y / self.PIXEL_SIZE_KM

        if not (
            0 <= row < self.RASTER_SIZE
            and 0 <= column < self.RASTER_SIZE
        ):
            return None

        return row, column

    @staticmethod
    def _cell_color(visible):
        if visible is True:
            return QColor(40, 190, 105, 210)

        if visible is False:
            return QColor(225, 70, 70, 210)

        return QColor(130, 140, 155, 175)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor("#10141b"))

        available = self.rect().adjusted(8, 8, -8, -8)
        side = min(available.width(), available.height())

        left = available.center().x() - side / 2
        top = available.center().y() - side / 2

        raster_rect = QRectF(left, top, side, side)

        painter.fillRect(
            raster_rect,
            QColor("#202936"),
        )

        if self.result is None:
            painter.setPen(QColor("#b9c3d0"))
            painter.drawText(
                raster_rect,
                Qt.AlignCenter,
                "No visibility data\n\nGenerate heatmap",
            )
            painter.end()
            return

        grid_size = self.result.grid_size
        cell_size = side / grid_size

        painter.setPen(QPen(QColor(30, 38, 49, 150), 0.5))

        for cell in self.result.cells:
            visible = getattr(
                cell,
                f"{self.target}_visible",
            )

            color = self._cell_color(visible)

            x = left + (
                cell.column / self.RASTER_SIZE
            ) * side

            y = top + (
                cell.row / self.RASTER_SIZE
            ) * side

            rect = QRectF(
                x - cell_size / 2,
                y - cell_size / 2,
                cell_size,
                cell_size,
            )

            painter.fillRect(rect, QBrush(color))
            painter.drawRect(rect)

        painter.setPen(QPen(QColor("#64748b"), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(raster_rect)

        marker = self._coordinate_to_pixel()

        if marker is not None:
            row, column = marker

            marker_x = left + (
                column / self.RASTER_SIZE
            ) * side

            marker_y = top + (
                row / self.RASTER_SIZE
            ) * side

            painter.setPen(QPen(QColor("white"), 2))
            painter.setBrush(QBrush(QColor("#2563eb")))

            painter.drawEllipse(
                int(marker_x - 6),
                int(marker_y - 6),
                12,
                12,
            )

            painter.setPen(QPen(QColor("white"), 1))
            painter.drawLine(
                int(marker_x - 10),
                int(marker_y),
                int(marker_x + 10),
                int(marker_y),
            )
            painter.drawLine(
                int(marker_x),
                int(marker_y - 10),
                int(marker_x),
                int(marker_y + 10),
            )

        painter.end()
