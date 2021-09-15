import cv2
import numpy as np
# read the images
# 读图（0:BGR， -1:保持不变)
wali = cv2.imread(
    "D:\Documentos\GitHub\crossy-road\minimalist-aesthetic-wallpaper-1920x1080-1.jpg")
# worm = cv2.imread("D:\Documentos\GitHub\crossy-road\parts-76.png", -1)

# # split and merge channels
# w, h = worm.shape[:2]
# b, g, r, a = cv2.split(worm)
# mask = np.dstack((a, a, a))
# worm = np.dstack((b, g, r))

# # mask operation
# canvas = wali[100:100+h, 200:200+w]
# imask = mask > 0
# canvas[imask] = worm[imask]

# # display
# cv2.imshow("wali", wali)
# cv2.waitKey()


def addPNG(pngFile, goalImage, x1, y1):
    pngImage = cv2.imread(pngFile, -1)
    w, h = pngImage.shape[:2]
    b, g, r, a = cv2.split(pngImage)
    mask = np.dstack((a, a, a))
    pngImage = np.dstack((b, g, r))

    # x1,y1 son la esquina superior izquierda desde donde se va a dibujar
    roi = goalImage[y1:y1+h, x1:x1+w]
    roi[mask > 0] = pngImage[mask > 0]


addPNG("parts-76.png", wali, 200, 200)
# display
cv2.imshow("wali", wali)
cv2.waitKey()
