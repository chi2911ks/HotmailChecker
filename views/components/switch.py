from PyQt5.QtWidgets import QWidget, QAbstractButton, QSizePolicy
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve, pyqtSignal, QSize
from PyQt5.QtGui import QPainter, QColor

class Switch(QAbstractButton):
    def __init__(self, parent=None, track_radius=12, thumb_radius=10):
        super().__init__(parent)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self._track_radius = track_radius
        self._thumb_radius = thumb_radius
        
        self._margin = 2
        self._base_offset = 0
        self._offset = self._base_offset
        
        self._animation = QPropertyAnimation(self, b"offset")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        self.setFixedSize(track_radius * 4, track_radius * 2)

    @pyqtProperty(float)
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self.update()

    def sizeHint(self):
        return QSize(self._track_radius * 4, self._track_radius * 2)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        r = self.rect()
        
        # Colors
        if self.isChecked():
            track_color = QColor("#3b82f6") # Primary blue
            thumb_color = QColor("#ffffff")
        else:
            # Safely check for is_dark_mode on the main window
            is_dark = getattr(self.window(), 'is_dark_mode', False)
            track_color = QColor("#30363d") if is_dark else QColor("#d1d5db")
            thumb_color = QColor("#ffffff")
            
        # Draw track
        p.setBrush(track_color)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(r, self._track_radius, self._track_radius)
        
        # Draw thumb
        thumb_pos = self._offset
        if not self._animation.state() == QPropertyAnimation.State.Running:
            thumb_pos = r.width() - self._thumb_radius * 2 - self._margin if self.isChecked() else self._margin
            
        p.setBrush(thumb_color)
        p.drawEllipse(int(thumb_pos), int(self._margin), int(self._thumb_radius * 2), int(self._thumb_radius * 2))

    def nextCheckState(self):
        super().nextCheckState()
        
        start = self._margin
        end = self.width() - self._thumb_radius * 2 - self._margin
        
        self._animation.setStartValue(start if self.isChecked() else end)
        self._animation.setEndValue(end if self.isChecked() else start)
        self._animation.start()
