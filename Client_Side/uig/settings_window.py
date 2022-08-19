from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QApplication, QFileDialog, QMainWindow
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui,QtWidgets
from detection_window import DetectionWindow

# Manages the settings window
class SettingsWindow(QMainWindow):
	def __init__(self, token):
		super(SettingsWindow, self).__init__()
		loadUi('UI/settings_window.ui', self)

		self.drop_widget.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=0, yOffset=0))
		self.pushButton.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=12, xOffset=3, yOffset=3))
		self.setWindowTitle("Weapon Detection")
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.cls_button.clicked.connect(self.close)
		self.min_butto.clicked.connect(self.showMinimized)
		
		self.token = token

		self.pathy = 0

		

		self.detection_window = DetectionWindow()

		self.pushButton.clicked.connect(self.go_to_detection)

		self.popup = QMessageBox()
		self.popup.setWindowTitle("Failed")
		self.popup.setText("Fields must not be empty.")

		self.Browse.clicked.connect(self.browsefiles)

	def browsefiles(self):

		fname=QFileDialog.getOpenFileName(self, 'open file')

		self.pathy = fname[0]

	

		return self.pathy


	def displayInfo(self):
		self.show()

	# Get input and go to detection window
	def go_to_detection(self):
		if self.location_input.text() == '' or self.sendTo_input.text() == '':
			self.popup.exec_()
		else:
			if self.detection_window.isVisible():
				print('Detection window is already open!')
			else:
				self.detection_window.create_detection_instance(self.token, self.location_input.text(), self.sendTo_input.text(),self.pathy)
				self.detection_window.start_detection()
	
	#When closed
	def closeEvent(self, event):
		if self.detection_window.isVisible():
			self.detection_window.detection.running = False
			self.detection_window.close()
			event.accept()

