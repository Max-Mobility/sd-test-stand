import glob
import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QComboBox, QApplication, QMainWindow, QStyleFactory, QDesktopWidget, QMessageBox, QErrorMessage, QFileDialog, QSplitter, QScrollArea)
from PyQt5.QtCore import QFileInfo, QFile, QProcess, QTimer, QBasicTimer, Qt, QObject, QRunnable, QThread, QThreadPool, pyqtSignal, pyqtSlot

import resource
import pages
from pager import Pager

from action import\
    Action

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC
from Adafruit_BBIO.Encoder import RotaryEncoder, eQEP2

class Programmer(QMainWindow):
    readParticleLoad = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.initIO()

    def initUI(self):
        QApplication.setStyle(QStyleFactory.create('Cleanlooks'))

        self.setStyleSheet("QLabel {font: 15pt} QPushButton {font: 15pt}")
        self.setWindowTitle('SmartDrive Test Stand')

        # Create the actions for the program
        exitAction = Action(resource.path('icons/toolbar/exit.png'), 'Exit Test Stand', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        aboutAction = Action(resource.path('icons/toolbar/about.png'), 'About', self)
        aboutAction.setStatusTip('About SmartDrive Test Stand')
        aboutAction.triggered.connect(self.about)

        # Set up the Menus for the program
        self.menubar_init()
        self.menubar_add_menu('&File')
        self.menu_add_action('&File', exitAction)

        self.menubar_add_menu('&Help')
        self.menu_add_action('&Help', aboutAction)

        # Set up the toolbars for the program
        self.toolbar_init()
        self.toolbar_create('toolbar1')
        self.toolbar_add_action('toolbar1', exitAction)

        # main UI
        self.startPage = pages.StartPage()
        self.testPage = pages.TestPage()
        self.endPage = pages.EndPage()

        self.pager = Pager()
        self.pager.addPage(self.startPage)
        self.pager.addPage(self.testPage)
        self.pager.addPage(self.endPage)

        # main controls
        '''
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.pager)
        self.scrollArea.setWidgetResizable(True)
        self.setCentralWidget(self.scrollArea)
        '''
        self.setCentralWidget(self.pager)
        self.setGeometry(0, 0, 1200, 1000)
        self.center()
        self.show()
        #self.setFixedSize(self.size())

    # smartdrive test stand functions
    def initIO(self):
        PWM.cleanup()

        # set up eQEP2 encoder for position feedback
        self.encoder = RotaryEncoder(eQEP2)
        print('Encoder enabled  ', self.encoder.enabled)
        print('Encoder frequency', self.encoder.frequency)
        print('Encoder position ', self.encoder.position)
        self.encoder.zero()

        # set up P8.13 PWM for Solenoid control
        self.solenoidPWM = "P8_13"
        # make sure it's not running
        PWM.stop(self.solenoidPWM)

        # set up P9.16 PWM for particle brake control
        self.particlePWM = "P9_16"
        PWM.start(self.particlePWM, 0, 2000, 0)

        # set up PX.YY ADC for particle brake current reading
        self.particleADC = "P9_36"
        ADC.setup()
        sense = ADC.read(self.particleADC)
        print('Particle current percentage:', sense)

        # wire up UI to IO functions
        self.testPage.doubleTap.connect(self.doubleTap)
        self.testPage.setLoadPercent.connect(self.setLoadPercent)
        self.readParticleLoad.connect(self.testPage.updateParticleLoad)

        # start timer for reading particle brake load
        self.adcTimer = QTimer()
        self.adcTimer.timeout.connect(self.adcReadTimeout)
        self.adcTimer.start(500)

    @pyqtSlot()
    def doubleTap(self):
        # stop the PWM if it's running
        PWM.stop(self.solenoidPWM)
        # start pwm at freq of 2 Hz
        PWM.start(self.solenoidPWM, 30, 3, 0)
        # create one-shot timer for canceling the pwm
        QTimer.singleShot(900, lambda : PWM.stop(self.solenoidPWM))

    @pyqtSlot(int)
    def setLoadPercent(self, percent):
        PWM.set_duty_cycle(self.particlePWM, percent)

    @pyqtSlot()
    def adcReadTimeout(self):
        sense = ADC.read(self.particleADC)
        self.readParticleLoad.emit(sense)

    # general functions
    def about(self):
        msg = '''
SmartDrive Test Stand

This program walks the user through the testing process for the SmartDrive MX2+.
        '''
        QMessageBox.information(
            self, 'About', msg.replace('\n', '<br>'),
            QMessageBox.Ok, QMessageBox.Ok)

    # window functions
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'Quit',
            'Sure you want to quit?', QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            PWM.cleanup()
        else:
            event.ignore()

    from menubar import \
        menubar_init, \
        menubar_add_menu, \
        menu_add_action

    from toolbar import \
        toolbar_init, \
        toolbar_create, \
        toolbar_add_action, \
        toolbar_add_widget, \
        toolbar_add_separator, \
        toolbar_remove

    from action import \
        action_init, \
        action_create

    from context_menu import \
        context_menu_init, \
        context_menu_create, \
        context_menu_add_action
