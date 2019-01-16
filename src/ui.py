import glob
import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QComboBox, QApplication, QMainWindow, QStyleFactory, QDesktopWidget, QMessageBox, QErrorMessage, QFileDialog, QSplitter, QScrollArea)
from PyQt5.QtCore import QFileInfo, QFile, QProcess, QTimer, QBasicTimer, Qt, QObject, QRunnable, QThread, QThreadPool, pyqtSignal

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
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initIO()

    def initIO(self):
        # set up eQEP2 encoder for position feedback
        self.encoder = RotaryEncoder(eQEP2)
        print('position', self.encoder.position)
        self.encoder.zero()

        # set up P8.13 PWM for Solenoid control
        self.solenoidPWM = "P8_13"
        PWM.start(self.solenoidPWM, 50)
        PWM.set_duty_cycle(self.solenoidPWM, 10)
        PWM.set_frequency(self.solenoidPWM, 1)

        # set up P9.16 PWM for particle brake control
        self.particlePWM = "P9_16"
        PWM.start(self.particlePWM, 50)
        PWM.set_duty_cycle(self.particlePWM, 50)
        #PWM.set_frequency(self.particlePWM, 1)

        PWM.stop(self.solenoidPWM)
        PWM.stop(self.particlePWM)

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
        self.bootloaderPage = pages.BootloaderPage()
        self.firmwarePage = pages.FirmwarePage()
        self.endPage = pages.EndPage()

        self.pager = Pager()
        self.pager.addPage(self.startPage)
        self.pager.addPage(self.bootloaderPage)
        self.pager.addPage(self.firmwarePage)
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
