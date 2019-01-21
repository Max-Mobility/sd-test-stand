from PyQt5 import QtGui
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QVBoxLayout, QVBoxLayout, QMessageBox, QErrorMessage, QScrollArea, QSizePolicy)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QSize, Qt

import resource
from progress import ProgressBar

class BasePage(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._pager = None
        self.nextEnabled = True
        self.previousEnabled = True
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))

        self.setStyleSheet("QLabel {font: 20pt}")

        self.labels = []
        self.picture = None

    @pyqtSlot()
    def onEnter(self):
        pass

    def setPager(self, pager):
        self._pager = pager

    def getButtonHeight(self):
        if self._pager is not None:
            return self._pager.getButtonHeight()
        else:
            return 100

    @pyqtSlot()
    def onExit(self):
        pass

    def getPictureSize(self):
        s = self.size() - QSize(0, self.getButtonHeight())
        for l in self.labels:
            s -= QSize(0, l.size().height())
        return QSize(max(400, s.width()), max(400, s.height()))

    def resizeEvent(self, event):
        if self.picture is not None:
            i = self.layout.indexOf(self.picture)
            self.layout.removeWidget(self.picture)
            self.picture.setParent(None)
            self.picture = QLabel(self)
            self.picture.setPixmap(self.pixMap.scaled(self.getPictureSize(), Qt.KeepAspectRatio))
            self.layout.insertWidget(i, self.picture)

class StartPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.previousEnabled = False
        title = QLabel("Welcome to SmartDrive Testing")
        self.labels = [title]
        self.layout.addWidget(title)

    @pyqtSlot()
    def onEnter(self):
        super().finished.emit()

class TestPage(BasePage):
    start = pyqtSignal()
    stop = pyqtSignal()

    doubleTap = pyqtSignal()
    setLoadPercent = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.nextEnabled = False

        self.load = 0
        self.setLoadPercent.emit(self.load)

        title = QLabel("Test Controls")
        self.speedLabel = QLabel("QEP Speed: 0 mph")
        self.progressBar = ProgressBar()
        self.increaseLoadButton = QPushButton("Increase Load")
        self.increaseLoadButton.clicked.connect(self.increaseLoad)
        self.decreaseLoadButton = QPushButton("Decrease Load")
        self.decreaseLoadButton.clicked.connect(self.decreaseLoad)
        self.zeroLoadButton = QPushButton("Zero Load")
        self.zeroLoadButton.clicked.connect(self.zeroLoad)
        self.doubleTapButton = QPushButton("Double Tap")
        self.doubleTapButton.clicked.connect(self.performDoubleTap)

        self.labels = [title,
                       self.speedLabel,
                       self.progressBar,
                       self.increaseLoadButton,
                       self.decreaseLoadButton,
                       self.zeroLoadButton,
                       self.doubleTapButton]

        self.layout.addWidget(title)
        self.layout.addWidget(self.speedLabel)
        self.layout.addWidget(self.progressBar)
        self.layout.addWidget(self.increaseLoadButton)
        self.layout.addWidget(self.decreaseLoadButton)
        self.layout.addWidget(self.zeroLoadButton)
        self.layout.addWidget(self.doubleTapButton)

    @pyqtSlot(float)
    def updateQepSpeed(self, speed):
        mph = (24.5 * speed / 4000.0) # inches per second
        mph = mph / 12.0 / 5280.0 # miles per second
        mph = mph * 60 * 60 # miles per hour
        self.speedLabel.setText("QEP Speed: {0:.2f} mph".format(mph))

    @pyqtSlot()
    def performDoubleTap(self):
        self.doubleTap.emit()

    @pyqtSlot()
    def increaseLoad(self):
        self.load += 1
        if self.load > 100: self.load = 100
        self.setLoadPercent.emit(self.load)

    @pyqtSlot()
    def decreaseLoad(self):
        self.load -= 1
        if self.load < 0: self.load = 0
        self.setLoadPercent.emit(self.load)

    @pyqtSlot()
    def zeroLoad(self):
        self.load = 0
        self.setLoadPercent.emit(self.load)

    @pyqtSlot(float)
    def updateParticleLoad(self, percent):
        percent = percent*100
        self.progressBar.setProgress(percent, "Particle brake load: {0:.2f} %".format(percent))


class EndPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.nextEnabled = False

        self.pixMap = QtGui.QPixmap(resource.path('images/runMX2+.jpg'))

        title = QLabel("Set the MX2+ DIP switches for running the firmware as shown below. \nThen power-cycle the SmartDrive.")
        title.setWordWrap(True)

        note = QLabel("NOTE: if you need to limit the speed, set DIP 7 OFF. For other configuration settings, please check out the 'Help' menu of this program.")
        note.setWordWrap(True)

        self.labels = [title, note]

        self.picture = QLabel(self)
        self.picture.setPixmap(self.pixMap.scaled(self.getPictureSize(), Qt.KeepAspectRatio))

        self.layout.addWidget(title)
        self.layout.addWidget(note)
        self.layout.addWidget(self.picture)

    @pyqtSlot()
    def onEnter(self):
        super().finished.emit()

