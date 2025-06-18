from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()

# 정적 파일 경로 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 템플릿 경로 설정
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/profit", response_class=HTMLResponse)
def read_profit(request: Request):
    return templates.TemplateResponse("profit.html", {"request": request})

@app.get("/picks", response_class=HTMLResponse)
def read_recommendations(request: Request):
    return templates.TemplateResponse("picks.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True) 