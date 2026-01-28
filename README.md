# Lab Management System (labman)

An opinionated lab management system for academic labs, now available as a CLI tool.

[![PyPI version](https://img.shields.io/pypi/v/ra-labman.svg)](https://pypi.org/project/ra-labman/)
[![Python versions](https://img.shields.io/pypi/pyversions/ra-labman.svg)](https://pypi.org/project/ra-labman/)
![GitHub Release](https://img.shields.io/github/v/release/lokeshmohanty/labMan)
[![License](https://img.shields.io/pypi/l/ra-labman.svg)](https://github.com/lokeshmohanty/labMan/blob/main/LICENSE)

## Directory Structure
- `labman/`: Main package directory
    - `lib/`: Backend modules
    - `templates/`: HTML templates
    - `static/`: Static assets
    - `server.py`: Flask application
    - `cli.py`: CLI entry point

## Installation

### Prerequisites
- Python 3.10+
- `uv` (recommended) or `pip`

### Install from pip
```bash
pip install ra-labman
```

### Install from source
```bash
git clone https://github.com/lokeshmohanty/labman.git
cd labman
uv pip install -e .
```

## Usage

### 1. Initialize Configuration

Run this command to create the `.env` configuration file interactively:

```bash
labman init
```

This will ask for:
- Lab Name
- Network Config (`HOST_IP`, `SERVER_PORT`, `ALLOWED_HOSTS`)
- SMTP settings

### 2. Start the Server

**Development mode** (default):

```bash
labman serve
# OR
labman serve dev
```

Starts Flask development server.

**Production mode**:

```bash
labman serve prod
# OR
labman serve prod --host 0.0.0.0 --port 9000
```

- Starts `gunicorn` in daemon mode (background).
- Logs output to `logs/YYYY-MM-DD.log`.

**Check Status**:
```bash
labman status
```
- Shows if the server is running (PID) and the latest log entry.

**Stop Production Server**:

```bash
labman serve stop
```
- Stops the running gunicorn process (using `gunicorn.pid` or matching process name).

### 3. Management Commands

**View Logs**:

```bash
labman log
```

Shows the latest log file and follows it (`tail -f`).

**Backup Database**:

```bash
labman backup
# OR
labman backup now
```

Creates a copy of the database in `backup/YYYY-MM-DD.db`.

**Automated Backup**:

```bash
labman backup auto daily
# Options: daily, weekly, monthly
```
Sets up a cron job to backup the database automatically.

**Stop Automated Backup**:
```bash
labman backup stop
```
Removes the automated backup cron job.

### 4. Access the Application

Open your browser at `http://<HOST_IP>:<SERVER_PORT>` (default: `http://localhost:9000`).

Default Login (first run):
- Email: Checks `.env` SMTP_USERNAME or `admin@example.com`
- Password: `admin123` (Change immediately!)

## Features

- **User Management**: Admin/User roles, secure auth with email activation.
- **Research Groups**: Hierarchical organization with member management.
- **Meeting Management**: Scheduling, RSVP, email notifications.
- **Content Library**: File sharing with access control and notifications.
- **Inventory**: Equipment and server tracking.
- **Email Notifications**: Automatic notifications with retry mechanism and background queue.
- **CLI Tools**: Built-in server management, logging, and backup.

![Dashboard](./assets/dashboard.png)
![Meetings](./assets/meetings.png)
![Research](./assets/research-groups.png)

## Email Notification System

The system includes a robust email notification system with:
- **Automatic Retry**: Failed emails are automatically retried up to 3 times with exponential backoff
- **Background Queue**: Mass notifications (meetings, content) are sent asynchronously to avoid blocking
- **Failure Logging**: Failed emails are logged to database for manual review and retry
- **Graceful Degradation**: Application continues to work even if email server is unavailable

# Development

To contribute:
1. Install in editable mode: `uv pip install -e .`
2. Run tests: `pytest`
3. Check code quality: `ruff check labman/`

## Testing

Run included tests and utilities:

```bash
# Test Email Configuration
labman test email

# Populate Test Data
labman test data

# Clear Test Data
labman test clear
```

## Troubleshooting

### Email Not Sending

1. **Check SMTP Configuration**:
   ```bash
   labman test email
   ```
   This will test your SMTP settings and show any errors.

2. **Verify `.env` Settings**:
   - `SMTP_SERVER`: Your SMTP server address (e.g., `smtp.gmail.com`)
   - `SMTP_PORT`: Usually `587` for TLS or `465` for SSL
   - `SMTP_USERNAME`: Your email address
   - `SMTP_PASSWORD`: Your email password or app-specific password
   - `SENDER_EMAIL`: Email address to send from (usually same as SMTP_USERNAME)

3. **Gmail Users**: You may need to:
   - Enable "Less secure app access" OR
   - Generate an "App Password" if using 2FA

4. **Check Failed Emails**: Failed emails are logged in the database and can be retried manually by an admin.

### Database Issues

If you encounter database errors:
```bash
# Backup current database
labman backup now

# Check database integrity
sqlite3 data/your_lab.db "PRAGMA integrity_check;"
```

### Server Won't Start

1. **Check if port is already in use**:
   ```bash
   lsof -i :9000  # Replace 9000 with your port
   ```

2. **Check logs**:
   ```bash
   labman log
   ```
