from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from utils import handle_user_query, handle_intermediate_steps

class UserQuery(BaseModel):
    query: str


app = FastAPI()

# Serve static files like JS or CSS (optional)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve HTML templates
templates = Jinja2Templates(directory="templates")

@app.post("/intermediate/")
async def create_item(query: UserQuery):
    return handle_intermediate_steps(query.query)

@app.post("/chatbot/")
async def get_final_response(query: UserQuery):
    return handle_user_query(query.query)


# Route to serve the HTML page
@app.get("/webpage", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
