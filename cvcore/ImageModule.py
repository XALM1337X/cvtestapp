import cv2

class ImageWrapper:
    def __init__(self, path):
        self.ImageArray = cv2.imread(path)
        self.TopLeftX = 0
        self.TopLeftY = 0
        self.Width = 0
        self.Height = 0
        if self.ImageArray is not None:
            self.UpdateDimensions()

    def ResizeImage(self, width, height):
        self.ImageArray = cv2.resize(self.ImageArray, (width, height))
        self.UpdateDimensions()

    def UpdateDimensions(self):
        if self.ImageArray is not None:
            self.Height, self.Width = self.ImageArray.shape[:2]

    def SetTopLeftCorner(self, x, y):
        self.TopLeftX = x
        self.TopLeftY = y

    def GetTopLeftCorner(self):
        return self.TopLeftX, self.TopLeftY

    def GetImageDimensions(self):
        return self.Width, self.Height

    def GetImage(self):
        return self.ImageArray