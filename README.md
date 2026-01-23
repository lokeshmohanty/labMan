# Lab Management System

A bare-bones lab management system for an academic lab.

## Quick Links

- 📖 **[User Guide](USAGE.md)** - Complete guide for end users

## Overview

This Lab Management System is a web-based application designed to streamline lab operations including member management, research group organization, meeting scheduling, content sharing, and inventory tracking.

### Key Features

- **User Management**: Two-level access control (Admin/User) with secure authentication
- **Password Management**: Self-service password reset via email, admin override capability
- **Research Groups**: Hierarchical group structure for organizing research teams
- **Meeting Management**: Schedule meetings with calendar view, RSVP functionality, and email notifications
- **Content Library**: Upload and share files with granular access control and public share links
- **Lab Inventory**: Track equipment and manage lab servers
- **Email Notifications**: Automated notifications for meetings and content updates
- **Mobile Responsive**: Full functionality on desktop, tablet, and mobile devices

## Quick Start

### Prerequisites
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Install uv (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment and install dependencies
```bash
uv sync
```

3. Set environment variables
```bash
# .env file
FLASK_SECRET_KEY=your-secret-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-password
SENDER_EMAIL=sender@domain.com
```

4. Run application
```bash
uv run app.py
```

5. Access via browser at <http://localhost:9000>

### Default Login
- **Email**: admin@demo.lab (your smtp_username from .env)
- **Password**: admin123
- ⚠️ **Change this immediately after first login!**

## Configuration

### Server Settings
Edit `app.py` to change host and port:
```python
app.run(host='localhost', port=9000, debug=False)
```

### Email Setup (Required for Notifications)

The system is **pre-configured** to use `admin@demo.lab`. You only need to:

**1. Generate Gmail App Password:**
- Go to https://myaccount.google.com (sign in as admin@demo.lab)
- Security → 2-Step Verification (enable if needed)
- Security → App passwords → Generate for "Mail"
- Copy the 16-character password

**2. Update .env:**
```python
SMTP_PASSWORD = 'abcdefghijklmnop'  # Replace with your actual 16-char password
```

**3. Test (optional):**
```bash
python test_email.py
```

**4. Replace login message (optional):**
- Edit `templates/login.html` to change the login message. It currently displays a 
  link to this repository. You can either remove it or replace it with something like your lab website.

## Documentation

### For End Users
- **[USAGE.md](USAGE.md)** - Complete user guide covering:
  - Getting started and first login
  - Dashboard and navigation
  - Profile management
  - Using all features (meetings, content, inventory, etc.)
  - Mobile access
  - Troubleshooting and FAQs

## Features Overview

### Authentication & Authorization
- Secure login with session management
- Password hashing using Werkzeug PBKDF2
- Two roles: Admin (full access) and User (limited access)
- Self-service password reset via email
- Admin can reset any user's password

### Research Groups
- Create hierarchical group structures
- Default "airex" group for all members
- Assign members to multiple groups
- Group-based content access control

### Meeting Management
- Schedule meetings with date/time
- Assign to research groups
- Tag meetings (Knowledge Session, Research Discussion, Progress Update)
- Interactive monthly calendar view
- RSVP functionality (Join/Can't Join)
- Email notifications to airex group members
- Upload and download meeting materials
- Filter meetings by tags

### Content Library
- Upload files up to 100MB
- Support for multiple file types (documents, images, code, etc.)
- Group-level access control
- Public share links for external sharing
- Associate content with meetings
- Filter content by group
- Download files

### Lab Inventory
- Track equipment with quantity and location
- Stock level indicators (low/medium/high)
- Server management (IP, hostname, admin, location)
- Admin-only editing

### Notifications
- Email notifications for new meetings
- Notifications for meeting content uploads
- User-controlled notification preferences
- Password reset emails

## Directory Structure

```
lab-manager/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── lib/                           # Backend modules
│   ├── __init__.py
│   ├── data.py                    # Database management
│   ├── auth.py                    # Authentication
│   ├── users.py                   # User management & email
│   ├── groups.py                  # Research groups
│   ├── meetings.py                # Meeting management
│   ├── content.py                 # Content management
│   └── inventory.py               # Inventory & servers
├── templates/                     # HTML templates
│   ├── base.html                  # Base layout
│   ├── login.html                 # Login page
│   ├── dashboard.html             # Dashboard
│   ├── [feature]*.html            # Feature templates
│   └── ...
├── uploads/                       # File storage
└── demo_lab.db                  # SQLite database
```

## User Roles

### Administrator
- Full system access
- Create, edit, delete users
- Reset any user's password
- Manage research groups
- Edit all content and meetings
- Manage inventory and servers
- All user capabilities

### User
- View all content with access permissions
- Change own password
- Request password reset via email
- Upload content to assigned groups
- Schedule meetings for their groups
- Download accessible files
- RSVP to meetings
- View inventory (read-only)
- Control notification preferences

## Security Features

- Password hashing (PBKDF2 with SHA-256)
- Secure session management
- CSRF protection
- SQL injection prevention via parameterized queries
- File upload validation
- Access control checks
- Password reset tokens (24-hour expiry)
- STARTTLS email encryption

## Backup and Maintenance

### Database Backup
```bash
# Manual backup
cp demo_lab.db demo_lab_backup_$(date +%Y%m%d).db

# Automated backup (add to crontab)
0 2 * * * /path/to/backup_script.sh
```

## Production Deployment

For production: **Use WSGI server** (Gunicorn):
   ```bash
   uv rungunicorn -w 4 -b localhost:9000 app:app
   ```
