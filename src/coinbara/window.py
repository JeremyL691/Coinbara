from __future__ import annotations

import math
import random
from dataclasses import dataclass

from PySide6 import QtCore, QtGui, QtWidgets

from .assets import asset_path
from .flip_engine import FlipEngine, FlipSide


RESULT_TEXT: dict[FlipSide, tuple[str, str]] = {
    "heads": ("Heads", "Coinbara chose heads."),
    "tails": ("Tails", "Coinbara chose tails."),
}


@dataclass
class Sparkle:
    x: float
    y: float
    radius: float
    hue: QtGui.QColor


class CoinWidget(QtWidgets.QWidget):
    finished = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(340, 340)
        self.setMaximumSize(380, 380)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.heads = QtGui.QPixmap(str(asset_path("coin_heads.png")))
        self.tails = QtGui.QPixmap(str(asset_path("coin_tails.png")))
        self.current_side: FlipSide = "heads"
        self.target_side: FlipSide = "heads"
        self.frame = 0
        self.total_frames = 46
        self._sparkles: list[Sparkle] = []
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(24)
        self._timer.timeout.connect(self._tick)

    def start_flip(self, target_side: FlipSide) -> bool:
        if self._timer.isActive():
            return False
        self.target_side = target_side
        self.frame = 0
        self._sparkles = self._make_sparkles()
        self._timer.start()
        self.update()
        return True

    def _make_sparkles(self) -> list[Sparkle]:
        palette = [
            QtGui.QColor("#F5B85A"),
            QtGui.QColor("#F28482"),
            QtGui.QColor("#6FC7B2"),
            QtGui.QColor("#FFF1B8"),
        ]
        return [
            Sparkle(
                x=random.uniform(-0.48, 0.48),
                y=random.uniform(-0.55, 0.2),
                radius=random.uniform(2.2, 5.8),
                hue=random.choice(palette),
            )
            for _ in range(24)
        ]

    def _tick(self) -> None:
        self.frame += 1
        if self.frame >= self.total_frames:
            self._timer.stop()
            self.current_side = self.target_side
            self.frame = self.total_frames
            self.update()
            self.finished.emit(self.target_side)
            return

        self.current_side = self.target_side if self.frame > self.total_frames * 0.72 else (
            "tails" if self.frame % 4 < 2 else "heads"
        )
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        del event
        painter = QtGui.QPainter(self)
        painter.setRenderHints(
            QtGui.QPainter.Antialiasing
            | QtGui.QPainter.SmoothPixmapTransform
            | QtGui.QPainter.TextAntialiasing
        )

        rect = self.rect()
        center = QtCore.QPointF(rect.center())
        progress = min(1.0, self.frame / self.total_frames) if self.total_frames else 1.0
        finished = not self._timer.isActive() and progress >= 1.0
        toss = 0.0 if finished else math.sin(progress * math.pi)
        spin = 1.0 if finished else abs(math.cos(progress * math.pi * 6.0))
        squash = 1.0 if finished else max(0.42, spin)
        coin_size = min(rect.width(), rect.height()) * (0.76 + toss * 0.06)
        coin_w = coin_size * squash
        coin_h = coin_size
        y_offset = -76 * toss

        shadow_alpha = int(68 - toss * 40)
        painter.setBrush(QtGui.QColor(112, 91, 62, max(12, shadow_alpha)))
        painter.setPen(QtCore.Qt.NoPen)
        shadow_w = coin_size * (0.72 - toss * 0.18)
        shadow_rect = QtCore.QRectF(
            center.x() - shadow_w / 2,
            center.y() + coin_size * 0.33,
            shadow_w,
            coin_size * 0.13,
        )
        painter.drawEllipse(shadow_rect)

        self._paint_sparkles(painter, center, coin_size, progress)

        pixmap = self.heads if self.current_side == "heads" else self.tails
        target = QtCore.QRectF(
            center.x() - coin_w / 2,
            center.y() - coin_h / 2 + y_offset,
            coin_w,
            coin_h,
        )
        painter.drawPixmap(target, pixmap, pixmap.rect())

        if toss > 0.04:
            glow = QtGui.QRadialGradient(target.center(), coin_size * 0.54)
            glow.setColorAt(0.0, QtGui.QColor(255, 245, 190, int(82 * toss)))
            glow.setColorAt(0.56, QtGui.QColor(255, 214, 126, int(30 * toss)))
            glow.setColorAt(1.0, QtGui.QColor(255, 214, 126, 0))
            painter.setBrush(glow)
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(target.adjusted(-22, -22, 22, 22))

    def _paint_sparkles(
        self,
        painter: QtGui.QPainter,
        center: QtCore.QPointF,
        coin_size: float,
        progress: float,
    ) -> None:
        if not self._timer.isActive() and progress >= 1.0:
            return

        alpha_curve = math.sin(min(1.0, progress) * math.pi)
        painter.setPen(QtCore.Qt.NoPen)
        for sparkle in self._sparkles:
            color = QtGui.QColor(sparkle.hue)
            color.setAlpha(int(185 * alpha_curve))
            painter.setBrush(color)
            drift = progress * 38
            x = center.x() + sparkle.x * coin_size
            y = center.y() + sparkle.y * coin_size - drift
            r = sparkle.radius * (0.65 + alpha_curve)
            painter.drawEllipse(QtCore.QPointF(x, y), r, r)


class BackgroundWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.background = QtGui.QPixmap(str(asset_path("app_background.png")))

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        del event
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        if not self.background.isNull():
            scaled = self.background.scaled(
                self.size(),
                QtCore.Qt.KeepAspectRatioByExpanding,
                QtCore.Qt.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        painter.fillRect(self.rect(), QtGui.QColor(255, 250, 238, 122))


class CoinFlipWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.engine = FlipEngine()

        self.setWindowTitle("Coinbara")
        self.setFixedSize(520, 700)
        self.setWindowIcon(QtGui.QIcon(str(asset_path("app_icon.ico"))))

        self.root = BackgroundWidget(self)
        self.root.setObjectName("root")
        self.root.setGeometry(self.rect())

        self._build_ui()
        self._apply_theme()
        self._center_on_screen()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.root.setGeometry(self.rect())

    def _build_ui(self) -> None:
        root_layout = QtWidgets.QVBoxLayout(self.root)
        root_layout.setContentsMargins(34, 24, 34, 28)
        root_layout.setSpacing(14)

        top = QtWidgets.QHBoxLayout()
        top.setSpacing(8)

        title_box = QtWidgets.QVBoxLayout()
        title_box.setSpacing(2)
        self.title = QtWidgets.QLabel("Coinbara")
        self.title.setObjectName("title")
        self.subtitle = QtWidgets.QLabel("A cozy coin for tiny decisions")
        self.subtitle.setObjectName("subtitle")
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        top.addLayout(title_box, 1)
        root_layout.addLayout(top)

        self.coin = CoinWidget()
        self.coin.finished.connect(self._finish_flip)
        root_layout.addWidget(self.coin, alignment=QtCore.Qt.AlignHCenter)

        self.result_label = QtWidgets.QLabel("Ready")
        self.result_label.setObjectName("resultLabel")
        self.result_label.setAlignment(QtCore.Qt.AlignCenter)
        self.result_subtitle = QtWidgets.QLabel("Tap Flip and let Coinbara decide.")
        self.result_subtitle.setObjectName("resultSubtitle")
        self.result_subtitle.setAlignment(QtCore.Qt.AlignCenter)
        root_layout.addWidget(self.result_label)
        root_layout.addWidget(self.result_subtitle)

        self.flip_button = QtWidgets.QPushButton("Flip")
        self.flip_button.setObjectName("flipButton")
        self.flip_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.flip_button.clicked.connect(self._start_flip)
        root_layout.addWidget(self.flip_button)

        stats = QtWidgets.QHBoxLayout()
        stats.setSpacing(10)
        self.heads_stat = QtWidgets.QLabel("Heads 0")
        self.tails_stat = QtWidgets.QLabel("Tails 0")
        for label in (self.heads_stat, self.tails_stat):
            label.setObjectName("statPill")
            label.setAlignment(QtCore.Qt.AlignCenter)
            stats.addWidget(label)
        root_layout.addLayout(stats)

        history_row = QtWidgets.QHBoxLayout()
        history_row.setSpacing(10)
        self.history_label = QtWidgets.QLabel("History: -")
        self.history_label.setObjectName("history")
        history_row.addWidget(self.history_label, 1)
        self.reset_button = QtWidgets.QPushButton("Reset")
        self.reset_button.setObjectName("resetButton")
        self.reset_button.clicked.connect(self._reset)
        history_row.addWidget(self.reset_button)
        root_layout.addLayout(history_row)

    def _start_flip(self) -> None:
        result = self.engine.begin_flip()
        if result is None:
            return
        self.flip_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.result_label.setText("Flipping...")
        self.result_subtitle.setText("Coinbara is thinking it over.")
        self.coin.start_flip(result)

    def _finish_flip(self, result: str) -> None:
        side = result if result in ("heads", "tails") else "heads"
        self.engine.finish_flip(side)  # type: ignore[arg-type]
        headline, subtitle = RESULT_TEXT[side]  # type: ignore[index]
        self.result_label.setText(headline)
        self.result_subtitle.setText(subtitle)
        self.flip_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self._update_stats()

    def _update_stats(self) -> None:
        self.heads_stat.setText(f"Heads {self.engine.heads_count}")
        self.tails_stat.setText(f"Tails {self.engine.tails_count}")
        symbols = ["H" if side == "heads" else "T" for side in self.engine.history]
        self.history_label.setText(f"History: {'  '.join(symbols) if symbols else '-'}")

    def _reset(self) -> None:
        self.engine.reset()
        self.coin.current_side = "heads"
        self.coin.update()
        self.result_label.setText("Ready")
        self.result_subtitle.setText("Tap Flip and let Coinbara decide.")
        self._update_stats()

    def _apply_theme(self) -> None:
        accent = "#5BB9A8"
        accent_dark = "#277E72"
        soft = "rgba(255, 255, 255, 175)"
        text = "#26403B"

        self.setStyleSheet(
            f"""
            QWidget {{
                color: {text};
                font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
                letter-spacing: 0px;
            }}
            QLabel#title {{
                font-size: 28px;
                font-weight: 800;
            }}
            QLabel#subtitle {{
                font-size: 13px;
                color: rgba(38, 64, 59, 175);
            }}
            QLabel#resultLabel {{
                font-size: 44px;
                font-weight: 850;
                min-height: 56px;
            }}
            QLabel#resultSubtitle {{
                font-size: 17px;
                min-height: 30px;
                color: rgba(38, 64, 59, 190);
            }}
            QPushButton {{
                border: 0;
                border-radius: 8px;
                padding: 10px 14px;
                background: {soft};
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 218);
            }}
            QPushButton:pressed {{
                background: rgba(236, 230, 214, 222);
            }}
            QPushButton#flipButton {{
                min-height: 58px;
                border-radius: 8px;
                background: {accent};
                color: white;
                font-size: 22px;
                font-weight: 850;
            }}
            QPushButton#flipButton:hover {{
                background: {accent_dark};
            }}
            QPushButton#flipButton:disabled {{
                background: rgba(119, 142, 132, 150);
            }}
            QPushButton#toolButton {{
                min-width: 72px;
            }}
            QPushButton#resetButton {{
                min-width: 74px;
            }}
            QLabel#statPill, QLabel#history {{
                border-radius: 8px;
                padding: 11px 14px;
                background: rgba(255, 255, 255, 162);
                font-size: 14px;
                font-weight: 700;
            }}
            """
        )

    def _center_on_screen(self) -> None:
        screen = QtGui.QGuiApplication.primaryScreen()
        if not screen:
            return
        available = screen.availableGeometry()
        self.move(available.center() - self.rect().center())
