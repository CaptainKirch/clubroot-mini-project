from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
load_dotenv()

from app.routes import form, admin_dashboard, client_dashboard

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="your-super-secret-key")

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/submissions", StaticFiles(directory="app/data/submissions"), name="submissions")  # ✅ THIS LINE
templates = Jinja2Templates(directory="app/templates")

# Register route groups
app.include_router(form.router)
app.include_router(admin_dashboard.router)
app.include_router(client_dashboard.router)

print("[BOOT] FastAPI loaded")