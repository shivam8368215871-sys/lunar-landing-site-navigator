from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class LandingConditionsView(QWidget):
    """
    Visual presentation of real mission-condition metrics.

    Science calculations remain in LunarAnalysisEngine.
    This widget only renders values supplied by AnalysisPage.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumHeight(250)

        self.illumination_value = self._value_label()
        self.contact_value = self._value_label()
        self.dark_period_value = self._value_label()
        self.blackout_value = self._value_label()

        self.suitability_value = self._value_label(font_size=28)

        self.illumination_points = self._detail_label()
        self.contact_points = self._detail_label()
        self.darkness_points = self._detail_label()

        self.sun_event = self._detail_label()
        self.earth_event = self._detail_label()

        self.illumination_bar = self._progress_bar()
        self.contact_bar = self._progress_bar()
        self.suitability_bar = self._progress_bar()

        self._build_ui()

    @staticmethod
    def _value_label(font_size=20):
        label = QLabel("--")
        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {font_size}px;
                font-weight: bold;
                padding: 6px;
            }}
            """
        )
        return label

    @staticmethod
    def _detail_label():
        label = QLabel("--")
        label.setWordWrap(True)
        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        return label

    @staticmethod
    def _progress_bar():
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(False)
        bar.setFixedHeight(10)
        return bar

    def _card(self, title, value, detail, progress=None):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d9dde5;
                border-radius: 8px;
                background: #ffffff;
            }
            """
        )

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)

        title_label = QLabel(title)
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        title_label.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #555d6b;
                border: none;
            }
            """
        )

        layout.addWidget(title_label)
        layout.addWidget(value)

        if progress is not None:
            layout.addWidget(progress)

        layout.addWidget(detail)

        return frame

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        metrics = QGridLayout()
        metrics.setSpacing(10)

        metrics.addWidget(
            self._card(
                "Illumination",
                self.illumination_value,
                self.illumination_points,
                self.illumination_bar,
            ),
            0,
            0,
        )

        metrics.addWidget(
            self._card(
                "Earth Contact",
                self.contact_value,
                self.contact_points,
                self.contact_bar,
            ),
            0,
            1,
        )

        metrics.addWidget(
            self._card(
                "Longest Dark Period",
                self.dark_period_value,
                QLabel(
                    "Terrain-aware sampled mission timeline"
                ),
            ),
            0,
            2,
        )

        metrics.addWidget(
            self._card(
                "Longest Earth Blackout",
                self.blackout_value,
                QLabel(
                    "Terrain-aware sampled mission timeline"
                ),
            ),
            0,
            3,
        )

        outer.addLayout(metrics)

        lower = QHBoxLayout()
        lower.setSpacing(10)

        suitability_card = QFrame()
        suitability_card.setFrameShape(
            QFrame.Shape.StyledPanel
        )
        suitability_card.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d9dde5;
                border-radius: 8px;
                background: #ffffff;
            }
            """
        )

        suitability_layout = QVBoxLayout(
            suitability_card
        )

        suitability_title = QLabel(
            "Landing-Site Suitability"
        )
        suitability_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        suitability_title.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #555d6b;
                border: none;
            }
            """
        )

        suitability_layout.addWidget(
            suitability_title
        )
        suitability_layout.addWidget(
            self.suitability_value
        )
        suitability_layout.addWidget(
            self.suitability_bar
        )
        suitability_layout.addWidget(
            self.illumination_points
        )
        suitability_layout.addWidget(
            self.contact_points
        )
        suitability_layout.addWidget(
            self.darkness_points
        )

        lower.addWidget(suitability_card)

        events_card = QFrame()
        events_card.setFrameShape(
            QFrame.Shape.StyledPanel
        )
        events_card.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d9dde5;
                border-radius: 8px;
                background: #ffffff;
            }
            """
        )

        events_layout = QVBoxLayout(events_card)

        events_title = QLabel(
            "Next Mission Events"
        )
        events_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        events_title.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #555d6b;
                border: none;
            }
            """
        )

        events_layout.addWidget(events_title)
        events_layout.addWidget(self.sun_event)
        events_layout.addWidget(self.earth_event)
        events_layout.addStretch()

        lower.addWidget(events_card)

        outer.addLayout(lower)

    def set_metrics(
        self,
        lighting_metrics: dict[str, float],
        communications_metrics: dict[str, float],
        suitability: dict[str, float],
        next_events: dict[str, object | None],
    ):
        illumination = float(
            lighting_metrics["illumination_percent"]
        )

        longest_dark = float(
            lighting_metrics["longest_dark_hours"]
        )

        contact_hours = float(
            communications_metrics["contact_hours"]
        )

        contact_percent = float(
            communications_metrics["contact_percent"]
        )

        longest_blackout = float(
            communications_metrics[
                "longest_blackout_hours"
            ]
        )

        score = float(
            suitability["score"]
        )

        illumination_points = float(
            suitability["illumination_points"]
        )

        contact_points = float(
            suitability["contact_points"]
        )

        darkness_points = float(
            suitability["darkness_points"]
        )

        self.illumination_value.setText(
            f"{illumination:.2f}%"
        )

        self.contact_value.setText(
            f"{contact_percent:.2f}%"
        )

        self.dark_period_value.setText(
            f"{longest_dark:.2f} h"
        )

        self.blackout_value.setText(
            f"{longest_blackout:.2f} h"
        )

        self.illumination_bar.setValue(
            max(0, min(100, round(illumination)))
        )

        self.contact_bar.setValue(
            max(0, min(100, round(contact_percent)))
        )

        self.suitability_value.setText(
            f"{score:.2f}/100"
        )

        self.suitability_bar.setValue(
            max(0, min(100, round(score)))
        )

        self.illumination_points.setText(
            f"Illumination: {illumination_points:.2f}/40"
        )

        self.contact_points.setText(
            f"Earth Contact: {contact_points:.2f}/35"
        )

        self.darkness_points.setText(
            f"Darkness: {darkness_points:.2f}/25"
        )

        self.sun_event.setText(
            self._event_text(
                "Sun",
                next_events.get(
                    "next_sun_event"
                ),
                next_events.get(
                    "next_sun_event_time"
                ),
                next_events.get(
                    "next_sun_countdown_hours"
                ),
            )
        )

        self.earth_event.setText(
            self._event_text(
                "Earth",
                next_events.get(
                    "next_earth_event"
                ),
                next_events.get(
                    "next_earth_event_time"
                ),
                next_events.get(
                    "next_earth_countdown_hours"
                ),
            )
        )

    @staticmethod
    def _event_text(
        target,
        event,
        event_time,
        countdown,
    ):
        if (
            event is None
            or event_time is None
            or countdown is None
        ):
            return (
                f"Next {target} Event: "
                "None in selected timeline"
            )

        return (
            f"Next {target} Event: {event}\n"
            f"in {float(countdown):.2f} hours — "
            f"{event_time.strftime('%Y-%m-%d %H:%M UTC')}"
        )

    def clear_metrics(self):
        self.illumination_value.setText("--")
        self.contact_value.setText("--")
        self.dark_period_value.setText("--")
        self.blackout_value.setText("--")
        self.suitability_value.setText("--/100")

        self.illumination_points.setText(
            "Illumination: --/40"
        )
        self.contact_points.setText(
            "Earth Contact: --/35"
        )
        self.darkness_points.setText(
            "Darkness: --/25"
        )

        self.illumination_bar.setValue(0)
        self.contact_bar.setValue(0)
        self.suitability_bar.setValue(0)

        self.sun_event.setText(
            "Next Sun Event: --"
        )
        self.earth_event.setText(
            "Next Earth Event: --"
        )
