# -*- coding: UTF-8 -*-  
import cv2
import numpy as np


class mycamshift(object):
    """description of class"""
    def __init__(self,ID=0): 
        self.ID=ID
        self.__framesize=None
        self.__track_window=None
        self.__hist=None
        self.prob=None
  
    @staticmethod
    def filte_color(frame,lower_hsv=np.array((0., 85., 85.)),higher_hsv=np.array((180., 255., 255.))):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_hsv, higher_hsv)
        return (hsv,mask)

    def preProcess(self,hsv,mask,selection,n=32):     
        if selection is None:
            return False
        x0, y0, x1, y1 = selection
        if x0==x1 or y0==y1:
            return False
        hsv_roi = hsv[y0:y1, x0:x1]
        mask_roi = mask[y0:y1, x0:x1]
        hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [n], [0, 180] )
        cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
        self.__hist = hist.reshape(-1)       
        self.__track_window=(x0,y0,x1-x0,y1-y0)
        self.__framesize=(hsv.shape[0],hsv.shape[1])
        return True

    def getHist(self):
        if self.__hist is None:
            return None
        bin_count = self.__hist.shape[0]
        bin_w = 24
        img = np.zeros((256, bin_count*bin_w, 3), np.uint8)
        for i in xrange(bin_count):
            h = int(self.__hist[i])
            cv2.rectangle(img, (i*bin_w+2, 255), ((i+1)*bin_w-2, 255-h), (int(180.0*i/bin_count), 255, 255), -1)
        return cv2.cvtColor(img, cv2.COLOR_HSV2BGR)


    def go_once(self,hsv,mask):
        if not(self.__track_window and self.__track_window[2] > 0 and self.__track_window[3] > 0):
            raise Exception('跟踪窗未定义或者出错')
        self.prob = cv2.calcBackProject([hsv], [0], self.__hist, [0, 180], 1)
        self.prob &= mask
        term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
        track_box, self.__track_window = cv2.CamShift(self.prob, self.__track_window, term_crit)
        area=track_box[1][0]*track_box[1][1];
        if(area<5):
            print('Target %s is Lost' % self.ID)
            self.__track_window=(0,0,self.__framesize[1],self.__framesize[0])
        return track_box







