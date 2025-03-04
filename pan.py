import os
import cv2
import numpy as np
from transformers import pipeline

pipe = pipeline("image-segmentation", model="briaai/RMBG-1.4", trust_remote_code=True)

def get_mask(image_path):
    mask = pipe(image_path, return_mask = True)
    mask = np.array(mask)
    mask = cv2.blur(mask, (5,5))
    mask = cv2.Canny(mask,100,200)
    return mask

def get_ellipse_area(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        if len(largest_contour) >= 5:
            ellipse = cv2.fitEllipse(largest_contour)
            (center, axes, angle) = ellipse
            major_axis, minor_axis = axes
            ellipse_area = (np.pi * (major_axis / 2) * (minor_axis / 2))
            return ellipse_area
    return 0

def get_percentage(route1, route2):
    mask1 = get_mask(route1)
    mask2 = get_mask(route2)
    
    area1 = get_ellipse_area(mask1)
    area2 = get_ellipse_area(mask2)
    area_diff = area2 / area1 * 100
    
    return (area1, area2, area_diff)