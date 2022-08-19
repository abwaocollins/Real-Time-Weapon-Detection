from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
import time
import requests
import datetime
import torch
from matplotlib import pyplot as plt



# Handles the YOLOv4 detection algorithm, saves detected frames and sends alert to the server-side application
class Detection(QThread):
    def __init__(self, token, location, receiver,pathy):
        super(Detection, self).__init__()
        self.token = token
        self.location = location
        self.receiver = receiver
        self.pathy = pathy
        self.current_time = None

    changePixmap = pyqtSignal(QImage)

    vid = ''

    def motion(self):
        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")
        detection = False
        detection_stopped_time = None
        timer_started = False
        SECONDS_TO_RECORD_AFTER_DETECTION = 5
        frame_size = (int(cap.get(3)), int(cap.get(4)))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        while True:
            _, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            bodies = body_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) + len(bodies) > 0:
                if detection:
                    timer_started = False
                else:
                    detection = True
                    self.current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
                    out = cv2.VideoWriter(
                        f"{self.current_time}.mp4", fourcc, 20, frame_size)
                    vid = out
                    print("Started Recording!")
            elif detection:
                if timer_started:
                    if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                        detection = False
                        timer_started = False
                        out.release()
                        print('Stop Recording!')
                    else:
                        timer_started = True
                        detection_stopped_time = time.time()

            if detection:
                out.write(frame)
                for (x, y, width, height) in faces:
                    cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3)
                    cv2.imshow("Camera", frame)
                if cv2.waitKey(1) == ord('q'):
                    break
        out.release()
        cap.release()
        cv2.destroyAllWindows()
        return vid
        
        # Runs the detection model, evaluates detections and draws boxes around detected objects
    def run(self):
        # self.motion()
        model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5/runs/train/exp15/weights/best.pt')
        self.running = True
        # cap = cv2.VideoCapture(f'{self.current_time}.mp4')
        cap = cv2.VideoCapture(self.pathy)
        # cap = cv2.VideoCapture(0);
        starting_time = time.time() - 11
        while self.running:
            ret, frame = cap.read()
            if frame.any():
                height, width, channels = frame.shape
            else:
                height, width, channels = (0,0,0)
            
            if ret:
                results = model(frame)
                
                try:
                    confidence = results.pred[0][0][4].tolist()
                    if len(results.pred[0]) > 0:
                        if confidence > 0.5:
                            frame =  np.squeeze(results.render())
                            
                            # print(frame)
                            # self.save_detection(frame)
                            elapsed_time = starting_time - time.time()
                            # Save detected frame every 10 seconds
                            if elapsed_time <= -10:
                                starting_time = time.time()
                                self.save_detection(frame)
                except:
                    pass
                        
            # Showing final result
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bytesPerLine = channels * width
            convertToQtFormat = QImage(rgbImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(981, 631, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)
            # Saves detected frame as a .jpg within the saved_alert folder
    def save_detection(self, frame):
        cv2.imwrite("saved_frame/frame.jpg", frame)
        print('Frame Saved')
        self.post_detection()
# Sends alert to the server
    def post_detection(self):
        try:
            url = 'http://127.0.0.1:8000/api/images/'
            headers = {'Authorization': 'Token ' + self.token}
            files = {'image': open('saved_frame/frame.jpg', 'rb')}
            data = {'user_ID': self.token,'location': self.location, 'alert_receiver': self.receiver}
            response = requests.post(url, files=files, headers=headers, data=data)
            # checks whether alert was sent successfuly
            if response.ok:
                print('Alert was sent to the server')
            else:
                print('Alert was not sent successfully')
        except:
            print('Unable to access server')




