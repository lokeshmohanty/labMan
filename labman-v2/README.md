# LabMan v2 - FastAPI + SolidJS

Modern replication of the LabMan academic lab management system using FastAPI (backend) and SolidJS (frontend).

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- uv (for Python package management)
- npm (for frontend packages)

### Backend Setup

```bash
cd labman-v2/backend

# Install dependencies with uv
uv pip install -e .

# Edit configuration file (conf.toml) as needed

# Initialize database
python init_db.py

# Run development server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/api/v1/docs`
- Health Check: `http://localhost:8000/health`

### Frontend Setup

```bash
cd labman-v2/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📋 Default Credentials

- **Email**: `admin@example.com`
- **Password**: `admin123`

**⚠️ Change these credentials immediately in production!**

## ✨ Features (MVP)

### ✅ Implemented
- **Authentication**
  - JWT-based login/logout
  - Password reset flow
  - Account activation via email
  - Protected routes

- **User Management**
  - List all users
  - Create new users (admin only)
  - Delete users (admin only)
  - Resend activation emails
  - Update passwords

- **Security**
  - Password hashing with bcrypt
  - JWT token authentication
  - CORS configuration
  - Admin-only endpoints

### 🚧 Coming Soon
- Research groups management
- Meeting scheduling and RSVP
- Content library with file uploads
- Inventory tracking
- Server management
- Research plans with Gantt charts
- Email notifications
- Rate limiting

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   ├── config.py     # Settings
│   ├── database.py   # Database setup
│   └── main.py       # FastAPI app
├── init_db.py        # Database initialization
└── pyproject.toml    # Dependencies
```

### Frontend (SolidJS)
```
frontend/
├── src/
│   ├── components/   # Reusable components
│   ├── pages/        # Page components
│   ├── services/     # API services
│   ├── stores/       # State management
│   ├── styles/       # CSS files
│   ├── types/        # TypeScript types
│   ├── App.tsx       # Main app
│   └── index.tsx     # Entry point
├── package.json
└── vite.config.ts
```

## 🔧 Configuration

### Backend (conf.toml)
```toml
SECRET_KEY = "your-secret-key-here"
DATABASE_URL = "sqlite:///./labman.db"
FRONTEND_URL = "http://localhost:5173"
LAB_NAME = "Your Lab Name"
FIRST_SUPERUSER = "admin@example.com"
FIRST_SUPERUSER_PASSWORD = "admin123"

# Optional: SMTP for emails
# SMTP_HOST = "smtp.gmail.com"
# SMTP_PORT = 587
# SMTP_USER = "your-email@gmail.com"
# SMTP_PASSWORD = "your-app-password"
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`

### Key Endpoints

**Authentication**
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password
- `POST /api/v1/auth/activate` - Activate account

**Users**
- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user (admin)
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user (admin)
- `DELETE /api/v1/users/{id}` - Delete user (admin)
- `PUT /api/v1/users/{id}/password` - Update password

## 🧪 Development

### Backend
```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run on different port
uvicorn app.main:app --reload --port 8080

# Reset database
rm labman.db
python init_db.py
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📦 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database
- **Pydantic** - Data validation
- **python-jose** - JWT tokens
- **passlib** - Password hashing
- **uvicorn** - ASGI server

### Frontend
- **SolidJS** - Reactive UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Axios** - HTTP client
- **@solidjs/router** - Routing

## 🔐 Security

- Passwords hashed with bcrypt
- JWT tokens for authentication
- CORS properly configured
- Admin-only endpoints protected
- SQL injection prevention (parameterized queries)
- File upload validation (when implemented)

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a replication of the original Flask-based LabMan. For the original project, see the `labman/` directory.

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify `conf.toml` file exists with correct settings
- Run `python init_db.py` to initialize database

### Frontend won't start
- Run `npm install` to install dependencies
- Check if port 5173 is available
- Verify backend is running on port 8000

### Login fails
- Check backend logs for errors
- Verify database was initialized
- Use default credentials: admin@example.com / admin123

## 📞 Support

For issues or questions, please check the implementation plan in the artifacts directory.
