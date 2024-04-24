from typing import Union
from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes import routes
from database import SessionLocal, engine, Base
# Create an instance of the FastAPI class
app = FastAPI()
app.mount("/statice", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Define a route using a decorator
@app.get("/")
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="signup.html",
    )


# # Define another route
# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str = None):
#     return {"item_id": item_id, "q": q}

# @app.get("/home")
# def home():
#     return {"message": "home"}

# @app.get("/str/{q}")
# def read_item(item_id: int, q: str):
#     return {"item_id": item_id, "q": q}


app.include_router(router=routes)
Base.metadata.create_all(bind=engine)