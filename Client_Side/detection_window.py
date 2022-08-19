from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtCore, QtGui,QtWidgets
import cv2
import numpy as np
import time
import requests
from detection import Detection

# Manages detection window, starts and stops detection thread
class DetectionWindow(QMainWindow):
	def __init__(self):
		super(DetectionWindow, self).__init__()	
		loadUi('UI/detection_window.ui', self)

		self.drop_widget.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=0, yOffset=0))
		self.stop_detection_button.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=12, xOffset=3, yOffset=3))
		self.setWindowTitle("smartCM")
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.cls_button.clicked.connect(self.close)
		self.min_butto.clicked.connect(self.showMinimized)
		

		self.stop_detection_button.clicked.connect(self.close)

	# Creating an instance of detection
	def create_detection_instance(self, token, location, receiver,pathy):
		self.detection = Detection(token, location, receiver,pathy)

	# Assigns detection output to the label in order to display detection output
	@pyqtSlot(QImage)
	def setImage(self, image):
		self.label_detection.setPixmap(QPixmap.fromImage(image))

	# Begin detection
	def start_detection(self):
		self.detection.changePixmap.connect(self.setImage)
		self.detection.start()
		self.show()

	# Closing the app
	def closeEvent(self, event):
		self.detection.running = False
		event.accept()

