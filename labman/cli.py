import click
import os
import secrets
import shutil
import glob
import subprocess
import time
from datetime import datetime
from labman.server import app
from dotenv import load_dotenv, dotenv_values
import difflib

@click.group()
def main():
    """Lab Manager CLI"""
    pass

@main.command()
@click.argument('mode', default='dev', type=click.Choice(['dev', 'prod', 'stop']))
@click.option('--port', default=9000, help='Port to run on')
@click.option('--host', default='0.0.0.0', help='Host to run on')
def serve(mode, port, host):
    """Start (dev/prod) or stop the server"""
    if mode == 'dev':
        click.echo(f"Starting dev server on {host}:{port}...")
        app.run(debug=True, host=host, port=port)
    
    elif mode == 'stop':
        if not os.path.exists("gunicorn.pid"):
            # Try to stop via pkill if pid file missing
            click.echo("PID file not found. Trying to stop any running labman gunicorn process...")
            if os.system("pkill -f 'labman.server:app'") == 0:
                 click.secho("Server stopped.", fg="green")
            else:
                 click.secho("No running server found.", fg="yellow")
            return

        try:
            with open("gunicorn.pid", "r") as f:
                pid = int(f.read().strip())
            
            os.kill(pid, 15) # SIGTERM
            click.secho(f"Stopped server (PID {pid})", fg="green")
            os.remove("gunicorn.pid")
        except ProcessLookupError:
            click.secho("Process not found. Cleaning up PID file.", fg="yellow")
            os.remove("gunicorn.pid")
        except Exception as e:
            click.secho(f"Error stopping server: {e}", fg="red")

    else: # prod
        click.echo(f"Starting prod server on {host}:{port} using gunicorn...")
        # Check if gunicorn is installed
        if os.system("which gunicorn > /dev/null") != 0:
            click.secho("Error: gunicorn is not installed. Please install it (pip install gunicorn).", fg="red")
            return
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = f"logs/{date_str}.log"
        
        # Run gunicorn as daemon
        cmd = [
            "gunicorn",
            "-w", "4",
            "-b", f"{host}:{port}",
            "--daemon",
            "--pid", "gunicorn.pid",
            "--access-logfile", log_file,
            "--error-logfile", log_file,
            "labman.server:app"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            click.secho(f"Server started in background. Logs: {log_file}", fg="green")
        except subprocess.CalledProcessError as e:
            click.secho(f"Failed to start server: {e}", fg="red")

@main.command()
def log():
    """Show the latest log with follow mode"""
    logs = sorted(glob.glob("logs/*.log"))
    if not logs:
        click.secho("No log files found in logs/", fg="yellow")
        return
    
    latest_log = logs[-1]
    click.echo(f"Showing log: {latest_log}")
    try:
        # Use tail -f to follow
        subprocess.run(["tail", "-f", latest_log])
    except KeyboardInterrupt:
        pass

@main.command()
@click.argument('action', default='now', type=click.Choice(['now', 'auto', 'stop']))
@click.argument('frequency', required=False, type=click.Choice(['daily', 'weekly', 'monthly']))
def backup(action, frequency):
    """Backup the database files"""
    load_dotenv()
    db_filename = os.getenv('LAB_NAME', 'Demo Lab').lower().replace(" ", "_") + '.db'
    db_path = os.path.join('data', db_filename)
    
    if not os.path.exists(db_path):
        click.secho(f"Database file {db_path} not found.", fg="red")
        return

    os.makedirs('backup', exist_ok=True)
    
    if action == 'now':
        date_str = datetime.now().strftime('%Y-%m-%d')
        backup_file = f"backup/{date_str}.db"
        shutil.copy2(db_path, backup_file)
        click.secho(f"Backup created: {backup_file}", fg="green")
        
    elif action == 'auto' or action == 'stop':
        # Get current working directory for unique job ID
        cwd = os.getcwd()
        job_comment = f'labman-backup-{cwd}'
        
        try:
            from crontab import CronTab
        except ImportError:
            click.secho("Error: python-crontab not installed. Cannot manage auto backup.", fg="red")
            click.secho("Try: pip install python-crontab", fg="yellow")
            return

        try:
            cron = CronTab(user=True)
            
            # Remove existing backups for this project (common step for both auto and stop)
            iter = cron.find_comment(job_comment)
            removed_count = 0
            for job in iter:
                cron.remove(job)
                removed_count += 1
            
            if action == 'stop':
                if removed_count > 0:
                    cron.write()
                    click.secho(f"Auto backup stopped. Removed {removed_count} cron job(s).", fg="green")
                else:
                    click.secho("No active auto backup found to stop.", fg="yellow")
                return

            # Action is auto, setup new job
            if not frequency:
                click.secho("Error: Frequency (daily/weekly/monthly) required for auto backup", fg="red")
                return
                
            # Get absolute path to labman executable
            labman_path = shutil.which("labman")
            if not labman_path:
                # Fallback to python -m labman.cli
                labman_cmd = f"{shutil.which('python3')} -m labman.cli backup now"
            else:
                labman_cmd = f"{labman_path} backup now"
                
            full_cmd = f"cd {cwd} && {labman_cmd}"

            job = cron.new(command=full_cmd, comment=job_comment)
            
            if frequency == 'daily':
                job.day.every(1)
            elif frequency == 'weekly':
                job.dow.on('SUN')
            elif frequency == 'monthly':
                job.month.every(1)
                
            cron.write()
            click.secho(f"Auto backup scheduled: {frequency}", fg="green")
        except Exception as e:
            click.secho(f"Failed to manage cron: {e}", fg="red")



@main.command()
@click.argument('target', type=click.Choice(['email', 'data', 'clear']))
def test(target):
    """Run tests: email, populate data, or clear test data"""
    load_dotenv()
    
    if target == 'email':
        click.echo("Running email configuration test...")
        from labman.tests.test_email import test_email, LAB_NAME
        
        click.echo(f"Testing for Lab: {LAB_NAME}")
        if test_email():
             click.secho("Email test passed!", fg="green")
        else:
             click.secho("Email test failed.", fg="red")
             
    elif target == 'data':
        click.echo("Populating test data...")
        from labman.tests.populate_test_data import populate
        try:
            populate()
            click.secho("Test data populated successfully!", fg="green")
        except Exception as e:
            click.secho(f"Failed to populate data: {e}", fg="red")

    elif target == 'clear':
        click.echo("Clearing test data...")
        from labman.tests.populate_test_data import clear
        try:
            clear()
            click.secho("Test data cleared successfully!", fg="green")
        except Exception as e:
            click.secho(f"Failed to clear data: {e}", fg="red")

@main.command()
def status():
    """Check the status of the production server"""
    pid_file = "gunicorn.pid"
    
    if not os.path.exists(pid_file):
        click.secho("Status: Stopped (PID file not found)", fg="yellow")
        return

    try:
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())
        
        # Check if process exists (signal 0 does nothing but error if process dead)
        os.kill(pid, 0)
        click.secho(f"Status: Running (PID: {pid})", fg="green")
        
        # Show log info
        logs = sorted(glob.glob("logs/*.log"))
        if logs:
            latest_log = logs[-1]
            click.echo(f"Latest log: {latest_log}")
            # Show last line
            try:
                last_line = subprocess.check_output(['tail', '-n', '1', latest_log]).decode('utf-8').strip()
                click.echo(f"Last log entry: {last_line}")
            except:
                pass
                
    except ProcessLookupError:
        click.secho(f"Status: Stopped (Stale PID file {pid} found)", fg="red")
        # Optional: prompt to clean up? For now just report.
    except Exception as e:
        click.secho(f"Status: Unknown error: {e}", fg="red")

