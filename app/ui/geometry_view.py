import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QFont
from PySide6.QtWidgets import QWidget


class LunarGeometryView(QWidget):
    """
    Visualize real Sun/Earth local lunar-horizon geometry.

    The diagram uses the actual elevation and azimuth calculated
    by the SPICE + lunar observer pipeline.

    Celestial bodies are drawn as directional markers only.
    They are not drawn to physical scale.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumHeight(360)

        self.sun = None
        self.earth = None

    def set_geometry(self, sun, earth):
        """
        Set Sun/Earth geometry dictionaries from AnalysisResult data.
        """
        self.sun = sun
        self.earth = earth
        self.update()

    def clear_geometry(self):
        self.sun = None
        self.earth = None
        self.update()

    def _polar_point(
        self,
        center,
        radius,
        azimuth_deg,
        elevation_deg,
    ):
        """
        Convert local lunar azimuth/elevation into diagram coordinates.

        Azimuth:
            0°   = North
            90°  = East
            180° = South
            270° = West

        Elevation:
            0°  = local horizon
            90° = zenith
            -90° = nadir

        The upper hemisphere is represented by the radial distance
        from the center: horizon is outer edge, zenith is center.
        """

        elevation = max(-90.0, min(90.0, elevation_deg))

        radial_fraction = (
            (90.0 - max(elevation, 0.0)) / 90.0
        )

        r = radius * radial_fraction

        azimuth = math.radians(azimuth_deg)

        x = center.x() + r * math.sin(azimuth)
        y = center.y() - r * math.cos(azimuth)

        return QPointF(x, y)

    def _draw_grid(self, painter, center, radius):
        painter.setPen(
            QPen(
                Qt.GlobalColor.lightGray,
                1,
                Qt.PenStyle.SolidLine,
            )
        )

        # Horizon.
        painter.drawEllipse(
            QRectF(
                center.x() - radius,
                center.y() - radius,
                radius * 2,
                radius * 2,
            )
        )

        # 30° elevation ring.
        ring30 = radius * (60.0 / 90.0)

        painter.drawEllipse(
            QRectF(
                center.x() - ring30,
                center.y() - ring30,
                ring30 * 2,
                ring30 * 2,
            )
        )

        # 60° elevation ring.
        ring60 = radius * (30.0 / 90.0)

        painter.drawEllipse(
            QRectF(
                center.x() - ring60,
                center.y() - ring60,
                ring60 * 2,
                ring60 * 2,
            )
        )

        # Cardinal directions.
        painter.setPen(
            QPen(
                Qt.GlobalColor.gray,
                1,
                Qt.PenStyle.DashLine,
            )
        )

        painter.drawLine(
            QPointF(center.x(), center.y() - radius),
            QPointF(center.x(), center.y() + radius),
        )

        painter.drawLine(
            QPointF(center.x() - radius, center.y()),
            QPointF(center.x() + radius, center.y()),
        )

        font = QFont()
        font.setBold(True)
        painter.setFont(font)

        painter.setPen(Qt.GlobalColor.black)

        painter.drawText(
            QPointF(center.x() - 5, center.y() - radius - 8),
            "N",
        )

        painter.drawText(
            QPointF(center.x() + radius + 8, center.y() + 5),
            "E",
        )

        painter.drawText(
            QPointF(center.x() - 5, center.y() + radius + 20),
            "S",
        )

        painter.drawText(
            QPointF(center.x() - radius - 20, center.y() + 5),
            "W",
        )

        painter.setFont(QFont())

        painter.setPen(Qt.GlobalColor.darkGray)

        painter.drawText(
            QPointF(center.x() + 8, center.y() - ring30 + 4),
            "30°",
        )

        painter.drawText(
            QPointF(center.x() + 8, center.y() - ring60 + 4),
            "60°",
        )

        painter.drawText(
            QPointF(center.x() + 8, center.y() - 8),
            "90°",
        )

    def _draw_body(
        self,
        painter,
        center,
        radius,
        data,
        label,
    ):
        if data is None:
            return

        elevation = data.get("elevation")
        azimuth = data.get("azimuth")

        if elevation is None or azimuth is None:
            return

        if elevation < 0.0:
            return

        point = self._polar_point(
            center,
            radius,
            azimuth,
            elevation,
        )

        # Use actual mission visibility for the line state.
        mission_visible = data.get(
            "terrain_visible"
        )

        if mission_visible is None:
            mission_visible = data.get(
                "visible",
                False,
            )

        if label == "Sun":
            body_pen = QPen(
                Qt.GlobalColor.darkYellow
                if mission_visible
                else Qt.GlobalColor.gray,
                3,
            )
            body_brush = QBrush(
                Qt.GlobalColor.yellow
                if mission_visible
                else Qt.GlobalColor.lightGray,
            )
        else:
            body_pen = QPen(
                Qt.GlobalColor.darkBlue
                if mission_visible
                else Qt.GlobalColor.gray,
                3,
            )
            body_brush = QBrush(
                Qt.GlobalColor.cyan
                if mission_visible
                else Qt.GlobalColor.lightGray,
            )

        painter.setPen(body_pen)
        painter.drawLine(center, point)

        painter.setBrush(body_brush)
        painter.drawEllipse(
            QRectF(
                point.x() - 9,
                point.y() - 9,
                18,
                18,
            )
        )

        painter.setPen(Qt.GlobalColor.black)

        painter.drawText(
            QPointF(
                point.x() + 12,
                point.y() + 4,
            ),
            label,
        )

        painter.setPen(Qt.GlobalColor.darkGray)

        painter.drawText(
            QPointF(
                point.x() + 12,
                point.y() + 20,
            ),
            (
                f"{elevation:.1f}° / "
                f"{azimuth:.1f}°"
            ),
        )

        horizon = data.get(
            "terrain_horizon_elevation"
        )

        if horizon is not None:
            painter.drawText(
                QPointF(
                    point.x() + 12,
                    point.y() + 36,
                ),
                f"Terrain horizon: {horizon:.1f}°",
            )

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.fillRect(
            self.rect(),
            Qt.GlobalColor.white,
        )

        if self.sun is None and self.earth is None:
            painter.setPen(Qt.GlobalColor.gray)

            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Run an analysis to display real Sun/Earth geometry.",
            )

            painter.end()
            return

        center = QPointF(
            self.width() / 2.0,
            self.height() / 2.0 + 10.0,
        )

        radius = min(
            self.width() * 0.35,
            self.height() * 0.38,
        )

        radius = max(radius, 90.0)

        self._draw_grid(
            painter,
            center,
            radius,
        )

        self._draw_body(
            painter,
            center,
            radius,
            self.sun,
            "Sun",
        )

        self._draw_body(
            painter,
            center,
            radius,
            self.earth,
            "Earth",
        )

        painter.setPen(Qt.GlobalColor.black)

        painter.drawText(
            QRectF(
                12,
                10,
                self.width() - 24,
                24,
            ),
            Qt.AlignmentFlag.AlignLeft,
            "Local Lunar Horizon — Real SPICE Geometry",
        )

        painter.setPen(Qt.GlobalColor.darkGray)

        painter.drawText(
            QRectF(
                12,
                self.height() - 32,
                self.width() - 24,
                20,
            ),
            Qt.AlignmentFlag.AlignLeft,
            "Center = Zenith | Outer circle = 0° horizon | "
            "Directions = local lunar azimuth",
        )

        painter.end()
