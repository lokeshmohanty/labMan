# Quick Start Guide

## LabMan v2 - FastAPI + SolidJS MVP

### 🎯 What's Ready

✅ **Backend (FastAPI)**
- Complete authentication system (JWT)
- User management with admin controls
- All database models created
- API documentation at `/api/v1/docs`

✅ **Frontend (SolidJS)**
- Login page
- Dashboard
- User management UI
- Protected routes

### 🚀 Start the Application

**Terminal 1 - Backend:**
```bash
cd labman-v2/backend

# Install dependencies (first time only)
pip install tomli  # Required for TOML config
uv pip install -e .

# Initialize database (first time only)
python init_db.py

# Start server
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd labman-v2/frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

### 🔑 Login

- URL: `http://localhost:5173`
- Email: `admin@example.com`
- Password: `admin123`

### 📝 Configuration

Edit `labman-v2/backend/conf.toml` to customize:
- Lab name
- Admin credentials
- SMTP settings (for email)
- Database location

### 📚 Documentation

- **Implementation Plan**: See artifacts
- **Walkthrough**: See artifacts  
- **API Docs**: `http://localhost:8000/api/v1/docs`
- **Full README**: `labman-v2/README.md`

### ✨ Features to Add Later

The foundation is complete! You can now add:
- Research groups
- Meetings
- Content library
- Inventory
- Research plans with Gantt charts

All models and schemas are already created in the backend.
