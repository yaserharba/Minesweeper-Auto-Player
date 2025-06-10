from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRect
import keyboard
import sys
import json

class TransparentSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Select Area')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.start = None
        self.end = None
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end = self.start
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.update()
        self.save_coordinates()
        QApplication.quit()

    def paintEvent(self, event):
        if self.start and self.end:
            qp = QPainter(self)
            qp.setPen(QPen(Qt.red, 2))
            qp.drawRect(QRect(self.start, self.end))

    def save_coordinates(self):
        x1 = min(self.start.x(), self.end.x())
        y1 = min(self.start.y(), self.end.y())
        x2 = max(self.start.x(), self.end.x())
        y2 = max(self.start.y(), self.end.y())
        coords = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
        print("Selected area:", coords)
        with open("selected_area.json", "w") as f:
            json.dump(coords, f, indent=4)

def select_area():
    app = QApplication(sys.argv)
    selector = TransparentSelector()
    selector.showFullScreen()
    app.exec_()

def wait_for_key(key='space'):
    print(f"Waiting for key '{key}' to be pressed...")
    keyboard.wait(key)
    print(f"Key '{key}' pressed, continuing...")

if __name__ == "__main__":
    wait_for_key('space')
    print("You pressed space, program continues...")
    select_area()