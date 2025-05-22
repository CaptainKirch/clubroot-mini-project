# 🧼 Clubroot Reporting & Automation System

A technician-facing web app for field data collection, QR code tagging, PDF report generation, and automated internal reporting — built with FastAPI, TailwindCSS, and Python-based tooling.

---

## 📦 Features

### ✅ Phase 1 (Internal Workflow)
- Mobile-friendly technician form (photo uploads, GPS, signatures)
- File-safe submission saving (namespaced per UUID)
- CSV-based data logging
- QR code generation (one per unit)
- Branded PDF report generation
- 60-minute buffer with scheduled email report delivery
- Admin dashboard to view/download submissions

### 🔒 Phase 2 (Client Access Portal)
- Secure client login (via PIN)
- View/download submitted reports by unit or license
- QR-code-based report lookups
- PIN request workflow with admin approval

---

## 🛠 Stack

| Layer         | Tooling                        |
|---------------|--------------------------------|
| Frontend UI   | TailwindCSS + DaisyUI (Jinja2) |
| Backend       | FastAPI                        |
| Templating    | Jinja2                         |
| File Uploads  | FastAPI `UploadFile`           |
| Data Storage  | CSV + folder-based media       |
| QR Code       | `qrcode` Python lib            |
| PDF Generator | `FPDF` or `WeasyPrint`         |
| Scheduler     | APScheduler                    |
| Email Logic   | `smtplib` (config via `.env`)  |

---

## 🚀 Quickstart

```bash
# Clone and CD
git clone https://github.com/your-username/clubroot_reporting.git
cd clubroot_reporting

# Create and activate virtualenv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
uvicorn app.main:app --reload
