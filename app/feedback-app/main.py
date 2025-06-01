from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db, Feedback

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/status")
def status():
    return {"Status": "OK"}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(name="index.html", request=request)

@app.post("/submit-feedback")
async def submit_feedback(
    rating: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    print(f"Received category: {category}")
    print(f"Received message: {message}")


    feedback = Feedback(rating=rating, message=message)
    db.add(feedback)
    db.commit()

    return RedirectResponse(url="/?submitted=true", status_code=303)