import numpy as np
import cv2

def load_texture(path,alpha=False):
    try:
        im = cv2.imread(path)
        im = cv2.flip(im, 0)
        if alpha:
            im = cv2.cvtColor(im,cv2.COLOR_BGR2RGBA)
        else:
            im = cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
        im = im.astype(np.float32)
        return im
    except Exception:
        print("unable to load image @ {}".format(path))

def write_image(im, path):
#    try:
    #im = np.frombuffer(im, np.float32)
        #im.shape = h, w, 4
        #im = im[::-1, :]
    cv2.imwrite(path, im)
        #im = cv2.flip(im, 0)
        #if alpha:
        #    im = cv2.cvtColor(im,cv2.COLOR_BGR2RGBA)
        #else:
        #    im = cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
        #im = im.astype(np.float32)
        #return im
#    except Exception:
#        print("unable to write image @ {}".format(path))
