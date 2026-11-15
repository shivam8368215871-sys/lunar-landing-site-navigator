import math
from pathlib import Path

import numpy as np

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from matplotlib import image as mpimg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MoonGlobeWidget(QWidget):
    """
    Interactive 3D Moon globe.

    Mouse controls:
        Left drag -> rotate
        Scroll    -> zoom
        Click     -> select lunar location

    Emits:
        location_selected(latitude, longitude)
    """

    location_selected = Signal(float, float)

    MOON_RADIUS = 1.0
    MARKER_RADIUS = 1.065

    # High enough to make the sphere smooth,
    # but safer for Qt/Wayland than an extremely
    # dense textured surface.
    MESH_LONGITUDE = 240
    MESH_LATITUDE = 120

    def __init__(self, parent=None):
        super().__init__(parent)

        self.latitude = None
        self.longitude = None

        self.dragging = False
        self.last_mouse_position = None
        self.mouse_moved = False

        self.figure = Figure(
            figsize=(6, 6),
            dpi=100,
        )

        self.figure.patch.set_facecolor("#11151c")

        self.canvas = FigureCanvasQTAgg(
            self.figure
        )

        self.ax = self.figure.add_subplot(
            111,
            projection="3d",
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self._configure_axes()
        self._create_moon()
        self._create_marker()

        self.canvas.mpl_connect(
            "button_press_event",
            self._mouse_press,
        )

        self.canvas.mpl_connect(
            "button_release_event",
            self._mouse_release,
        )

        self.canvas.mpl_connect(
            "motion_notify_event",
            self._mouse_move,
        )

        self.canvas.mpl_connect(
            "scroll_event",
            self._mouse_scroll,
        )

        self.canvas.draw()

    def _configure_axes(self):
        self.ax.set_facecolor("#11151c")

        self.ax.set_xlim(
            -1.1,
            1.1,
        )

        self.ax.set_ylim(
            -1.1,
            1.1,
        )

        self.ax.set_zlim(
            -1.1,
            1.1,
        )

        self.ax.set_box_aspect(
            (1, 1, 1)
        )

        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_zticks([])

        self.ax.grid(False)
        self.ax.set_axis_off()

    def _load_texture(self):
        """
        Load the NASA 4K lunar texture.

        The source texture remains 4096x2048,
        but it is sampled to the actual Moon
        mesh size before rendering.

        This avoids creating an unnecessarily
        huge collection of individual textured
        polygons.
        """

        texture_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "textures"
            / "moon_texture.tif"
        )

        if not texture_path.exists():
            raise FileNotFoundError(
                f"Moon texture not found: {texture_path}"
            )

        texture = np.asarray(
            mpimg.imread(texture_path)
        )

        if texture.ndim == 2:
            texture = np.stack(
                [texture, texture, texture],
                axis=-1,
            )

        if texture.shape[-1] == 4:
            texture = texture[:, :, :3]

        # Convert integer textures to 0..1.
        if np.issubdtype(
            texture.dtype,
            np.integer,
        ):
            max_value = np.iinfo(
                texture.dtype
            ).max

            texture = (
                texture.astype(
                    np.float32
                )
                / float(max_value)
            )

        else:
            texture = texture.astype(
                np.float32
            )

            maximum = float(
                texture.max()
            )

            if maximum > 1.0:
                if maximum <= 255.0:
                    texture /= 255.0
                else:
                    texture /= 65535.0

        texture = np.clip(
            texture,
            0.0,
            1.0,
        )

        print(
            "Moon texture loaded:",
            texture.shape,
            "dtype:",
            texture.dtype,
        )

        return texture

    def _create_moon(self):
        """
        Create a smooth spherical Moon and map
        the NASA equirectangular texture onto it.
        """

        # -------------------------------------------------
        # 1. Create Moon geometry
        # -------------------------------------------------

        u = np.linspace(
            -math.pi,
            math.pi,
            self.MESH_LONGITUDE,
        )

        v = np.linspace(
            -math.pi / 2,
            math.pi / 2,
            self.MESH_LATITUDE,
        )

        uu, vv = np.meshgrid(
            u,
            v,
        )

        x = (
            self.MOON_RADIUS
            * np.cos(vv)
            * np.cos(uu)
        )

        y = (
            self.MOON_RADIUS
            * np.cos(vv)
            * np.sin(uu)
        )

        z = (
            self.MOON_RADIUS
            * np.sin(vv)
        )

        # -------------------------------------------------
        # 2. Load NASA texture
        # -------------------------------------------------

        texture = self._load_texture()

        texture_height = (
            texture.shape[0]
        )

        texture_width = (
            texture.shape[1]
        )

        # -------------------------------------------------
        # 3. Sample texture at polygon centers
        #
        # This is important.
        #
        # Instead of assigning a texture pixel to
        # every vertex, calculate the UV coordinate
        # for the center of every surface polygon.
        # -------------------------------------------------

        u_centers = (
            u[:-1] + u[1:]
        ) / 2.0

        v_centers = (
            v[:-1] + v[1:]
        ) / 2.0

        uu_center, vv_center = (
            np.meshgrid(
                u_centers,
                v_centers,
            )
        )

        longitude_fraction = (
            (uu_center + math.pi)
            / (2.0 * math.pi)
        )

        latitude_fraction = (
            (math.pi / 2.0 - vv_center)
            / math.pi
        )

        texture_x = np.clip(
            (
                longitude_fraction
                * (texture_width - 1)
            ).astype(np.int32),
            0,
            texture_width - 1,
        )

        texture_y = np.clip(
            (
                latitude_fraction
                * (texture_height - 1)
            ).astype(np.int32),
            0,
            texture_height - 1,
        )

        colors = texture[
            texture_y,
            texture_x,
        ]

        # -------------------------------------------------
        # 4. Render the Moon
        # -------------------------------------------------

        self.ax.plot_surface(
            x,
            y,
            z,
            rstride=1,
            cstride=1,
            facecolors=colors,
            shade=False,
            linewidth=0,
            edgecolor="none",
            antialiased=False,
        )

    def _create_marker(self):
        self.marker = self.ax.scatter(
            [],
            [],
            [],
            s=260,
            color="#ff3b30",
            edgecolors="white",
            linewidths=2.5,
            depthshade=False,
        )

    def _coordinates_to_xyz(
        self,
        latitude: float,
        longitude: float,
        radius: float,
    ):
        lat = math.radians(latitude)
        lon = math.radians(longitude)

        x = (
            radius
            * math.cos(lat)
            * math.cos(lon)
        )

        y = (
            radius
            * math.cos(lat)
            * math.sin(lon)
        )

        z = (
            radius
            * math.sin(lat)
        )

        return x, y, z

    def set_location(
        self,
        latitude: float,
        longitude: float,
    ):
        latitude = float(latitude)
        longitude = float(longitude)

        self.latitude = latitude
        self.longitude = longitude

        x, y, z = self._coordinates_to_xyz(
            latitude,
            longitude,
            self.MARKER_RADIUS,
        )

        self.marker._offsets3d = (
            np.array([x]),
            np.array([y]),
            np.array([z]),
        )

        self.marker.stale = True

        self.canvas.draw_idle()

    def clear_location(self):
        self.latitude = None
        self.longitude = None

        self.marker._offsets3d = (
            np.array([]),
            np.array([]),
            np.array([]),
        )

        self.marker.stale = True

        self.canvas.draw_idle()

    def _mouse_press(self, event):
        if event.button != 1:
            return

        self.dragging = True
        self.mouse_moved = False

        if (
            event.x is not None
            and event.y is not None
        ):
            self.last_mouse_position = (
                event.x,
                event.y,
            )

    def _mouse_release(self, event):
        if event.button != 1:
            return

        was_dragging = self.dragging

        self.dragging = False
        self.last_mouse_position = None

        if (
            was_dragging
            and not self.mouse_moved
        ):
            self._select_from_screen(event)

    def _mouse_move(self, event):
        if not self.dragging:
            return

        if (
            event.x is None
            or event.y is None
        ):
            return

        if self.last_mouse_position is None:
            self.last_mouse_position = (
                event.x,
                event.y,
            )
            return

        last_x, last_y = (
            self.last_mouse_position
        )

        dx = event.x - last_x
        dy = event.y - last_y

        if (
            abs(dx) > 1
            or abs(dy) > 1
        ):
            self.mouse_moved = True

        self.last_mouse_position = (
            event.x,
            event.y,
        )

        elevation = self.ax.elev
        azimuth = self.ax.azim

        azimuth -= dx * 0.5
        elevation += dy * 0.5

        elevation = max(
            -89,
            min(89, elevation),
        )

        self.ax.view_init(
            elev=elevation,
            azim=azimuth,
        )

        self.canvas.draw_idle()

    def _mouse_scroll(self, event):
        if event.button == "up":
            factor = 0.90

        elif event.button == "down":
            factor = 1.10

        else:
            return

        self.ax.set_xlim(
            self._scaled_limits(
                self.ax.get_xlim(),
                factor,
            )
        )

        self.ax.set_ylim(
            self._scaled_limits(
                self.ax.get_ylim(),
                factor,
            )
        )

        self.ax.set_zlim(
            self._scaled_limits(
                self.ax.get_zlim(),
                factor,
            )
        )

        self.canvas.draw_idle()

    @staticmethod
    def _scaled_limits(
        limits,
        factor,
    ):
        center = (
            limits[0]
            + limits[1]
        ) / 2

        half = (
            limits[1]
            - limits[0]
        ) / 2

        half *= factor

        return (
            center - half,
            center + half,
        )

    def _select_from_screen(self, event):
        """
        Convert a screen click into a point
        on the visible Moon.
        """

        if (
            event.x is None
            or event.y is None
        ):
            return

        width = self.canvas.width()
        height = self.canvas.height()

        if (
            width <= 0
            or height <= 0
        ):
            return

        center_x = width / 2
        center_y = height / 2

        radius = (
            min(width, height)
            * 0.36
        )

        dx = (
            event.x
            - center_x
        )

        dy = (
            center_y
            - event.y
        )

        nx = dx / radius
        ny = dy / radius

        distance_squared = (
            nx * nx
            + ny * ny
        )

        if distance_squared > 1.0:
            return

        nz = math.sqrt(
            1.0
            - distance_squared
        )

        point = np.array(
            [nx, ny, nz],
            dtype=float,
        )

        point /= np.linalg.norm(
            point
        )

        latitude = math.degrees(
            math.asin(point[2])
        )

        longitude = math.degrees(
            math.atan2(
                point[1],
                point[0],
            )
        )

        self.set_location(
            latitude,
            longitude,
        )

        self.location_selected.emit(
            latitude,
            longitude,
        )
