# import numpy as np
import time
import cv2
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pylibdmtx.pylibdmtx import decode

app = FastAPI()
# точность распознавания
accuracy = 70 
LastUIN = ""
templates = Jinja2Templates(directory="templates")
# os.add_dll_directory("C:\Users\admin\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\pylibdmtx")
#constans
windowName = "Ascort:DM scanner"
version = 1

def renderPlain(image):

    image = cv2.putText(
        image,
        'Поиск DM',
        (30, 30),
        cv2.FONT_HERSHEY_COMPLEX,
        0.5,
        (255, 55, 108),
        1
    )

    image = cv2.putText(
        image,
        'Нажмите любую клавишу для завершения',
        (30, 450),
        cv2.FONT_HERSHEY_COMPLEX,
        0.5,
        (255, 55, 108),
        1
    )

    image = cv2.putText(
        image,
        'Версия ' + str(version),
        (520, 30),
        cv2.FONT_HERSHEY_COMPLEX,
        0.5,
        (255, 55, 108),
        1
    )    


def renderWithUIN(image, plain, points, UIN):

    # рамка датаматрикса, для повёрнутых кодов pylibdmtx даёт некорректную ширину
    image = cv2.rectangle(
        image, 
        points[0],
        points[1],
        (132,255,56),
        5
    )
    
    # определённый уин
    image = cv2.putText(
        image,
        UIN,
        (30, 30),
        cv2.FONT_HERSHEY_COMPLEX,
        1,
        (132,255,56),
        2
    )

def render(plain, image, points, UIN):
    if plain:
        renderPlain(image)
    else:
        renderWithUIN(image, plain, points, UIN)
    cv2.imshow(windowName, image)
    

def proccessDMCode(image):

    data = decode(image, accuracy, shape=2)

    for decodedObject in data:

        points = [
            (decodedObject.rect.left,  image.shape[0] - decodedObject.rect.top), 
            (decodedObject.rect.left + decodedObject.rect.width,  image.shape[0] - decodedObject.rect.top - decodedObject.rect.height)
        ]
        print(decodedObject.data.decode("utf-8"))
        return (True,  points, decodedObject.data.decode("utf-8"))
    
    return (False, None, None)

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(3, 1920)  # float `width`
        self.video.set(4, 1080)  # float `height`
        # self.video = cv2.VideoCapture('Class_Det.mp4')
        # self.video = cv2.VideoCapture(args["input"])

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        print(image.shape)
        image=cv2.resize(image,(640,360))
        # video stream.
        (found, points, UIN) = proccessDMCode(image)
        LastUIN= UIN
        render(not found, image, points, UIN)
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})

@app.get('/lastUIN')
def lastdata(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})

def gen(camera):
    c = 1
    start = time.time()
    while True:
        start_1 = time.time()
        if c % 20 == 0:
            end = time.time()
            FPS = 20/(end-start)
            # print("FPS_avg : {:.6f} ".format(FPS))
            start = time.time()
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        end_1 = time.time()
        FPS = 1/(end_1-start_1)
        # print("FPS : {:.6f} ".format(FPS))
        c +=1

@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen(VideoCamera()), media_type="multipart/x-mixed-replace;boundary=frame")
if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=5000, access_log=False)