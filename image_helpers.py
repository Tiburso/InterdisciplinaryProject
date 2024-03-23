import cv2
import numpy as np
from shapely.geometry import Polygon


def polygons_to_mask(polygons, size=832):
    mask = np.zeros((size, size, 1))
    for polygon in polygons:
        x, y = polygon.exterior.xy
        x = np.array(x, dtype=np.int32)
        y = np.array(y, dtype=np.int32)
        mask = cv2.fillPoly(mask, [np.column_stack((x, y))], (255))
    return mask


# Convert the mask to a polygon
def mask_to_polygons(mask):
    mask = mask.astype(np.uint8)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        polygons.append(Polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)]))
    return polygons


def polygon_to_bounding_box(polygon):
    x, y, w, h = cv2.boundingRect(np.array(polygon.exterior))
    return x, y, w, h
