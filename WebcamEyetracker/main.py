from Eyetracker import Eyetracker, GazeObserver
from Calibration import Calibration
import cv2
import numpy as np
from SmoothingFilter import RingBuffer
from Button import Button


class Mainloop(GazeObserver):
    def __init__(self):
        self.button = Button()
        self.eye = Eyetracker(0)
        self.eye.subscribe(self)
        self.eye.start()

        # CALIBRATION
        self.calibration = Calibration()
        self.imsize = (600, 800)
        border = 10
        x_step = (self.imsize[1]-border*2)/2
        y_step = (self.imsize[0]-border*2)/2
        self.stim_pos = []
        for x in range(3):
            for y in range(3):
                self.stim_pos.append([int(border+x_step*x), int(border+y_step*y)])
        self.current_stim = 0
        # CALIBRATION

        # FILTER
        self.smoother = RingBuffer(1)
        # FILTER

    def __del__(self):
        self.eye.join()

    def update_gaze(self, gaze, frame):
        cv2.imshow('Eyetracker', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        # CALIBRATION
        calibration_img = np.zeros((self.imsize[0], self.imsize[1], 3))
        if self.calibration.is_calibrating:
            radius = 5
            cv2.circle(calibration_img, (self.stim_pos[self.current_stim][0], self.stim_pos[self.current_stim][1]), radius,
                       (255, 255, 255), -1)
            self.calibration.push_sample((gaze[0], gaze[1]), self.stim_pos[self.current_stim])
        else:
            gaze = self.calibration.apply_calibration((gaze[0], gaze[1]))
            self.smoother.append(gaze)
            radius = 10
            gaze = self.smoother.get_mean()
            cv2.circle(calibration_img, (int(gaze[0]), int(gaze[1])), radius, (0, 255, 0), -1)
            self.button.draw(gaze, calibration_img)
        cv2.imshow("stimulus", calibration_img)
        # CALIBRATION

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            self.eye.should_run = False
        if key & 0xFF == ord('a'):
            self.current_stim = self.current_stim + 1
            if self.current_stim == len(self.stim_pos):
                self.calibration.calibrate()


main = Mainloop()

