Clubroot Reporting & Automation System
A technician-facing and admin-controlled system for field data collection, QR code tagging, PDF report generation, and controlled email distribution — built with FastAPI, TailwindCSS, and Python tooling.

📦 Features
✅ Phase 1 (Technician Workflow)
Mobile-friendly technician form with:

Photo uploads (before, after, disinfection)

Auto-captured GPS location (browser-based)

Digital signature capture (drawn on-screen)

Technician email collection

UUID-namespaced folder saving per submission

CSV-based master log (form_log.csv)

Branded PDF report generation including:

Technician signature image

GPS coordinates

Embedded QR code per report

Background image/template support on PDFs

✅ Phase 2 (Admin Dashboard + Control)
Secure admin login with password protection

Admin dashboard to:

View all submissions and their statuses

Edit recipient email before approval

Approve reports (changes status + triggers email send)

Delete or manage pending client PIN requests

Email dispatch only after admin approval

Integrated pending PIN workflow:

Clients request PINs via portal

Admin reviews + approves to grant access

✅ Phase 3 (Client Portal)
Secure client login via approved PIN

Client dashboard to:

View/download their related reports

Track report statuses

Access PDFs with QR-code cross-validation

🛠 Stack
Layer	Tooling
Frontend UI	TailwindCSS + DaisyUI (Jinja2)
Backend	FastAPI
Templating	Jinja2
File Uploads	FastAPI UploadFile
Data Storage	CSV + structured media folders
QR Code	qrcode Python library
PDF Generator	reportlab + PyPDF2
Scheduler	APScheduler (or custom script)
Email Logic	smtplib (configured via .env)
Signature Pad	signature_pad.js in-browser

🚀 Quickstart
bash
Copy
Edit
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
🔑 Admin Setup
Add a .env file with:

ADMIN_PASSWORD=your-secure-password

EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS (for outgoing emails)

Any API keys (e.g., background removal, Slazzer)

🌍 Access Points
Route	Purpose
/form	Technician form (field input)
/admin-login	Admin login page
/admin-dashboard	Admin dashboard view
/pending-requests	Pending PIN requests
/client-login	Client portal login
/client-dashboard	Client report dashboard

