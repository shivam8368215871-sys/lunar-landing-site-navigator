from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
    QComboBox,
    QPushButton,
)

from app.science.heatmap import calculate_visibility_heatmap
from app.ui.heatmap_view import VisibilityHeatmapView


class LunarMapView(QLabel):
    """
    Lightweight image-based lunar map.

    Displays a pre-rendered image and optionally draws
    the selected lunar location on top of it.
    """

    def __init__(self, image_path: Path, parent=None):
        super().__init__(parent)

        self.image_path = image_path
        self.latitude = None
        self.longitude = None

        self.base_pixmap = QPixmap(str(image_path))

        if self.base_pixmap.isNull():
            raise FileNotFoundError(
                f"Could not load lunar map: {image_path}"
            )

        self.setAlignment(Qt.AlignCenter)

        self.setMinimumSize(320, 320)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.setStyleSheet("""
            background: #10141b;
            border: 1px solid #303844;
        """)

    def set_location(self, latitude, longitude):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.update()

    def clear_location(self):
        self.latitude = None
        self.longitude = None
        self.update()

    def _coordinate_to_pixel(self):
        """
        Convert lunar coordinates to normalized coordinates matching
        the full 7584x7584 LOLA south-polar raster.

        The LOLA DEM uses 40 m pixels with the south pole at the
        raster center.  The PNG height map is generated directly
        from this complete raster, so the marker must use the same
        raster coordinates.
        """

        if (
            self.latitude is None
            or self.longitude is None
        ):
            return None

        import math

        lat = float(self.latitude)
        lon = float(self.longitude)

        if not -90.0 <= lat <= -85.0:
            return None

        # LOLA LDEM_85S_40M raster geometry from the PDS label.
        R = 1737.4
        PIXEL_SIZE_KM = 0.04
        RASTER_SIZE = 7584
        CENTER = 3791.5

        phi = math.radians(lat)
        lam = math.radians(lon)

        rho = (
            2.0
            * R
            * math.tan(
                math.pi / 4.0
                + phi / 2.0
            )
        )

        x = rho * math.sin(lam)
        y = -rho * math.cos(lam)

        # Convert projected south-polar coordinates to the
        # actual LOLA raster sample/line coordinates.
        sample = CENTER + x / PIXEL_SIZE_KM
        line = CENTER + y / PIXEL_SIZE_KM

        nx = sample / (RASTER_SIZE - 1)
        ny = line / (RASTER_SIZE - 1)

        nx = max(0.0, min(1.0, nx))
        ny = max(0.0, min(1.0, ny))

        return nx, ny

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        painter.fillRect(
            self.rect(),
            self.palette().window()
        )

        if self.base_pixmap.isNull():
            painter.end()
            return

        available = self.rect()

        scaled = self.base_pixmap.scaled(
            available.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        x = (
            available.width()
            - scaled.width()
        ) // 2

        y = (
            available.height()
            - scaled.height()
        ) // 2

        painter.drawPixmap(
            x,
            y,
            scaled,
        )

        normalized = self._coordinate_to_pixel()

        if normalized is not None:
            nx, ny = normalized

            marker_x = x + nx * scaled.width()
            marker_y = y + ny * scaled.height()

            painter.setPen(
                QPen(Qt.white, 3)
            )

            painter.setBrush(
                QBrush(Qt.red)
            )

            painter.drawEllipse(
                int(marker_x - 8),
                int(marker_y - 8),
                16,
                16,
            )

            painter.setPen(
                QPen(Qt.white, 1)
            )

            painter.drawLine(
                int(marker_x - 14),
                int(marker_y),
                int(marker_x + 14),
                int(marker_y),
            )

            painter.drawLine(
                int(marker_x),
                int(marker_y - 14),
                int(marker_x),
                int(marker_y + 14),
            )

        painter.end()


class LunarMapsWidget(QWidget):
    """
    Three-panel lunar visualization:

        1. Surface Map
        2. LOLA Height Map
        3. Analysis Heat Map

    The heat-map panel is intentionally prepared here but
    will be connected to the real landing-analysis score
    in the next step.
    """

    def __init__(self, engine=None, time_provider=None, parent=None):
        super().__init__(parent)

        self.engine = engine
        self.time_provider = time_provider

        root = Path(__file__).resolve().parents[2]

        maps_dir = (
            root
            / "assets"
            / "maps"
        )

        self.surface_map = LunarMapView(
            maps_dir
            / "moon_surface_map.png"
        )

        self.height_map = LunarMapView(
            maps_dir
            / "moon_height_map.png"
        )

        self.heat_map = VisibilityHeatmapView()

        self.heatmap_target = QComboBox()
        self.heatmap_target.addItems(["Sun", "Earth"])
        self.heatmap_target.currentTextChanged.connect(
            self._on_heatmap_target_changed
        )

        self.heatmap_generate_button = QPushButton(
            "Generate / Refresh"
        )
        self.heatmap_generate_button.clicked.connect(
            self.generate_heatmap
        )

        self.heatmap_status = QLabel(
            "Select Sun or Earth, then generate the map."
        )
        self.heatmap_status.setWordWrap(True)
        self.heatmap_status.setStyleSheet(
            "color: #b9c3d0; font-size: 11px; border: none;"
        )

        self.heatmap_content = QWidget()
        heatmap_layout = QVBoxLayout(self.heatmap_content)
        heatmap_layout.setContentsMargins(0, 0, 0, 0)
        heatmap_layout.setSpacing(5)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Target:"))
        controls.addWidget(self.heatmap_target, 1)
        controls.addWidget(self.heatmap_generate_button)
        heatmap_layout.addLayout(controls)
        heatmap_layout.addWidget(self.heat_map, 1)

        legend = QLabel(
            "<span style='color:#28be69'>●</span> Visible  "
            "<span style='color:#e14646'>●</span> Blocked  "
            "<span style='color:#828c9b'>●</span> Unavailable"
        )
        legend.setStyleSheet(
            "font-size: 11px; border: none;"
        )
        heatmap_layout.addWidget(legend)
        heatmap_layout.addWidget(self.heatmap_status)

        self._setup_ui()

    def _create_placeholder(self, text):
        label = QLabel(text)

        label.setAlignment(
            Qt.AlignCenter
        )

        label.setMinimumSize(
            300,
            300,
        )

        label.setStyleSheet("""
            background: #10141b;
            color: #8f9aaa;
            border: 1px solid #303844;
            font-size: 16px;
            font-weight: 600;
        """)

        return label

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            8,
            8,
            8,
            4,
        )

        main_layout.setSpacing(6)

        title = QLabel(
            "Lunar Surface Maps"
        )

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
        """)

        subtitle = QLabel(
            "Surface imagery, LOLA elevation, "
            "and landing-site analysis."
        )

        subtitle.setStyleSheet("""
            color: #9aa5b5;
            font-size: 13px;
        """)

        main_layout.addWidget(
            title
        )

        main_layout.addWidget(
            subtitle
        )

        maps_layout = QHBoxLayout()

        maps_layout.setSpacing(8)

        maps_layout.addWidget(
            self._panel(
                "Surface Map",
                self.surface_map,
            ),
            1,
        )

        maps_layout.addWidget(
            self._panel(
                "LOLA Height Map",
                self.height_map,
            ),
            1,
        )

        maps_layout.addWidget(
            self._panel(
                "Sun / Earth Terrain Visibility",
                self.heatmap_content,
            ),
            1,
        )

        main_layout.addLayout(
            maps_layout,
            1,
        )

        self.location_label = QLabel(
            "Selected location: --"
        )

        self.location_label.setStyleSheet("""
            color: #b9c3d0;
            font-size: 13px;
            padding: 6px;
        """)

        main_layout.addWidget(
            self.location_label
        )

    def _on_heatmap_target_changed(self, value):
        target = "sun" if value == "Sun" else "earth"
        self.heat_map.set_target(target)
        self._update_heatmap_status()

    def _update_heatmap_status(self):
        result = self.heat_map.result
        if result is None:
            return

        visible = 0
        blocked = 0
        unavailable = 0

        for cell in result.cells:
            value = getattr(
                cell,
                f"{self.heat_map.target}_visible",
            )
            if value is True:
                visible += 1
            elif value is False:
                blocked += 1
            else:
                unavailable += 1

        self.heatmap_status.setText(
            f"UTC: {result.analysis_time:%Y-%m-%d %H:%M:%S} | "
            f"Visible: {visible} | Blocked: {blocked} | "
            f"Unavailable: {unavailable}"
        )

    def generate_heatmap(self):
        """Calculate a real visibility grid using the shared engine."""
        if self.engine is None or self.time_provider is None:
            self.heatmap_status.setText(
                "Heatmap engine or UTC time provider is unavailable."
            )
            return

        self.heatmap_generate_button.setEnabled(False)
        self.heatmap_status.setText(
            "Calculating real SPICE and LOLA visibility..."
        )

        try:
            analysis_time = self.time_provider()
            result = calculate_visibility_heatmap(
                engine=self.engine,
                analysis_time=analysis_time,
                grid_size=32,
            )

            self.heat_map.set_result(result)

            self._update_heatmap_status()

        except Exception as exc:
            self.heatmap_status.setText(
                f"Heatmap calculation failed: {exc}"
            )
        finally:
            self.heatmap_generate_button.setEnabled(True)

    def _panel(self, title, widget):
        frame = QFrame()

        frame.setStyleSheet("""
            QFrame {
                background: #171c24;
                border: 1px solid #2d3542;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(frame)

        label = QLabel(title)

        label.setStyleSheet("""
            color: #ffffff;
            font-size: 14px;
            font-weight: 700;
            border: none;
        """)

        layout.addWidget(
            label
        )

        layout.addWidget(
            widget,
            1,
        )

        return frame

    def set_location(
        self,
        latitude: float,
        longitude: float,
    ):
        self.surface_map.set_location(
            latitude,
            longitude,
        )

        self.height_map.set_location(
            latitude,
            longitude,
        )
        self.heat_map.set_location(
            latitude,
            longitude,
        )

        self.location_label.setText(
            f"Selected location: "
            f"{latitude:.4f}°, "
            f"{longitude:.4f}°"
        )

    def clear_location(self):
        self.surface_map.clear_location()
        self.height_map.clear_location()
        self.heat_map.clear_location()

        self.location_label.setText(
            "Selected location: --"
        )
