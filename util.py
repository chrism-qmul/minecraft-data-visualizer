import numpy as np
import cv2

def load_texture(path):
    try:
        im = cv2.imread(path)
        im = cv2.flip(im, 0)
        im = cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
        im = im.astype(np.float32)
        return im
    except Exception:
        print("unable to load image @ {}".format(path))
