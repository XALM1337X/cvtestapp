import cv2
from cvcore.ImageModule import ImageWrapper  # Importing ImageWrapper from ImageModule

class CVCore:
    def __init__(self, win_name="default"):
        self.ImageWrappers = []  # List to store ImageWrapper instances
        self.CurrentImageIndex = 0
        self.WindowName = win_name
        self.IsDrawing = False
        self.ClickX = 0
        self.ClickY = 0
        self.WindowClosed = False
        
        cv2.namedWindow(winname=win_name)
        self.SetMouseCallback(win_name)

    def AddImage(self, path):
        self.ImageWrappers.append(ImageWrapper(path))

    def ChangeCurrentImage(self, index):
        if 0 <= index < len(self.ImageWrappers):
            self.CurrentImageIndex = index

    def HandleEvent(self, event, x, y, flags, param):
        cpy = self.ImageWrappers[self.CurrentImageIndex].GetImage().copy()
        if event == cv2.EVENT_LBUTTONDOWN:
            self.IsDrawing = True
            self.ClickX = x
            self.ClickY = y
        elif event == cv2.EVENT_LBUTTONUP:
            self.IsDrawing = False
        elif event == cv2.EVENT_RBUTTONDOWN:
            print("Right button clicked")
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.IsDrawing:
                cv2.rectangle(cpy, (self.ClickX, self.ClickY), (x, y), (0, 0, 255), 1)

        if self.IsDrawing:
            self.Render(cpy)

    def Render(self, cpy):
        cv2.imshow(self.WindowName, cpy)

    def SetMouseCallback(self, win_name):
        cv2.setMouseCallback(win_name, self.HandleEvent)

    def CheckWindowClosed(self):
        return cv2.getWindowProperty(self.WindowName, cv2.WND_PROP_VISIBLE) < 1

    def GetCurrentImage(self):
        return self.ImageWrappers[self.CurrentImageIndex].GetImage()
        return cv2.getWindowProperty(self.WindowName, cv2.WND_PROP_VISIBLE) < 1