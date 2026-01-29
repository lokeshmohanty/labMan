from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify, abort
from functools import wraps
import os
from werkzeug.middleware.proxy_fix import ProxyFix
from labman.lib.data import init_db, get_db
# ... imports ...
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Fix for gunicorn
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

@app.before_request
def check_allowed_hosts():
    allowed = os.getenv('ALLOWED_HOSTS', '0.0.0.0')
    if allowed == '0.0.0.0':
        return
    
    host = request.host.split(':')[0]
    if host not in allowed.split(','):
        abort(403)
from labman.lib.auth import login_user, logout_user, require_login, require_admin, get_current_user
from labman.lib.audit import get_audit_logs
from labman.lib.users import create_user, get_all_users, update_user, delete_user, get_user_by_id, update_user_password, create_password_reset_token, verify_reset_token, update_user_notifications, get_latest_activation_token, resend_activation_email
from labman.lib.users import update_user_profile, verify_email_change
from labman.lib.groups import create_group, get_all_groups, get_all_groups_with_counts, add_user_to_group, remove_user_from_group, get_user_groups, get_group_members, get_group_by_id, update_group, delete_group
from labman.lib.meetings import create_meeting, get_all_meetings, update_meeting, delete_meeting, get_meeting_by_id, get_meetings_this_week, get_meetings_by_month, record_meeting_response, get_meeting_responses, get_meetings_by_tags, format_meeting_datetime, get_all_tags
from labman.lib.content import upload_content, get_content, delete_content, get_content_by_id, check_content_access, get_content_by_share_link, get_content_by_group, update_content
from labman.lib.inventory import add_inventory_item, get_all_inventory, update_inventory_item, delete_inventory_item
from labman.lib.servers import add_server, get_all_servers, update_server, delete_server, get_server_by_id
from labman.lib.research import get_research_plan, update_research_problem, add_research_task, update_research_task_status, delete_research_task, get_task_by_id, update_research_links, update_task_due_date, update_task_start_date

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'data', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    init_db()

@app.context_processor
def inject_lab_info():
    return dict(lab_name=os.getenv('LAB_NAME', 'Lab Manager'), min=min, max=max)

