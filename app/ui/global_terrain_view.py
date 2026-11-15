from __future__ import annotations

import math

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import (
    QColor,
    QFont,
    QImage,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QWidget

from app.science.lola_global_terrain import GlobalLOLATerrain


class GlobalTerrainMapView(QWidget):
    """
    Worldwide lunar elevation map rendered from NASA LRO/LOLA.

    The source is the actual LDEM_64_FLOAT raster in simple
    cylindrical projection. Longitude increases eastward
    from 0 to 360 degrees across the image.

    Polar landing-site analysis continues to use the separate
    higher-resolution 40 m polar DEMs.
    """

    DISPLAY_WIDTH = 1440
    DISPLAY_HEIGHT = 720

    def __init__(self, parent=None):
        super().__init__(parent)

        self.latitude = None
        self.longitude = None

        self._terrain_image = None
        self._load_attempted = False
        self._load_error = None

        self.setMinimumSize(300, 280)

        self.setStyleSheet(
            """
            background: #000000;
            border: 1px solid #292929;
            """
        )

    def set_location(self, latitude, longitude):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.update()

    def clear_location(self):
        self.latitude = None
        self.longitude = None
        self.update()

    def _ensure_terrain_image(self):
        if self._load_attempted:
            return

        self._load_attempted = True
        terrain = GlobalLOLATerrain()

        try:
            terrain.load()

            elevation = terrain.display_grid(
                width=self.DISPLAY_WIDTH,
                height=self.DISPLAY_HEIGHT,
            )

            finite = (
                elevation == elevation
            ) & (
                abs(elevation) != float("inf")
            )

            if not finite.any():
                raise ValueError(
                    "Global LOLA preview contains no finite elevations."
                )

            valid = elevation[finite]

            minimum = float(
                __import__("numpy").percentile(valid, 2)
            )

            maximum = float(
                __import__("numpy").percentile(valid, 98)
            )

            if maximum <= minimum:
                raise ValueError(
                    "Global LOLA elevation range is invalid."
                )

            import numpy as np

            normalized = np.clip(
                (elevation - minimum) / (maximum - minimum),
                0.0,
                1.0,
            )

            shade = (
                24.0 + normalized * 170.0
            ).astype(np.uint8)

            shade[~finite] = 8

            rgb = np.empty(
                (
                    self.DISPLAY_HEIGHT,
                    self.DISPLAY_WIDTH,
                    3,
                ),
                dtype=np.uint8,
            )

            rgb[:, :, 0] = shade
            rgb[:, :, 1] = shade
            rgb[:, :, 2] = shade

            self._terrain_image = QImage(
                rgb.data,
                self.DISPLAY_WIDTH,
                self.DISPLAY_HEIGHT,
                rgb.strides[0],
                QImage.Format.Format_RGB888,
            ).copy()

        except Exception as exc:
            self._load_error = str(exc)
            self._terrain_image = None

        finally:
            terrain.unload()

    def _map_rect(self):
        left = 44.0
        right = 12.0
        top = 42.0
        bottom = 38.0

        available_width = max(
            1.0,
            self.width() - left - right,
        )

        available_height = max(
            1.0,
            self.height() - top - bottom,
        )

        map_width = min(
            available_width,
            available_height * 2.0,
        )

        map_height = map_width / 2.0

        x = (
            left
            + (available_width - map_width) / 2.0
        )

        y = (
            top
            + (available_height - map_height) / 2.0
        )

        return QRectF(
            x,
            y,
            map_width,
            map_height,
        )

    def _draw_grid(self, painter, rect):
        painter.save()

        painter.setPen(
            QPen(
                QColor(220, 225, 235, 65),
                1,
                Qt.PenStyle.DashLine,
            )
        )

        longitude_lines = [
            (0, "0°"),
            (90, "90°E"),
            (180, "180°"),
            (270, "90°W"),
            (360, "0°"),
        ]

        for longitude, _label in longitude_lines:
            x = (
                rect.left()
                + longitude / 360.0 * rect.width()
            )

            painter.drawLine(
                int(x),
                int(rect.top()),
                int(x),
                int(rect.bottom()),
            )

        latitude_lines = [
            60,
            30,
            0,
            -30,
            -60,
        ]

        for latitude in latitude_lines:
            y = (
                rect.top()
                + (90.0 - latitude) / 180.0
                * rect.height()
            )

            painter.drawLine(
                int(rect.left()),
                int(y),
                int(rect.right()),
                int(y),
            )

        painter.setPen(QColor("#c4ccd7"))

        font = QFont("Sans Serif", 8)
        font.setBold(True)
        painter.setFont(font)

        for longitude, label in longitude_lines:
            x = (
                rect.left()
                + longitude / 360.0 * rect.width()
            )

            label_rect = QRectF(
                x - 24,
                rect.bottom() + 4,
                48,
                18,
            )

            painter.drawText(
                label_rect,
                Qt.AlignmentFlag.AlignHCenter
                | Qt.AlignmentFlag.AlignTop,
                label,
            )

        for latitude in latitude_lines:
            y = (
                rect.top()
                + (90.0 - latitude) / 180.0
                * rect.height()
            )

            painter.drawText(
                QRectF(
                    2,
                    y - 9,
                    38,
                    18,
                ),
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter,
                f"{latitude}°",
            )

        painter.restore()

    def _draw_marker(self, painter, rect):
        if (
            self.latitude is None
            or self.longitude is None
        ):
            return

        if not (
            math.isfinite(self.latitude)
            and math.isfinite(self.longitude)
            and -90.0 <= self.latitude <= 90.0
        ):
            return

        # The global raster begins at 0 degrees east and
        # wraps continuously to 360 degrees east.
        longitude = self.longitude % 360.0

        x = (
            rect.left()
            + longitude / 360.0 * rect.width()
        )

        y = (
            rect.top()
            + (90.0 - self.latitude) / 180.0
            * rect.height()
        )

        painter.save()

        painter.setPen(
            QPen(
                QColor("#00e5a8"),
                2,
            )
        )

        painter.setBrush(
            QColor(0, 229, 168, 45)
        )

        painter.drawEllipse(
            int(x - 7),
            int(y - 7),
            14,
            14,
        )

        painter.drawLine(
            int(x - 13),
            int(y),
            int(x + 13),
            int(y),
        )

        painter.drawLine(
            int(x),
            int(y - 13),
            int(x),
            int(y + 13),
        )

        painter.setPen(QColor("#ffffff"))

        font = QFont("Sans Serif", 8)
        font.setBold(True)
        painter.setFont(font)

        label_x = (
            x - 155
            if x > rect.center().x()
            else x + 12
        )

        label_y = max(
            rect.top() + 15,
            min(
                rect.bottom() - 5,
                y - 11,
            ),
        )

        painter.drawText(
            int(label_x),
            int(label_y),
            f"Selected: {self.latitude:.3f}°, "
            f"{self.longitude:.3f}°",
        )

        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.fillRect(
            self.rect(),
            QColor("#000000"),
        )

        self._ensure_terrain_image()

        rect = self._map_rect()

        if self._terrain_image is None:
            painter.setPen(QColor("#d0d0d0"))

            message = (
                "Global LOLA DEM unavailable\n"
                + (self._load_error or "")
            )

            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                message,
            )

            painter.end()
            return

        painter.drawImage(
            rect,
            self._terrain_image,
        )

        self._draw_grid(
            painter,
            rect,
        )

        painter.setPen(
            QPen(
                QColor("#aab3c0"),
                1,
            )
        )

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(rect)

        self._draw_marker(
            painter,
            rect,
        )

        painter.setPen(QColor("#b9c3d0"))

        font = QFont("Sans Serif", 8)
        painter.setFont(font)

        painter.drawText(
            QRectF(
                6,
                4,
                self.width() - 12,
                28,
            ),
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter,
            "NASA LRO / LOLA LDEM_64_FLOAT  |  "
            "64 pixels/degree  |  "
            "473.802 m/pixel at equator",
        )

        painter.drawText(
            QRectF(
                8,
                self.height() - 25,
                self.width() - 16,
                20,
            ),
            Qt.AlignmentFlag.AlignCenter,
            "Global elevation overview · Polar analysis uses "
            "dedicated 40 m LOLA datasets",
        )

        painter.end()
