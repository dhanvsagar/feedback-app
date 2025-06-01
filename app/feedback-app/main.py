from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/status")
def status():
    return {"Status": "OK"}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(name="index.html", request=request)
