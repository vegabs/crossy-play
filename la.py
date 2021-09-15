import tkinter as tk
import cv2
from PIL import Image, ImageTk
import threading
import numpy as np
import keyboard


def addPNG(pngFile, goalImage, x1, y1):
    pngImage = cv2.imread(pngFile, -1)
    w, h = pngImage.shape[:2]
    b, g, r, a = cv2.split(pngImage)
    mask = np.dstack((a, a, a))
    pngImage = np.dstack((b, g, r))

    # x1,y1 son la esquina superior izquierda desde donde se va a dibujar
    roi = goalImage[int(y1-h/2):int((y1-h/2)+h), int(x1-w/2):int((x1-w/2)+w)]
    roi[mask > 0] = pngImage[mask > 0]


class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Crossy Road")
        self.master.resizable(0, 0)
        self.master.protocol("WM_DELETE_WINDOW", self.closing)

        self.resize_scale = 1.5

        self.cap = cv2.VideoCapture(0)
        _, frame = self.cap.read()

        self.width = int(frame.shape[1]/self.resize_scale)
        self.height = int(frame.shape[0]/self.resize_scale)

        frm1 = tk.Frame(self.master)
        frm1.pack(padx=10, pady=10)

        # frame 1
        self.canvas = tk.Canvas(frm1, width=self.width, height=self.height,
                                borderwidth=1, relief='sunken')
        self.canvas.pack(fill='both', expand=True)

        th = threading.Thread(target=self.cam_loop, daemon=True)
        th.start()

    def cam_loop(self):
        self.update()

    def update(self):

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

        ret, frame = self.cap.read()

        if ret:

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)  # mirror mode
            frame = cv2.blur(frame, (5, 5))  # blur mode
            frame = cv2.resize(frame, (self.width, self.height))

            height = frame.shape[0]  # 480
            width = frame.shape[1]  # 640

            # rangos
            rangoiz = int(width*.3)
            rangoder = int(width*.7)
            rangosup = int(height*.3)
            rangoinf = int(height*.7)

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            range_min = (23, 36, 66)
            range_max = (126, 255, 141)

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
            try:
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=photo, anchor='nw')
                self.canvas.image = photo
            except:
                pass

        self.master.after(10, self.cam_loop)

    def closing(self):
        if self.cap.isOpened():
            self.cap.release()
        self.master.destroy()


root = tk.Tk()
app = App(root)
root.mainloop()
