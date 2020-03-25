import sys
import asyncio
from time import sleep
from math import sin, cos, tan, asin, acos, atan, degrees, radians
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets

from my_modules.pyLoadingScreen import LoadingScreen
#from pyLoadingScreen import LoadingScreen
from GUI.window_main import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """GUI SETUP."""
        QtWidgets.QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.stop_button.setDisabled(True)

        self.ui.start_button.clicked.connect(self.animation_start)
        self.ui.stop_button.clicked.connect(self.animation_stop)

        # Animation type selecter
        self.ui.animationTypeSelect_comboBox.addItem("RoundRobin")
        self.ui.animationTypeSelect_comboBox.addItem("RibbonDance")

   
    def animation_start(self):
        self.ui.start_button.setDisabled(True)

        animationType = self.ui.animationTypeSelect_comboBox.currentText()

        if animationType == "RoundRobin":
            self._animation = LoadingScreen()
        elif animationType == "RibbonDance":
            self._animation = LoadingScreen(
                windowSize = (500, 170),
                animationType = animationType,
                animationColorRainbow = True,
                animationCountStepsPerRound = 200
            )
        else:
            self.ui.start_button.setEnabled(True)
            return
        
        self._animation.thread = Thread(target=self._animation.worker)
        self._animation.thread.start()
        self.ui.stop_button.setEnabled(True)
    

    def animation_stop(self):
        self.ui.stop_button.setDisabled(True)
        self.ui.stop_button.repaint()

        self._animation.exit = True
        while self._animation.isRunning:
            sleep(0.5)
        else:
            self._animation.thread.join()
            self.ui.start_button.setEnabled(True)


    def closeEvent(self, event):
        """QtWidgets.QMainWindow.closeEvent"""
        try:
            if self._animation:
                self._animation.exit = True
        except AttributeError:
            pass


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    MAIN = MainWindow()
    MAIN.show()

    sys.exit(app.exec())