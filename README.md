# 🏥 MediCare Cloud
### Medicine Reminder and Health Records Management System
**SITER Academy Summer Internship 2026 | Cloud Computing Domain**

---

## 📌 Project Overview
MediCare Cloud is a cloud-based web application that helps patients manage medicine schedules and store health records securely using **Microsoft Azure** cloud services.

**Live Demo:** [your-app.azurestaticapps.net](#)  
**Backend API:** [your-api.azurewebsites.net/api/health](#)

---

## ⚡ Features
- 💊 **Medicine Reminder** — Add medicines with dosage, frequency, and time
- 📁 **Health Records** — Upload and manage prescriptions, lab reports (Azure Blob Storage)
- 📊 **Dashboard** — Today's schedule, stats, and recent records
- 📧 **Email Reminders** — Azure Communication Services
- 🔐 **User Authentication** — Register/Login with hashed passwords
- 📱 **Fully Responsive** — Mobile, tablet, desktop
- 🔍 **SEO Optimized** — Meta tags, semantic HTML, heading hierarchy

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3.x, Flask |
| Cloud Platform | Microsoft Azure |
| Database | Azure SQL Database |
| File Storage | Azure Blob Storage |
| Email | Azure Communication Services |
| Hosting (Frontend) | Azure Static Web Apps |
| Hosting (Backend) | Azure App Service |
| Version Control | Git, GitHub |

---

## 📁 Project Structure
```
medicare-cloud/
├── index.html          # Home page
├── about.html          # About page
├── login.html          # Login / Register
├── dashboard.html      # User dashboard
├── medicines.html      # Medicine tracker
├── records.html        # Health records
├── contact.html        # Contact page
├── css/
│   └── style.css       # Main stylesheet
├── js/
│   └── main.js         # Main JavaScript
├── backend/
│   ├── app.py          # Python Flask API
│   └── requirements.txt
└── README.md
```

---

## 🚀 How to Run Locally

### Frontend
Just open `index.html` in your browser — no setup needed.

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```
API runs at: `http://localhost:5000`

---

## ☁️ Azure Deployment

### Frontend → Azure Static Web Apps
1. Go to [portal.azure.com](https://portal.azure.com)
2. Create → Static Web App
3. Connect your GitHub repo
4. Set build output to `/` (root)
5. Deploy — done!

### Backend → Azure App Service
1. Go to [portal.azure.com](https://portal.azure.com)
2. Create → App Service → Python 3.12
3. Deploy from GitHub or zip upload
4. Set environment variables:
   - `SECRET_KEY` = your-secret-key
   - `AZURE_SQL_CONNECTION_STRING` = your-connection-string
   - `AZURE_BLOB_CONNECTION_STRING` = your-blob-connection-string
   - `AZURE_COMM_CONNECTION_STRING` = your-comm-connection-string

---

## 📄 Documentation
Full SRS and project documentation included in submission folder.

---

## 👤 Author
**Sayyada Sana Fatima**  
📧 b24cn003@kitsw.ac.in  
🔗 [github.com/SayyadaSanaFatima/medicare-cloud](https://github.com/SayyadaSanaFatima/medicare-cloud)  
SITER Academy Summer Internship 2026  
Domain: Cloud Computing  
Submission: 1 July 2026

---

## 📜 License
This project is created for educational purposes as part of SITER Academy internship.
