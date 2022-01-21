import time 
import cv2
from threading import Thread
import numpy as np
class Cap:
    def __init__(self, filename) -> None:
        self.cap = cv2.VideoCapture(filename)
        self.thread = None
        self.start = True
    def E_thread(self):
        self.thread = Thread(target=self.loop)
        self.thread.setDaemon(True)
        self.thread.start()
    def loop(self):
        while self.start:
            ret, frame = self.cap.read()
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cv2.imshow("gray", gray)
                #time.sleep(0.05)
            except:
                pass
            if cv2.waitKey(25) == ord("q"):
                break
            
        self.cap.release()
        cv2.destroyAllWindows()