@app.template_filter('date_diff')
def date_diff(d1, d2):
    """Return difference in days between two date strings (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"""
    if not d1 or not d2:
        return 0
    try:
        # Handle timestamps
        if ' ' in str(d1): d1 = str(d1).split(' ')[0]
        if ' ' in str(d2): d2 = str(d2).split(' ')[0]
        
        date1 = datetime.strptime(str(d1), '%Y-%m-%d')
        date2 = datetime.strptime(str(d2), '%Y-%m-%d')
        return (date1 - date2).days
    except:
        return 0

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = login_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/research/links', methods=['POST'])
def update_research_links_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    github_link = request.form.get('github_link')
    manuscript_link = request.form.get('manuscript_link')
    
    if update_research_links(session['user_id'], github_link, manuscript_link):
        flash('Research links updated successfully!', 'success')
    else:
        flash('Error updating research links', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@require_login
def dashboard():
    user = get_current_user()
    recent_meetings = get_meetings_this_week()[:3]
    for meeting in recent_meetings:
        meeting['meeting_time'] = format_meeting_datetime(meeting['meeting_time'])
    user_groups = [g for g in get_user_groups(user['id'])]
    
    # Get research plan
    research_plan = get_research_plan(user['id'])
    
    today = datetime.now().date()
    current_date = today.strftime('%Y-%m-%d')
    timeline_start = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    timeline_end = (today + timedelta(days=14)).strftime('%Y-%m-%d')
    
    return render_template('dashboard.html', user=user, meetings=recent_meetings, groups=user_groups, research_plan=research_plan, timeline_start=timeline_start, timeline_end=timeline_end, current_date=current_date)

# User Management
@app.route('/users')
@require_login
def users():
    all_users = get_all_users()
    
    # Add status and token info
    for user in all_users:
        if user['password_hash'] is None:
            user['status'] = 'pending'
            token = get_latest_activation_token(user['id'])
            user['token_info'] = token
        else:
            user['status'] = 'active'
            
    return render_template('users.html', users=all_users)
# ... users/create route ...

@app.route('/members/<int:user_id>/research')
@require_login
def member_research(user_id):
    target_user = get_user_by_id(user_id)
    if not target_user:
        flash('User not found', 'error')
        return redirect(url_for('research'))
    
    plan = get_research_plan(user_id)
    
    today = datetime.now().date()
    timeline_start = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    timeline_end = (today + timedelta(days=14)).strftime('%Y-%m-%d')
    
    return render_template('member_research.html', target_user=target_user, plan=plan, timeline_start=timeline_start, timeline_end=timeline_end)
@app.route('/users/create', methods=['GET', 'POST'])
@require_admin
def create_user_route():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        is_admin = request.form.get('is_admin') == 'on'
        
        if create_user(name, email, None, is_admin):
            flash('User created! Activation email sent.', 'success')
            return redirect(url_for('users'))
        else:
            flash('Failed to create user', 'error')
    
    return render_template('user_form.html')

@app.route('/users/<int:user_id>/resend-invitation', methods=['POST'])
@require_admin
def resend_invitation(user_id):
    if resend_activation_email(user_id):
        flash('Invitation email resent successfully!', 'success')
    else:
        flash('Failed to resend invitation email', 'error')
    return redirect(url_for('users'))

@app.route('/activate/<token>', methods=['GET', 'POST'])
def activate_account(token):
    user_id = verify_reset_token(token)
    
    if not user_id:
        flash('Invalid or expired activation link', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('activate_account.html', token=token)
        
        if update_user_password(user_id, new_password):
            from labman.lib.data import execute_db
            execute_db('UPDATE password_reset_tokens SET used = 1 WHERE user_id = ? AND token = ?', 
                      (user_id, token))
            flash('Account activated! Please login with your password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Failed to activate account', 'error')
    
    return render_template('activate_account.html', token=token)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@require_admin
def edit_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('users'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        is_admin = request.form.get('is_admin') == 'on'
        
        if update_user(user_id, name, email, is_admin):
            flash('User updated successfully!', 'success')
            return redirect(url_for('users'))
        else:
            flash('Failed to update user', 'error')
    
    return render_template('user_form.html', user=user)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
@require_admin
def delete_user_route(user_id):
    if delete_user(user_id):
        flash('User deleted successfully!', 'success')
    else:
        flash('Failed to delete user', 'error')
    return redirect(url_for('users'))

@app.route('/profile/change-password', methods=['GET', 'POST'])
@require_login
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user = get_current_user()
        
        if not login_user(user['email'], current_password):
            flash('Current password is incorrect', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('change_password.html')
        
        if update_user_password(user['id'], new_password):
            flash('Password changed successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Failed to change password', 'error')
    
    return render_template('change_password.html')

@app.route('/profile/notifications', methods=['POST'])
@require_login
def update_notifications():
    user = get_current_user()
    enabled = request.form.get('notifications') == 'on'
    if update_user_notifications(user['id'], enabled):
        flash('Notification preferences updated!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/profile/edit', methods=['GET', 'POST'])
@require_login
def edit_profile():
    user = get_current_user()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        result = update_user_profile(user['id'], name, email)
        if result == 'verification_sent':
            flash('Profile updated! Please check the new email to verify the change.', 'success')
        elif result:
            flash('Profile updated successfully!', 'success')
        else:
            flash('Failed to update profile', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_profile.html', user=user)

@app.route('/verify-email/<token>')
@require_login
def verify_email(token):
    user_id = verify_reset_token(token)
    new_email = request.args.get('email')
    
    if user_id and new_email and verify_email_change(user_id, new_email):
        flash('Email verified and updated successfully!', 'success')
    else:
        flash('Invalid or expired verification link', 'error')
    return redirect(url_for('dashboard'))

@app.route('/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@require_admin
def admin_reset_password(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('users'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('admin_reset_password.html', user=user)
        
        if update_user_password(user_id, new_password):
            flash(f'Password reset successfully for {user["name"]}!', 'success')
            return redirect(url_for('users'))
        else:
            flash('Failed to reset password', 'error')
    
    return render_template('admin_reset_password.html', user=user)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        from labman.lib.users import get_user_by_email, send_password_reset_email
        user = get_user_by_email(email)
        
        if user:
            token = create_password_reset_token(user['id'])
            reset_link = url_for('reset_password', token=token, _external=True)
            
            if send_password_reset_email(email, user['name'], reset_link):
                flash('Password reset instructions have been sent to your email', 'success')
            else:
                flash('Failed to send email. Please contact administrator.', 'error')
        else:
            flash('If that email exists, password reset instructions have been sent', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_id = verify_reset_token(token)
    
    if not user_id:
        flash('Invalid or expired reset link', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        if update_user_password(user_id, new_password):
            from labman.lib.data import execute_db
            execute_db('UPDATE password_reset_tokens SET used = 1 WHERE user_id = ? AND token = ?', 
                      (user_id, token))
            flash('Password reset successfully! Please login with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Failed to reset password', 'error')
    
    return render_template('reset_password.html', token=token)

# Group Management
@app.route('/groups')
@require_login
def groups():
    all_groups = get_all_groups_with_counts()
    return render_template('groups.html', groups=all_groups)

@app.route('/groups/create', methods=['GET', 'POST'])
@require_login
def create_group_route():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id')
        lead_id = session.get('user_id') # Current user is lead by default
        
        if create_group(name, description, parent_id if parent_id else None, lead_id):
            flash('Group created successfully!', 'success')
            return redirect(url_for('groups'))
        else:
            flash('Failed to create group', 'error')
    
    all_groups = get_all_groups()
    lab_name = os.getenv('LAB_NAME', 'Lab Manager')
    lab_group = next((g for g in all_groups if g['name'] == lab_name), None)
    return render_template('group_form.html', groups=all_groups, lab_group=lab_group)


@app.route('/groups/<int:group_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_group(group_id):
    group = get_group_by_id(group_id)
    if not group:
        flash('Group not found', 'error')
        return redirect(url_for('groups'))
    
    # Check permissions: Admin or Group Lead
    if not session.get('is_admin') and group.get('lead_id') != session.get('user_id'):
        flash('Only admins or the group lead can edit this group', 'error')
        return redirect(url_for('group_detail', group_id=group_id))
        
    if group['name'] == os.getenv('LAB_NAME', 'Lab Manager'):
        flash('Cannot edit the default Lab group', 'error')
        return redirect(url_for('groups'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id')
        lead_id = request.form.get('lead_id') or group['lead_id'] # Allow changing lead
        
        if update_group(group_id, name, description, parent_id if parent_id else None, lead_id):
            flash('Group updated successfully!', 'success')
            return redirect(url_for('groups'))
        else:
            flash('Failed to update group', 'error')
    
    all_groups = [g for g in get_all_groups() if g['id'] != group_id]
    all_users = get_all_users()
    return render_template('group_form.html', group=group, groups=all_groups, all_users=all_users)

@app.route('/groups/<int:group_id>')
@require_login
def group_detail(group_id):
    group = get_group_by_id(group_id)
    if not group:
        flash('Group not found', 'error')
        return redirect(url_for('groups'))
    
    members = get_group_members(group_id)
    all_users = get_all_users()
    return render_template('group_detail.html', group=group, members=members, all_users=all_users)

@app.route('/groups/<int:group_id>/add_member', methods=['POST'])
@require_login
def add_member(group_id):
    group = get_group_by_id(group_id)
    if not session.get('is_admin') and (not group or group.get('lead_id') != session.get('user_id')):
        flash('Unauthorized', 'error')
        return redirect(url_for('group_detail', group_id=group_id))
        
    user_id = request.form.get('user_id')
    if add_user_to_group(user_id, group_id):
        flash('Member added successfully!', 'success')
    else:
        flash('Failed to add member', 'error')
    return redirect(url_for('group_detail', group_id=group_id))

@app.route('/groups/<int:group_id>/remove_member/<int:user_id>', methods=['POST'])
@require_login
def remove_member(group_id, user_id):
    group = get_group_by_id(group_id)
    if not session.get('is_admin') and (not group or group.get('lead_id') != session.get('user_id')):
        flash('Unauthorized', 'error')
        return redirect(url_for('group_detail', group_id=group_id))
        
    if remove_user_from_group(user_id, group_id):
        flash('Member removed successfully!', 'success')
    else:
        flash('Failed to remove member', 'error')
    return redirect(url_for('group_detail', group_id=group_id))


@app.route('/groups/<int:group_id>/delete', methods=['POST'])
@require_login
def delete_group_route(group_id):
    group = get_group_by_id(group_id)
    if not group:
        flash('Group not found', 'error')
        return redirect(url_for('groups'))
    
    if not session.get('is_admin') and group.get('lead_id') != session.get('user_id'):
        flash('Unauthorized', 'error')
        return redirect(url_for('group_detail', group_id=group_id))
        
    if group['name'] == os.getenv('LAB_NAME', 'Lab Manager'):
        flash('Cannot delete the default Lab group', 'error')
        return redirect(url_for('groups'))
    
    if delete_group(group_id):
        flash('Group deleted successfully!', 'success')
    else:
        flash('Failed to delete group', 'error')
    return redirect(url_for('groups'))

@app.route('/research')
@require_login
def research():
    from labman.lib.groups import get_research_tree
    tree = get_research_tree()
    return render_template('research.html', tree=tree)

# Meeting Management
@app.route('/meetings')
@require_login
def meetings():
    tag_filter = request.args.get('tag')
    if tag_filter:
        all_meetings = get_meetings_by_tags([tag_filter])
    else:
        all_meetings = get_all_meetings()

    this_week = get_meetings_this_week()

    for meeting in all_meetings:
        meeting['meeting_time'] = format_meeting_datetime(meeting['meeting_time'])
    for meeting in this_week:
        meeting['meeting_time'] = format_meeting_datetime(meeting['meeting_time'])
    
    # Get available tags for filter
    default_tags = [t.strip() for t in os.getenv('DEFAULT_MEETING_TAGS', '').split(',') if t.strip()]
    db_tags = get_all_tags()
    available_tags = sorted(list(set(default_tags + db_tags)))
    
    return render_template('meetings.html', meetings=all_meetings, this_week=this_week, available_tags=available_tags)

@app.route('/meetings/calendar/<int:year>/<int:month>')
@require_login
def meeting_calendar_data(year, month):
    meetings = get_meetings_by_month(year, month)
    return jsonify({'meetings': meetings})

@app.route('/meetings/create', methods=['GET', 'POST'])
@require_login
def create_meeting_route():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        meeting_time = request.form.get('meeting_time')
        group_id = request.form.get('group_id')
        tags_str = request.form.get('tags', '')
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        
        user = get_current_user()
        if create_meeting(title, description, meeting_time, user['id'], group_id, tags):
            flash('Meeting created successfully!', 'success')
            return redirect(url_for('meetings'))
        else:
            flash('Failed to create meeting', 'error')
    
    user = get_current_user()
    user_groups = get_user_groups(user['id'])
    
    # Get available tags
    default_tags = [t.strip() for t in os.getenv('DEFAULT_MEETING_TAGS', '').split(',') if t.strip()]
    db_tags = get_all_tags()
    available_tags = sorted(list(set(default_tags + db_tags)))
    
    # Set default time to now
    default_time = datetime.now().strftime('%Y-%m-%dT%H:%M')
    
    return render_template('meeting_form.html', groups=user_groups, available_tags=available_tags, default_time=default_time)

@app.route('/meetings/<int:meeting_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_meeting(meeting_id):
    meeting = get_meeting_by_id(meeting_id)
    if not meeting:
        flash('Meeting not found', 'error')
        return redirect(url_for('meetings'))
    
    user = get_current_user()
    # Only organizer or admin can edit
    if not user['is_admin'] and meeting['created_by'] != user['id']:
        flash('Only the organizer or admin can edit this meeting', 'error')
        return redirect(url_for('meeting_detail', meeting_id=meeting_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        new_time = request.form.get('meeting_time')
        group_id = request.form.get('group_id')
        tags_str = request.form.get('tags', '')
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        
        # Check if time changed
        old_time = meeting['meeting_time']
        time_changed = (new_time != old_time)
        
        if update_meeting(meeting_id, title, description, new_time, group_id, tags, send_notification=time_changed):
            flash('Meeting updated successfully!', 'success')
            return redirect(url_for('meeting_detail', meeting_id=meeting_id))
        else:
            flash('Failed to update meeting', 'error')
    
    user_groups = get_user_groups(user['id'])
    # Parse existing tags
    meeting['tags_list'] = meeting['tags'].split(',') if meeting.get('tags') else []
    
    # Get available tags
    default_tags = [t.strip() for t in os.getenv('DEFAULT_MEETING_TAGS', '').split(',') if t.strip()]
    db_tags = get_all_tags()
    available_tags = sorted(list(set(default_tags + db_tags)))
    
    return render_template('meeting_form.html', meeting=meeting, groups=user_groups, is_edit=True, available_tags=available_tags)

@app.route('/meetings/<int:meeting_id>/delete', methods=['POST'])
@require_login
def delete_meeting_route(meeting_id):
    meeting = get_meeting_by_id(meeting_id)
    if not meeting:
        flash('Meeting not found', 'error')
        return redirect(url_for('meetings'))
    
    user = get_current_user()
    # Only organizer or admin can delete
    if not user['is_admin'] and meeting['created_by'] != user['id']:
        flash('Only the organizer or admin can delete this meeting', 'error')
        return redirect(url_for('meeting_detail', meeting_id=meeting_id))
    
    if delete_meeting(meeting_id):
        flash('Meeting deleted successfully!', 'success')
    else:
        flash('Failed to delete meeting', 'error')
    return redirect(url_for('meetings'))

@app.route('/meetings/<int:meeting_id>')
@require_login
def meeting_detail(meeting_id):
    meeting = get_meeting_by_id(meeting_id)
    if not meeting:
        flash('Meeting not found', 'error')
        return redirect(url_for('meetings'))
    
    # Format datetime
    meeting['meeting_time'] = format_meeting_datetime(meeting['meeting_time'])
    
    # Check if user can edit
    user = get_current_user()
    can_edit = user['is_admin'] or meeting['created_by'] == user['id']
    
    contents = get_content(meeting_id=meeting_id)
    responses = get_meeting_responses(meeting_id)
    return render_template('meeting_detail.html', meeting=meeting, contents=contents, responses=responses, can_edit=can_edit)

@app.route('/meetings/<int:meeting_id>/respond', methods=['POST'])
@require_login
def respond_to_meeting(meeting_id):
    response = request.form.get('response')
    user = get_current_user()
    if record_meeting_response(meeting_id, user['id'], response):
        flash('Response recorded!', 'success')
    else:
        flash('Failed to record response', 'error')
    return redirect(url_for('meeting_detail', meeting_id=meeting_id))

# Content Management
@app.route('/content')
@require_login
def content():
    user = get_current_user()
    group_filter = request.args.get('group_id')
    
    if group_filter:
        all_content = get_content_by_group(int(group_filter))
    else:
        all_content = get_content(user_id=None)
    
    user_groups = get_user_groups(user['id'])
    return render_template('content.html', contents=all_content, groups=user_groups)

@app.route('/content/upload', methods=['GET', 'POST'])
@require_login
def upload_content_route():
    if request.method == 'POST':
        file = request.files.get('file')
        title = request.form.get('title')
        description = request.form.get('description')
        group_id = request.form.get('group_id')
        meeting_id = request.form.get('meeting_id')
        
        user = get_current_user()
        
        if file and upload_content(file, title, description, user['id'], group_id, meeting_id, upload_folder=app.config['UPLOAD_FOLDER']):
            flash('Content uploaded successfully!', 'success')
            return redirect(url_for('content'))
        else:
            flash('Failed to upload content', 'error')
    
    user = get_current_user()
    user_groups = get_user_groups(user['id'])
    meetings = get_all_meetings()
    
    # Pre-select meeting if meeting_id is provided in URL
    selected_meeting_id = request.args.get('meeting_id')
    selected_group_id = None
    
    if selected_meeting_id:
        # Also find the group associated with this meeting to pre-select it
        meeting = next((m for m in meetings if str(m['id']) == str(selected_meeting_id)), None)
        if meeting:
            selected_group_id = meeting['group_id']
            
    return render_template('content_form.html', 
                         groups=user_groups, 
                         meetings=meetings, 
                         selected_meeting_id=selected_meeting_id,
                         selected_group_id=selected_group_id)

@app.route('/content/<int:content_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_content(content_id):
    content_item = get_content_by_id(content_id)
    if not content_item:
        flash('Content not found', 'error')
        return redirect(url_for('content'))
    
    user = get_current_user()
    # Only uploader or admin can edit
    if not user['is_admin'] and content_item['uploaded_by'] != user['id']:
        flash('Only the uploader or admin can edit this content', 'error')
        return redirect(url_for('content'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        group_id = request.form.get('group_id')
        meeting_id = request.form.get('meeting_id')
        
        if update_content(content_id, title, description, group_id, meeting_id):
            flash('Content updated successfully!', 'success')
            return redirect(url_for('content'))
        else:
            flash('Failed to update content', 'error')
    
    user_groups = get_user_groups(user['id'])
    meetings = get_all_meetings()
    return render_template('content_form.html', content=content_item, groups=user_groups, meetings=meetings, is_edit=True)

@app.route('/content/<int:content_id>/delete', methods=['POST'])
@require_login
def delete_content_route(content_id):
    content_item = get_content_by_id(content_id)
    if not content_item:
        flash('Content not found', 'error')
        return redirect(url_for('content'))
    
    user = get_current_user()
    # Only uploader or admin can delete
    if not user['is_admin'] and content_item['uploaded_by'] != user['id']:
        flash('Only the uploader or admin can delete this content', 'error')
        return redirect(url_for('content'))
    
    if delete_content(content_id):
        flash('Content deleted successfully!', 'success')
    else:
        flash('Failed to delete content', 'error')
    
    # Redirect back to where the request came from (e.g. dashboard)
    return redirect(request.referrer or url_for('content'))

@app.route('/content/<int:content_id>/download')
def download_content(content_id):
    user = get_current_user() if 'user_id' in session else None
    content_item = get_content_by_id(content_id)
    
    if not content_item:
        flash('Content not found', 'error')
        return redirect(url_for('content'))
    
    if not check_content_access(content_id, user['id'] if user else None):
        flash('Access denied', 'error')
        return redirect(url_for('content'))
    
    download_name = content_item['filename']
    return send_file(content_item['file_path'], as_attachment=True, download_name=download_name)

@app.route('/share/<share_link>')
def shared_content(share_link):
    content_item = get_content_by_share_link(share_link)
    
    if not content_item:
        flash('Content not found or link expired', 'error')
        return redirect(url_for('login'))
    
    return send_file(content_item['file_path'], as_attachment=True, download_name=content_item['filename'])

# Inventory Management
@app.route('/inventory')
@require_login
def inventory():
    all_inventory = get_all_inventory()
    all_servers = get_all_servers()
    return render_template('inventory.html', inventory=all_inventory, servers=all_servers)

@app.route('/inventory/add', methods=['GET', 'POST'])
@require_login
def add_inventory():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        quantity = request.form.get('quantity')
        location = request.form.get('location')
        
        if add_inventory_item(name, description, quantity, location):
            flash('Inventory item added successfully!', 'success')
            return redirect(url_for('inventory'))
        else:
            flash('Failed to add inventory item', 'error')
    
    return render_template('inventory_form.html')

@app.route('/inventory/<int:item_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_inventory(item_id):
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        quantity = request.form.get('quantity')
        location = request.form.get('location')
        
        if update_inventory_item(item_id, name, description, quantity, location):
            flash('Inventory item updated successfully!', 'success')
            return redirect(url_for('inventory'))
        else:
            flash('Failed to update inventory item', 'error')
    
    from labman.lib.data import query_db
    item = query_db('SELECT * FROM inventory WHERE id = ?', (item_id,), one=True)
    return render_template('inventory_form.html', item=item)

@app.route('/inventory/<int:item_id>/delete', methods=['POST'])
@require_admin
def delete_inventory_route(item_id):
    if delete_inventory_item(item_id):
        flash('Inventory item deleted successfully!', 'success')
    else:
        flash('Failed to delete inventory item', 'error')
    return redirect(url_for('inventory'))

# Server Management
@app.route('/servers/add', methods=['GET', 'POST'])
@require_login
def add_server_route():
    if request.method == 'POST':
        hostname = request.form.get('hostname')
        ip_address = request.form.get('ip_address')
        admin_name = request.form.get('admin_name')
        location = request.form.get('location')
        description = request.form.get('description')
        
        if add_server(hostname, ip_address, admin_name, location, description):
            flash('Server added successfully!', 'success')
            return redirect(url_for('inventory'))
        else:
            flash('Failed to add server', 'error')
    
    return render_template('server_form.html')

@app.route('/servers/<int:server_id>/edit', methods=['GET', 'POST'])
@require_admin
def edit_server(server_id):
    server = get_server_by_id(server_id)
    if not server:
        flash('Server not found', 'error')
        return redirect(url_for('inventory'))
    
    if request.method == 'POST':
        hostname = request.form.get('hostname')
        ip_address = request.form.get('ip_address')
        admin_name = request.form.get('admin_name')
        location = request.form.get('location')
        description = request.form.get('description')
        
        if update_server(server_id, hostname, ip_address, admin_name, location, description):
            flash('Server updated successfully!', 'success')
            return redirect(url_for('inventory'))
        else:
            flash('Failed to update server', 'error')
    
    return render_template('server_form.html', server=server)

@app.route('/servers/<int:server_id>/delete', methods=['POST'])
@require_admin
def delete_server_route(server_id):
    if delete_server(server_id):
        flash('Server deleted successfully!', 'success')
    else:
        flash('Failed to delete server', 'error')
    return redirect(url_for('inventory'))

# Research Plan Management
@app.route('/dashboard/research/update', methods=['POST'])
@require_login
def update_research_problem_route():
    user = get_current_user()
    problem_statement = request.form.get('problem_statement')
    research_progress = request.form.get('research_progress')
    
    if update_research_problem(user['id'], problem_statement, research_progress):
        flash('Research plan updated!', 'success')
    else:
        flash('Failed to update research plan', 'error')
    return redirect(url_for('dashboard'))

@app.route('/dashboard/research/upload_doc', methods=['POST'])
@require_login
def upload_research_document_route():
    user = get_current_user()
    file = request.files.get('file')
    title = request.form.get('title')
    description = request.form.get('description')
    
    if not title:
        title = file.filename if file else "Untitled Document"
        
    if file and upload_content(file, title, description, user['id'], research_plan_id=user['id'], access_level='link', upload_folder=app.config['UPLOAD_FOLDER']):
        flash('Document uploaded successfully!', 'success')
    else:
        flash('Failed to upload document', 'error')
    return redirect(url_for('dashboard'))

@app.route('/dashboard/tasks/add', methods=['POST'])
@require_login
def add_research_task_route():
    user = get_current_user()
    task_name = request.form.get('task_name')
    due_date = request.form.get('due_date')
    start_date = request.form.get('start_date')
    status = request.form.get('status', 'pending')
    
    if add_research_task(user['id'], task_name, due_date, status, start_date):
        flash('Task added successfully!', 'success')
    else:
        flash('Failed to add task', 'error')
    return redirect(url_for('dashboard'))

@app.route('/dashboard/tasks/<int:task_id>/update', methods=['POST'])
@require_login
def update_research_task_route(task_id):
    user = get_current_user()
    status = request.form.get('status')
    
    # Check ownership
    task = get_task_by_id(task_id)
    if not task or task['user_id'] != user['id']:
        flash('Task not found or unauthorized', 'error')
        return redirect(url_for('dashboard'))
    
    if update_research_task_status(task_id, status):
        flash('Task updated!', 'success')
    else:
        flash('Failed to update task', 'error')
    return redirect(url_for('dashboard'))

@app.route('/dashboard/tasks/<int:task_id>/delete', methods=['POST'])
@require_login
def delete_research_task_route(task_id):
    user = get_current_user()
    
    # Check ownership
    task = get_task_by_id(task_id)
    if not task or task['user_id'] != user['id']:
        flash('Task not found or unauthorized', 'error')
        return redirect(url_for('dashboard'))
    
    if delete_research_task(task_id):
        flash('Task deleted!', 'success')
    else:
        flash('Failed to delete task', 'error')
    return redirect(url_for('dashboard'))
@app.route('/dashboard/tasks/<int:task_id>/update-date', methods=['POST'])
@require_login
def update_task_date_route(task_id):
    due_date = request.form.get('due_date')
    if update_task_due_date(task_id, due_date):
        flash('Due date updated!', 'success')
    else:
        flash('Failed to update due date', 'error')
    return redirect(url_for('dashboard'))

@app.route('/dashboard/tasks/<int:task_id>/update-start-date', methods=['POST'])
@require_login
def update_task_start_date_route(task_id):
    start_date = request.form.get('start_date')
    if update_task_start_date(task_id, start_date):
        flash('Start date updated!', 'success')
    else:
        flash('Failed to update start date', 'error')
    return redirect(url_for('dashboard'))

@app.route('/history')
@require_login
def history_route():
    user = get_current_user()
    
    # Filtering parameters (admin only)
    filter_user_id = request.args.get('user_id')
    filter_action = request.args.get('action')
    
    if user['is_admin']:
        # Admins can see everything and filter
        logs = get_audit_logs(limit=200, user_id=filter_user_id, action=filter_action)
        all_users = get_all_users()
        return render_template('audit_history.html', logs=logs, all_users=all_users, 
                             filter_user_id=filter_user_id, filter_action=filter_action)
    else:
        # Regular users only see their own logs
        logs = get_audit_logs(limit=100, user_id=user['id'])
        return render_template('audit_history.html', logs=logs)

@app.route('/groups/<int:group_id>/set-lead/<int:user_id>', methods=['POST'])
@require_admin
def set_group_lead_route(group_id, user_id):
    group = get_group_by_id(group_id)
    if not group:
        flash('Group not found', 'error')
        return redirect(url_for('groups'))
    
    if update_group(group_id, group['name'], group['description'], group['parent_id'], user_id):
        flash('Group lead updated successfully', 'success')
    else:
        flash('Failed to update group lead', 'error')
    return redirect(url_for('group_detail', group_id=group_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
