import cv2

class ImageWrapper:
    def __init__(self, path):
        self.ImageArray = cv2.imread(path)
        self.TopLeftX = 0
        self.TopLeftY = 0
        self.Width = 0
        self.Height = 0

    def ResizeImageCpy(self, width, height):
        cpy = cv2.resize(self.ImageArray, (width, height))
        return cpy

    def UpdateDimensionsCpy(self, width, height):
        if self.ImageArray is not None:
            return cv2.resize(self.ImageArray.copy(), (width, height))

    def SetTopLeftCorner(self, x, y):
        self.TopLeftX = x
        self.TopLeftY = y

    def GetTopLeftCorner(self):
        return self.TopLeftX, self.TopLeftY

    def GetImageDimensions(self):
        return self.Width, self.Height

    def GetImage(self):
        return self.ImageArray