# -*- coding: utf-8 -*-
"""
:Author  : weijinlong
:Time    : 
:File    : 
"""
import cv2
import numpy as np
from PIL import Image


def solve(box):
    """
    绕 cx,cy点 w,h 旋转 angle 的坐标
    x = cx-w/2
    y = cy-h/2
    x1-cx = -w/2*cos(angle) +h/2*sin(angle)
    y1 -cy= -w/2*sin(angle) -h/2*cos(angle)

    h(x1-cx) = -wh/2*cos(angle) +hh/2*sin(angle)
    w(y1 -cy)= -ww/2*sin(angle) -hw/2*cos(angle)
    (hh+ww)/2sin(angle) = h(x1-cx)-w(y1 -cy)

    """
    x1, y1, x2, y2, x3, y3, x4, y4 = box[:8]
    cx = (x1 + x3 + x2 + x4) / 4.0
    cy = (y1 + y3 + y4 + y2) / 4.0
    w = (np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) + np.sqrt((x3 - x4) ** 2 + (y3 - y4) ** 2)) / 2
    h = (np.sqrt((x2 - x3) ** 2 + (y2 - y3) ** 2) + np.sqrt((x1 - x4) ** 2 + (y1 - y4) ** 2)) / 2

    sinA = (h * (x1 - cx) - w * (y1 - cy)) * 1.0 / (h * h + w * w) * 2
    angle = np.arcsin(sinA)
    return angle, w, h, cx, cy


def rotate_cut_img(im, degree, box, w, h, leftAdjust=False, rightAdjust=False, alph=0.2):
    x1, y1, x2, y2, x3, y3, x4, y4 = box[:8]
    x_center, y_center = np.mean([x1, x2, x3, x4]), np.mean([y1, y2, y3, y4])
    degree_ = degree * 180.0 / np.pi
    right = 0
    left = 0
    if rightAdjust:
        right = 1
    if leftAdjust:
        left = 1

    box = (max(1, x_center - w / 2 - left * alph * (w / 2))  ##xmin
           , y_center - h / 2,  ##ymin
           min(x_center + w / 2 + right * alph * (w / 2), im.size[0] - 1)  ##xmax
           , y_center + h / 2)  ##ymax

    newW = box[2] - box[0]
    newH = box[3] - box[1]
    tmpImg = im.rotate(degree_, center=(x_center, y_center)).crop(box)
    return tmpImg, newW, newH


def letterbox_image(image, size, fillValue=[128, 128, 128]):
    '''resize image with unchanged aspect ratio using padding'''
    image_w, image_h = image.size
    w, h = size
    new_w = int(image_w * min(w * 1.0 / image_w, h * 1.0 / image_h))
    new_h = int(image_h * min(w * 1.0 / image_w, h * 1.0 / image_h))

    resized_image = image.resize((new_w, new_h), Image.BICUBIC)
    if fillValue is None:
        fillValue = [int(x.mean()) for x in cv2.split(np.array(image))]
    boxed_image = Image.new('RGB', size, tuple(fillValue))
    boxed_image.paste(resized_image, (0, 0))
    return boxed_image, new_w / image_w


def sort_box(box):
    """
    对box排序,及页面进行排版
        box[index, 0] = x1
        box[index, 1] = y1
        box[index, 2] = x2
        box[index, 3] = y2
        box[index, 4] = x3
        box[index, 5] = y3
        box[index, 6] = x4
        box[index, 7] = y4
    """

    box = sorted(box, key=lambda x: sum([x[1], x[3], x[5], x[7]]))
    return list(box)
