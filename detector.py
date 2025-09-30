
import cv2
class SimpleDetector:
    def __init__(self, min_area=500):
        self.bgsub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50)
        self.min_area = min_area
        self.stationary = {}

    def detect(self, frame):
        mask = self.bgsub.apply(frame)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        counts = {'N':0,'S':0,'E':0,'W':0,'ambulance':0,'accident':False}
        h,w = frame.shape[:2]
        centers = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < self.min_area:
                continue
            x,y,ww,hh = cv2.boundingRect(c)
            boxes.append((x,y,ww,hh))
            cx = x + ww//2; cy = y + hh//2
            centers.append((cx,cy))
            if cy < h/3:
                counts['N'] += 1
            elif cy > 2*h/3:
                counts['S'] += 1
            elif cx < w/3:
                counts['W'] += 1
            else:
                counts['E'] += 1
        for cx,cy in centers:
            key = f"{(cx//20, cy//20)}"
            self.stationary[key] = self.stationary.get(key,0) + 1
            if self.stationary[key] > 80:
                counts['accident'] = True
        for k in list(self.stationary.keys()):
            self.stationary[k] -= 1
            if self.stationary[k] <= 0:
                del self.stationary[k]
        return boxes, counts

class SimpleAutoDetector:
    def __init__(self, min_area=500):
        self.simple = SimpleDetector(min_area=min_area)
    def detect(self, frame):
        return self.simple.detect(frame)
