import __init__

from lifting import PoseEstimator
from lifting.utils import draw_limbs
from lifting.utils import plot_pose

import cv2
import matplotlib.pyplot as plt
from os.path import dirname, realpath
import time
import sys
from multiprocessing.connection import Listener

# address = ('localhost', 6000)     # family is deduced to be 'AF_INET'
# listener = Listener(address, authkey='secret password'.encode())
# conn = listener.accept()
# print('connection accepted from', listener.last_accepted)
# while True:
#     msg = conn.recv()
#     # do something with msg
#     print(msg)
#     conn.send("hello from the other side...")
#     if msg == 'close':
#         conn.close()
#         break
# listener.close()

# cap = cv2.VideoCapture(VIDEO_FILE_PATH)



class Server:
    def __init__(self):
        self.DIR_PATH = dirname(realpath(__file__))
        self.PROJECT_PATH = realpath(self.DIR_PATH + '/..')
        self.IMAGE_FILE_PATH = self.PROJECT_PATH + '/data/images/test_image.png'
        self.VIDEO_FILE_PATH = self.PROJECT_PATH + '/data/videos/test.mp4'
        self.SAVED_SESSIONS_DIR = self.PROJECT_PATH + '/data/saved_sessions'
        self.SESSION_PATH = self.SAVED_SESSIONS_DIR + '/init_session/init'
        self.PROB_MODEL_PATH = self.SAVED_SESSIONS_DIR + '/prob_model/prob_model_params.mat'

        self.address = ('localhost', 6000)

        self.listener = Listener(self.address, authkey='secret password'.encode())
        self.conn = self.listener.accept()
        print('connection accepted from', self.listener.last_accepted)

        self.cap = cv2.VideoCapture(self.VIDEO_FILE_PATH)

        if not self.cap.isOpened():
            raise IOError("Cannot open video")
        
        hasFrame, temp_image = self.cap.read()
        self.image_size = temp_image.shape

        self.pose_estimator = PoseEstimator(self.image_size, self.SESSION_PATH, self.PROB_MODEL_PATH)
        self.pose_estimator.initialise()

        self.processRate = 10 # Pose will be estimated for every self.processRate frames

    def sendObjs(self, obj):
        self.conn.send(obj)

    def recvObjs(self):
        obj = self.conn.recv()
        return obj
    
    def processVideo(self):
        hasFrame, image = self.cap.read()
        
        while hasFrame:
            try:
                pose_2d, visibility, pose_3d = self.processFrame(image)
                self.sendObjs(pose_3d.tolist())
            except ValueError:
                print("No visible people in the image.")
                self.sendObjs("No visible people in the image.")
        
            hasFrame, image = self.cap.read()

    def processFrame(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pose_2d, visibility, pose_3d = self.pose_estimator.estimate(image)
        return pose_2d, visibility, pose_3d

s = Server()
s.processVideo()