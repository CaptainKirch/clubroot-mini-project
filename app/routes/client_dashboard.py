from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/client-login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("client_login.html", {"request": request})

@router.post("/client-login", response_class=HTMLResponse)
async def process_login(request: Request, client_name: str = Form(...), pin: str = Form(...)):
    df = pd.read_csv("app/data/client_pins.csv")  # store PINs here
    match = df[(df["client_name"] == client_name) & (df["pin"] == pin)]

    if not match.empty:
        response = RedirectResponse(url=f"/client-dashboard/{client_name}", status_code=303)
        return response
    else:
        return templates.TemplateResponse("client_login.html", {"request": request, "error": "Invalid login."})

@router.get("/client-dashboard/{client_name}", response_class=HTMLResponse)
async def client_dashboard(request: Request, client_name: str):
    df = pd.read_csv("app/data/form_log.csv")
    client_records = df[df["client"] == client_name].to_dict(orient="records")

    return templates.TemplateResponse("client_dashboard.html", {
        "request": request,
        "records": client_records,
        "client_name": client_name
    })

@router.get("/request-pin", response_class=HTMLResponse)
async def show_pin_request_form(request: Request):
    return templates.TemplateResponse("request_pin.html", {"request": request})

@router.post("/request-pin", response_class=HTMLResponse)
async def handle_pin_request(
    request: Request,
    company_name: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    province: str = Form(...)
):
    import csv
    from pathlib import Path

    file_path = Path("app/data/pending_pin_requests.csv")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    write_header = not file_path.exists()

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["company_name", "full_name", "email", "phone", "province"])
        writer.writerow([company_name, full_name, email, phone, province])

    return templates.TemplateResponse("request_pin.html", {
        "request": request,
        "message": "Request submitted. We'll be in touch with your PIN."
    })
