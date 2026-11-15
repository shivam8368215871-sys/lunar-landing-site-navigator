from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout


class LunarTimeSeriesPlot(QWidget):
    """Matplotlib plot for real Sun/Earth elevation and LOLA horizons."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure(figsize=(8, 4.5))
        self.canvas = FigureCanvasQTAgg(self.figure)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def clear(self):
        self.figure.clear()
        self.canvas.draw_idle()

    def plot(self, results):
        self.figure.clear()

        axes = self.figure.add_subplot(111)

        times = [result.time for result in results]

        sun_elevation = [
            result.sun.elevation
            for result in results
        ]

        earth_elevation = [
            result.earth.elevation
            for result in results
        ]

        sun_horizon = [
            result.sun.terrain_horizon_elevation
            for result in results
        ]

        earth_horizon = [
            result.earth.terrain_horizon_elevation
            for result in results
        ]

        axes.plot(
            times,
            sun_elevation,
            marker="o",
            markersize=3,
            linewidth=1.8,
            label="Sun elevation",
        )

        axes.plot(
            times,
            earth_elevation,
            marker="o",
            markersize=3,
            linewidth=1.8,
            label="Earth elevation",
        )

        if all(value is not None for value in sun_horizon):
            axes.plot(
                times,
                sun_horizon,
                linestyle="--",
                linewidth=1.2,
                label="Sun terrain horizon",
            )

        if all(value is not None for value in earth_horizon):
            axes.plot(
                times,
                earth_horizon,
                linestyle="--",
                linewidth=1.2,
                label="Earth terrain horizon",
            )

        axes.axhline(
            0.0,
            linewidth=1.0,
            linestyle=":",
            label="Geometric horizon",
        )

        axes.set_title(
            "7-Day Lunar Mission Timeline"
        )

        axes.set_ylabel(
            "Elevation (degrees)"
        )

        axes.set_xlabel(
            "UTC"
        )

        axes.grid(
            True,
            alpha=0.25,
        )

        axes.legend(
            loc="best"
        )

        self.figure.autofmt_xdate()

        self.figure.tight_layout()

        self.canvas.draw_idle()
