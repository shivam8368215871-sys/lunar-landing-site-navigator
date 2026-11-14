import math

from PySide6.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class EarthMoonPlot(QWidget):
    """
    Earth/Moon geometry visualization.

    The widget accepts a list of Earth positions in a
    Moon-centered coordinate system.

    positions:
        [(x, y), (x, y), ...]
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure(
            figsize=(6, 4),
            facecolor="#0b1120",
        )

        self.canvas = FigureCanvasQTAgg(self.figure)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self.plot_positions([])

    def plot_positions(self, positions):
        self.figure.clear()

        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#0b1120")

        if positions:
            xs = [point[0] for point in positions]
            ys = [point[1] for point in positions]

            ax.plot(
                xs,
                ys,
                color="#38bdf8",
                linewidth=2,
                alpha=0.9,
            )

            ax.scatter(
                xs[0],
                ys[0],
                color="#facc15",
                s=80,
                zorder=5,
            )

            ax.scatter(
                [0],
                [0],
                color="#94a3b8",
                s=180,
                zorder=5,
            )

            ax.text(
                0,
                0,
                "  MOON",
                color="#e5e7eb",
                fontsize=9,
                verticalalignment="center",
            )

            ax.text(
                xs[0],
                ys[0],
                "  EARTH",
                color="#facc15",
                fontsize=9,
                verticalalignment="center",
            )

            max_range = max(
                max(abs(x) for x in xs),
                max(abs(y) for y in ys),
                1.0,
            )

            margin = max_range * 0.15

            ax.set_xlim(
                -max_range - margin,
                max_range + margin,
            )

            ax.set_ylim(
                -max_range - margin,
                max_range + margin,
            )

        else:
            ax.text(
                0.5,
                0.5,
                "Earth–Moon geometry",
                transform=ax.transAxes,
                color="#64748b",
                ha="center",
                va="center",
            )

        ax.set_xlabel(
            "X — Moon-centered frame",
            color="#64748b",
            fontsize=8,
        )

        ax.set_ylabel(
            "Y — Moon-centered frame",
            color="#64748b",
            fontsize=8,
        )

        ax.tick_params(
            colors="#64748b",
            labelsize=7,
        )

        for spine in ax.spines.values():
            spine.set_color("#263244")

        ax.grid(
            True,
            color="#1e293b",
            alpha=0.6,
        )

        self.figure.tight_layout()
        self.canvas.draw()
