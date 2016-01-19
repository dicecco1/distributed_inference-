import numpy as np
import cv2
import os
import subprocess

def getint(name):
    num = name.split('.')[0]
    return int(num)

def write_video(output):
    fourcc = cv2.cv.CV_FOURCC(*'WMV1')#cv2.VideoWriter_fourcc(*'WMV1')
    out = cv2.VideoWriter(output, fourcc, 30.0, (1280, 720))

    filenames = os.listdir('output/')

    filenames.sort(key=getint)

    for f in filenames:
        img = cv2.imread('output/' + f)
        out.write(img)
        cv2.waitKey(1)
        os.remove('output/' + f)
        os.remove('temp/' + f)
