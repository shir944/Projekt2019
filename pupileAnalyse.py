# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 11:36:36 2019

@author: shir-
"""

import pgm
import matplotlib.pyplot as plt
from scipy import ndimage
import numpy as np

pgmfile = "p00001s001e016c001t001.pgm"

video = pgm.PGMReader(pgmfile)
frames = video[0::1]

co_y = np.arange(0, video.height, 1)
co_x = np.arange(0, video.width, 1)
com = np.full((2,video.length), np.nan, dtype=float) 

doplot = False
if doplot:
    fig = plt.figure(figsize=(10,5))
    
for i, frame in enumerate(frames):
    img = frame['data']
    img[100:-1,0:25] = 100
    #img1 = ndimage.median_filter(img, 1)
    #img1 = ndimage.uniform_filter(img, 3)
    img1 = ndimage.gaussian_filter(img, sigma=1)
    h = ndimage.histogram(img1, 0, 255, 256)
    b = img1 < 80
    b[0,:] = False
    b[-3:,:] = False
    img[b] = 255
    
    sum_x = np.sum(b, axis=0)
    sum_y = np.sum(b, axis=1)
    sum_n = np.sum(sum_x)
    com[0,i] = np.dot(co_x, sum_x)/sum_n 
    com[1,i] = np.dot(co_y, sum_y)/sum_n 
    icom = np.round(com[:,i]).astype(int) 
    
    img[:,icom[0]-1:icom[0]+1] = 200
    img[icom[1]-1:icom[1]+1,:] = 200
    print(i)
    
    if doplot:
         # ax = fig.add_subplot(len(frames),3, i*3+1)
         # ax.imshow(img, cmap='gray')
         # ax.set_axis_off()
         #
         # ax = fig.add_subplot(len(frames),3, i*3+2)
         # ax.imshow(img1, cmap='gray')
         # ax.set_axis_off()
         #
         # ax = fig.add_subplot(len(frames),3, i*3+3)
         # ax.plot(h)
         plt.imshow(img, cmap='gray')
         plt.title('%d/%d x=%1.2f y=%1.2f' % (i,video.length,com[0,i],com[1,i]))
         plt.show()
plt.show()
plt.plot(com.T)
plt.show()