@main.command()
def init():
    """Initialize the application configuration (.env)"""
    defaults = {}
    if os.path.exists('.env'):
        defaults = dotenv_values('.env')
        
    click.echo("Initializing Lab Manager configuration...")
    
    lab_name = click.prompt("Lab Name", default=defaults.get("LAB_NAME", "Lab Manager"))
    
    # Secret Key
    default_key = defaults.get("FLASK_SECRET_KEY", secrets.token_hex(32))
    secret_key = click.prompt("Flask Secret Key", default=default_key, hide_input=True)
    
    click.echo("Configuring Network...")
    host_ip = click.prompt("Host IP (for links)", default=defaults.get("HOST_IP", "localhost"))
    server_port = click.prompt("Server Port", default=defaults.get("SERVER_PORT", "9000"), type=int)
    allowed_hosts = click.prompt("Allowed Hosts (0.0.0.0 for all)", default=defaults.get("ALLOWED_HOSTS", "0.0.0.0"))

    click.echo("Configuring Email (SMTP)...")
    smtp_server = click.prompt("SMTP Server", default=defaults.get("SMTP_SERVER", ""))
    smtp_port = click.prompt("SMTP Port", default=defaults.get("SMTP_PORT", "587"), type=int)
    smtp_username = click.prompt("SMTP Username", default=defaults.get("SMTP_USERNAME", ""))
    smtp_password = click.prompt("SMTP Password", default=defaults.get("SMTP_PASSWORD", ""), hide_input=True)
    sender_email = click.prompt("Sender Email", default=defaults.get("SENDER_EMAIL", smtp_username))
    
    # Optional Tags
    default_tags = "Weekly,Project Update,Journal Club"
    current_tags = defaults.get("DEFAULT_MEETING_TAGS", default_tags)
    meeting_tags = click.prompt("Default Meeting Tags", default=current_tags)

    env_content = f"""# Lab Manager Configuration
LAB_NAME="{lab_name}"
FLASK_SECRET_KEY="{secret_key}"

# Network Configuration
HOST_IP="{host_ip}"
SERVER_PORT={server_port}
ALLOWED_HOSTS="{allowed_hosts}"

# Email Configuration
SMTP_SERVER="{smtp_server}"
SMTP_PORT={smtp_port}
SMTP_USERNAME="{smtp_username}"
SMTP_PASSWORD="{smtp_password}"
SENDER_EMAIL="{sender_email}"

# Optional Meetings/Tags
DEFAULT_MEETING_TAGS="{meeting_tags}"
"""
    
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            old_content = f.read()
            
        if old_content.strip() != env_content.strip():
            click.echo("\nProposed changes to .env:")
            diff = difflib.unified_diff(
                old_content.splitlines(), 
                env_content.splitlines(), 
                fromfile='.env (current)', 
                tofile='.env (new)',
                lineterm=""
            )
            for line in diff:
                color = "white"
                if line.startswith('+'): color = "green"
                elif line.startswith('-'): color = "red"
                elif line.startswith('^'): color = "blue"
                click.secho(line, fg=color)
                
            if not click.confirm('\nOverwrite existing .env?', default=False):
                click.secho("Aborted. .env not changed.", fg="yellow")
                return

    with open('.env', 'w') as f:
        f.write(env_content)
    
    click.secho("Configuration saved to .env", fg="green")
    
if __name__ == '__main__':
    main()
