from labman.lib.data import query_db, execute_db
from datetime import datetime


def get_project_by_group(group_id):
    """Get the project for a group, including tasks, documents, and recent meetings."""
    project = query_db('SELECT * FROM group_projects WHERE group_id = ?', [group_id], one=True)
    if not project:
        return None

    project_dict = dict(project)

    # Get tasks
    tasks = query_db(
        'SELECT * FROM project_tasks WHERE project_id = ? ORDER BY due_date ASC, created_at ASC',
        [project_dict['id']]
    )
    project_dict['tasks'] = [dict(t) for t in tasks]

    # Get documents linked to this project
    from labman.lib.content import get_content
    project_dict['documents'] = get_content(research_plan_id=None)
    # Use project_id column
    docs = query_db(
        '''SELECT c.*, u.name as uploaded_by_name
           FROM content c
           LEFT JOIN users u ON c.uploaded_by = u.id
           WHERE c.project_id = ?
           ORDER BY c.created_at DESC''',
        [project_dict['id']]
    )
    project_dict['documents'] = [dict(d) for d in docs]

    # Get recent 3 project meetings for the group
    from labman.lib.meetings import get_project_meetings_by_group, format_meeting_datetime
    all_meetings = get_project_meetings_by_group(group_id)
    recent_meetings = all_meetings[:3]
    for m in recent_meetings:
        m['meeting_time'] = format_meeting_datetime(m['meeting_time'])
    project_dict['recent_meetings'] = recent_meetings

    # Calculate date range for timeline
    dates = []
    for t in project_dict['tasks']:
        if t.get('start_date'):
            dates.append(str(t['start_date']).split(' ')[0])
        elif t.get('created_at'):
            dates.append(str(t['created_at']).split(' ')[0])
        if t.get('due_date'):
            dates.append(str(t['due_date']).split(' ')[0])

    project_dict['start_date'] = min(dates) if dates else None
    project_dict['end_date'] = max(dates) if dates else None

    return project_dict


def get_project_by_id(project_id):
    """Get a project by its ID."""
    project = query_db('SELECT * FROM group_projects WHERE id = ?', [project_id], one=True)
    return dict(project) if project else None


def create_project(group_id, title='Untitled Project'):
    """Create a new project for a group."""
    try:
        cursor = execute_db(
            'INSERT INTO group_projects (group_id, title) VALUES (?, ?)',
            (group_id, title)
        )
        from flask import session
        from labman.lib.audit import log_action
        log_action(session.get('user_id'), "created project", f"Group ID: {group_id}")
        return cursor.lastrowid
    except Exception as e:
        print(f"Error creating project: {e}")
        return None


def update_project(project_id, title=None, problem_statement=None, progress=None, github_link=None):
    """Update project fields."""
    try:
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if problem_statement is not None:
            updates.append("problem_statement = ?")
            params.append(problem_statement)
        if progress is not None:
            updates.append("progress = ?")
            params.append(progress)
        if github_link is not None:
            updates.append("github_link = ?")
            params.append(github_link)

        if not updates:
            return True

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(project_id)

        query = f"UPDATE group_projects SET {', '.join(updates)} WHERE id = ?"
        execute_db(query, params)
        return True
    except Exception as e:
        print(f"Error updating project: {e}")
        return False


def toggle_project_visibility(project_id):
    """Toggle project public/private visibility."""
    try:
        project = get_project_by_id(project_id)
        if not project:
            return False
        new_val = 0 if project['is_public'] else 1
        execute_db(
            'UPDATE group_projects SET is_public = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (new_val, project_id)
        )
        return True
    except Exception as e:
        print(f"Error toggling project visibility: {e}")
        return False


def update_project_comments(project_id, comments):
    """Update project comments (admin only)."""
    try:
        execute_db(
            'UPDATE group_projects SET comments = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (comments, project_id)
        )
        try:
            from flask import session
            from labman.lib.audit import log_action
            log_action(session.get('user_id'), "updated project comments", f"Project ID: {project_id}")
        except Exception:
            pass
        return True
    except Exception as e:
        print(f"Error updating project comments: {e}")
        return False


# --- Project Task CRUD ---

def add_project_task(project_id, task_name, due_date, status='pending', start_date=None):
    """Add a new task to a project."""
    try:
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        execute_db(
            'INSERT INTO project_tasks (project_id, task_name, due_date, status, start_date) VALUES (?, ?, ?, ?, ?)',
            (project_id, task_name, due_date, status, start_date)
        )
        return True
    except Exception as e:
        print(f"Error adding project task: {e}")
        return False


def update_project_task_status(task_id, status):
    """Update project task status."""
    try:
        execute_db('UPDATE project_tasks SET status = ? WHERE id = ?', (status, task_id))
        return True
    except Exception as e:
        print(f"Error updating project task status: {e}")
        return False


def delete_project_task(task_id):
    """Delete a project task."""
    try:
        execute_db('DELETE FROM project_tasks WHERE id = ?', (task_id,))
        return True
    except Exception as e:
        print(f"Error deleting project task: {e}")
        return False


def get_project_task_by_id(task_id):
    """Get a project task by ID."""
    task = query_db('SELECT * FROM project_tasks WHERE id = ?', [task_id], one=True)
    return dict(task) if task else None


def update_project_task_due_date(task_id, new_due_date):
    """Update project task due date with history tracking."""
    try:
        current_task = get_project_task_by_id(task_id)
        if not current_task:
            return False
        if current_task.get('due_date'):
            old_date = str(current_task['due_date']).split(' ')[0]
            if old_date != new_due_date:
                execute_db(
                    'UPDATE project_tasks SET due_date = ?, previous_due_date = ? WHERE id = ?',
                    (new_due_date, old_date, task_id)
                )
            else:
                execute_db('UPDATE project_tasks SET due_date = ? WHERE id = ?', (new_due_date, task_id))
        else:
            execute_db('UPDATE project_tasks SET due_date = ? WHERE id = ?', (new_due_date, task_id))
        return True
    except Exception as e:
        print(f"Error updating project task due date: {e}")
        return False


def update_project_task_start_date(task_id, new_start_date):
    """Update project task start date."""
    try:
        execute_db('UPDATE project_tasks SET start_date = ? WHERE id = ?', (new_start_date, task_id))
        return True
    except Exception as e:
        print(f"Error updating project task start date: {e}")
        return False


def has_project(group_id):
    """Check if a group has a project."""
    project = query_db('SELECT id FROM group_projects WHERE group_id = ?', [group_id], one=True)
    return project is not None
