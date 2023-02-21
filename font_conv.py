# -*- coding: utf-8 -*-
"""
Created on Sat May  7 01:03:35 2022

@author: herrm
"""
import cv2
import numpy as np
import sys

np.set_printoptions(threshold=sys.maxsize)

font = cv2.imread("font2.png", 0)[::2,::2].astype(np.uint8)
with open('font_repr.txt', 'w') as f:
    f.write(repr(font))


    
