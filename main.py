import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import parametrs 
import scanner 


app = FastAPI()

img_params = parametrs.ImgParametrs()

# default
img_params.set_params( 360, 640, 0)
CurVideo = scanner.VideoCamera(img_params)

# последний распознанный уин
LastUIN = ''
version = 0.1

templates = Jinja2Templates(directory="templates")

# stream cam
@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})

@app.get('/lastreadcode')
def lastdata(request: Request):
    return {"uin":CurVideo.LastUIN}

@app.get('/newscan')
def newScan():
    CurVideo.LastUIN = ''
    CurVideo.scanStatus = scanner.StatusScanner.Scan   
    return {"succes": "true"}

@app.get('/stopscan')
def stopscan():
    CurVideo.LastUIN = None
    CurVideo.scanStatus = scanner.StatusScanner.Stopped
    return {"succes": "true"}

@app.get('/pausescan/{uin}')
def stopscan(uin: str):
    if uin == CurVideo.LastUIN:
        CurVideo.LastUIN = None
        CurVideo.scanStatus = scanner.StatusScanner.Stopped
    return {"succes": "true"}

@app.post('/setinput')
def lastdata(inputdata):
    ImgInputSource = str(inputdata)
    return {"succes": "true"}

def gen(camera, openFrame = True ):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen(CurVideo), media_type="multipart/x-mixed-replace;boundary=frame")

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=5000, access_log=False)