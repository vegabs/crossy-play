import cv2
import numpy as np
import keyboard


def nothing(x):
    pass


def addPNG(pngFile, goalImage, x1, y1):
    pngImage = cv2.imread(pngFile, -1)
    w, h = pngImage.shape[:2]
    b, g, r, a = cv2.split(pngImage)
    mask = np.dstack((a, a, a))
    pngImage = np.dstack((b, g, r))

    # x1,y1 son la esquina superior izquierda desde donde se va a dibujar
    roi = goalImage[int(y1-h/2):int((y1-h/2)+h), int(x1-w/2):int((x1-w/2)+w)]
    roi[mask > 0] = pngImage[mask > 0]


# slider
cv2.namedWindow('slider')
cv2.createTrackbar('Vmin', 'slider', 66, 255, nothing)
cv2.createTrackbar('Vmax', 'slider', 141, 255, nothing)
cv2.createTrackbar('Smin', 'slider', 36, 255, nothing)
cv2.createTrackbar('Smax', 'slider', 255, 255, nothing)
cv2.createTrackbar('Hmin', 'slider', 23, 179, nothing)
cv2.createTrackbar('Hmax', 'slider', 126, 179, nothing)

# image processing
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

# keyboard
left_available = True
right_available = True
up_available = True
down_available = True

# img
RIGHT_IMG = "right-arrow.png"
LEFT_IMG = "left-arrow.png"
DOWN_IMG = "down-arrow.png"
UP_IMG = "up-arrow.png"

camera = cv2.VideoCapture(0)
while(True):
    available, frame = camera.read()
    height = frame.shape[0]  # 480
    width = frame.shape[1]  # 640

    # rangos
    rangoiz = int(width*.3)
    rangoder = int(width*.7)
    rangosup = int(height*.3)
    rangoinf = int(height*.7)

    if (available == True):
        frame = cv2.flip(frame, 1)  # mirror mode
        frame = cv2.blur(frame, (5, 5))  # blur mode

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h_min = cv2.getTrackbarPos('Hmin', 'slider')
        s_min = cv2.getTrackbarPos('Smin', 'slider')
        v_min = cv2.getTrackbarPos('Vmin', 'slider')
        h_max = cv2.getTrackbarPos('Hmax', 'slider')
        s_max = cv2.getTrackbarPos('Smax', 'slider')
        v_max = cv2.getTrackbarPos('Vmax', 'slider')

        range_min = (h_min, s_min, v_min)
        range_max = (h_max, s_max, v_max)

        segmented = cv2.inRange(hsv, range_min, range_max)
        segmented = cv2.morphologyEx(segmented, cv2.MORPH_OPEN, kernel)

        # centroid
        M = cv2.moments(segmented)
        if(M['m00'] > 1000):
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

            # draw lines
            frame = cv2.circle(frame, (cx, cy), 10, (255, 255, 255), 3)

            if((0 < cx < rangoiz) and left_available):
                keyboard.press_and_release("left")
                left_available = False

            elif((rangoder < cx < width) and right_available):
                keyboard.press_and_release("right")
                right_available = False

            elif ((rangoiz <= cx <= rangoder) and (cy < rangosup) and up_available):
                keyboard.press_and_release("up")
                up_available = False

            elif ((rangoiz <= cx <= rangoder) and (cy > rangoinf) and down_available):
                keyboard.press_and_release("down")
                down_available = False

            elif((rangoiz <= cx <= rangoder) and (rangosup <= cy <= rangoinf)):
                left_available = True
                right_available = True
                up_available = True
                down_available = True

            # draw arrow
            if((0 < cx < rangoiz)):
                addPNG(LEFT_IMG, frame, int(width*0.15), int(height*.5))

            elif((rangoder < cx < width)):
                addPNG(RIGHT_IMG, frame, int(width*0.85), int(height*.5))

            elif ((rangoiz <= cx <= rangoder) and (cy < rangosup)):
                addPNG(UP_IMG, frame, int(width*0.50), int(height*.15))

            elif ((rangoiz <= cx <= rangoder) and (cy > rangoinf)):
                addPNG(DOWN_IMG, frame, int(width*0.50), int(height*.85))

            # draw
            frame = cv2.line(frame,  (rangoiz, 0),
                             (rangoiz, height), (55, 75, 240), 2)
            frame = cv2.line(frame, (rangoder, 0),
                             (rangoder, height), (55, 75, 240), 2)
            frame = cv2.line(frame,  (rangoiz, rangosup),
                             (rangoder, rangosup), (55, 75, 240), 2)
            frame = cv2.line(frame,  (rangoiz, rangoinf),
                             (rangoder, rangoinf), (55, 75, 240), 2)

        cv2.imshow('Capture', frame)
        cv2.imshow('Capture_HSV', segmented)
    else:
        print("Camera not available")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
