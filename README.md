# Lab Management System (labman)

An opinionated lab management system for academic labs, now available as a CLI tool.

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
- **User Management**: Admin/User roles, secure auth.
- **Research Groups**: Hierarchical organization.
- **Meeting Management**: Scheduling, RSVP, notifications.
- **Content Library**: File sharing with access control.
- **Inventory**: Equipment tracking.
- **CLI Tools**: Built-in server management, logging, and backup.

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

## Development
To contribute:
1. Install in editable mode: `uv pip install -e .`
2. Run tests: `pytest`
