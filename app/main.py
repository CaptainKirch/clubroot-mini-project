from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.routes import form, admin_dashboard, client_dashboard

app = FastAPI()  # ✅ MOVE THIS UP HERE

app.add_middleware(SessionMiddleware, secret_key="your-super-secret-key")

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Register route groups
app.include_router(form.router)
app.include_router(admin_dashboard.router)
app.include_router(client_dashboard.router)
