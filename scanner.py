
import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pylibdmtx.pylibdmtx import decode
import parametrs as params
import keyboard

accuracy = 70 
version = "v0.1alfa vbelyakov"
class StatusScanner(object):
    Scan = "Search DM Code"
    Stopped = "Stop scan"
    Waiting = "Wait"


def renderPlain(image, statusScan):

    image = cv2.putText(
        image,
        statusScan,
        (30, 30),
        cv2.FONT_HERSHEY_COMPLEX,
        0.5,
        (255, 55, 108),
        1
    )

    image = cv2.putText(
        image,
        version,
        (520, 30),
        cv2.FONT_HERSHEY_COMPLEX,
        0.5,
        (255, 55, 108),
        1
    )    

def renderWithUIN(image, plain, points, dmCode):

    image = cv2.rectangle(
        image, 
        points[0],
        points[1],
        (132,255,56),
        3
    )
    
    image = cv2.putText(
        image,
        dmCode,
        (30, 30),
        cv2.FONT_HERSHEY_COMPLEX,
        1,
        (132,255,56),
        2
    )

def render(plain, image, points, UIN, statusScan):
    if plain:
        renderPlain(image, statusScan)
    else:
        renderWithUIN(image, plain, points, UIN)  

def findDMCode(image):

    data = decode(image, accuracy, shape=2, corrections = 2)

    for decodedObject in data:

        points = [
            (decodedObject.rect.left,  image.shape[0] - decodedObject.rect.top), 
            (decodedObject.rect.left + decodedObject.rect.width,  image.shape[0] - decodedObject.rect.top - decodedObject.rect.height)
        ]
        return (True,  points, decodedObject.data.decode("utf-8"))
    
    return (False, None, None)

class VideoCamera(object):
    # inputCamera
    video = None
    LastUIN = ''
    ImgInputSource = 0
    imgSizeW = 640
    imgSizeH = 360
    scanStatus = StatusScanner.Stopped

    def __init__(self, param: params.ImgParametrs):
        self.ImgInputSource = param.source
        self.imgSizeW = param.width
        self.imgSizeH = param.height

        self.video = cv2.VideoCapture(self.ImgInputSource)
        self.video.set(3, self.imgSizeW)  # float `width`
        self.video.set(4, self.imgSizeH)  # float `height`
            
    def __del__(self):
        self.video.release()

    def get_frame(self):
        _, image = self.video.read()
        image=cv2.resize(image,(self.imgSizeW, self.imgSizeH))

        if (self.scanStatus == StatusScanner.Scan):
            (found, points, UIN) = findDMCode(image)
            if self.LastUIN == None or self.LastUIN == '':
                self.LastUIN = UIN        
            if self.LastUIN != None and len(self.LastUIN) > 5:
                keyboard.write(self.LastUIN)
                keyboard.write("\n")               
                self.LastUIN = None
            render(not found, image, points, UIN, self.scanStatus)
        else:
            render(True, image, None, None, self.scanStatus)

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()       