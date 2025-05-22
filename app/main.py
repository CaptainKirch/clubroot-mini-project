from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import form, admin_dashboard, clients

app = FastAPI()

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Register route groups
app.include_router(form.router)
app.include_router(admin_dashboard.router)
app.include_router(clients.router)