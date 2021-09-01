import cv2
import numpy as np
import keyboard


def nothing(x):
    pass


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

camera = cv2.VideoCapture(0)
while(True):
    available, frame = camera.read()
    height = frame.shape[0]  # 480
    width = frame.shape[1]  # 640

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
            frame = cv2.circle(frame,(cx,cy),5,(0,255,0))
            
            if((0 < cx < 200) and left_available):
                keyboard.press_and_release("left")
                left_available = False
                
            elif( (440 < cx < 640) and right_available):
                keyboard.press_and_release("right")
                right_available = False
                
            elif ((200 <= cx <= 440) and (cy < 160) and up_available):
                keyboard.press_and_release("up")
                up_available = False
                
            elif ((200 <= cx <= 440) and (cy > 320) and down_available):
                keyboard.press_and_release("down")
                down_available = False
                
            elif((200 <= cx <= 440) and (160 <= cy <= 320)):
                left_available = True
                right_available = True
                up_available = True
                down_available = True
            
        # draw
        frame = cv2.line(frame,(200,0),(200,480),(0,255,0))
        frame = cv2.line(frame,(440,0),(440,480),(0,255,0))
        frame = cv2.line(frame,(200,160),(440,160),(0,255,0))
        frame = cv2.line(frame,(200,320),(440,320),(0,255,0))
        cv2.imshow('Capture', frame)
        cv2.imshow('Capture_HSV', segmented)
    else:
        print("Camera not available")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
