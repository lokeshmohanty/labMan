from labman.lib.data import query_db, execute_db
from datetime import datetime

def get_research_plan(user_id):
    """Get research problem, progress, tasks and documents for a user"""
    # Get problem statement and progress
    plan = query_db('SELECT * FROM research_plans WHERE user_id = ?', [user_id], one=True)
    plan_dict = dict(plan) if plan else {}
    problem_statement = plan_dict.get('problem_statement', "")
    research_progress = plan_dict.get('research_progress', "")
    github_link = plan_dict.get('github_link', "")
    manuscript_link = plan_dict.get('manuscript_link', "")
    
    # Get tasks
    tasks = query_db('SELECT * FROM research_tasks WHERE user_id = ? ORDER BY due_date ASC, created_at ASC', [user_id])
    tasks_list = [dict(task) for task in tasks]
    
    # Get related documents
    from labman.lib.content import get_content
    documents = get_content(research_plan_id=user_id)
    
    # Calculate date range
    start_date = None
    end_date = None
    dates = []
    
    for t in tasks_list:
        if t.get('start_date'):
            dates.append(str(t['start_date']).split(' ')[0])
        elif t.get('created_at'):
            dates.append(str(t['created_at']).split(' ')[0])
        if t.get('due_date'):
            dates.append(str(t['due_date']).split(' ')[0])
            
    if dates:
        start_date = min(dates)
        end_date = max(dates)
        
    return {
        'problem_statement': problem_statement,
        'research_progress': research_progress,
        'github_link': github_link,
        'manuscript_link': manuscript_link,
        'comments': plan_dict.get('comments', ''),
        'tasks': tasks_list,
        'documents': documents,
        'start_date': start_date,
        'end_date': end_date
    }

def update_research_problem(user_id, problem_statement=None, research_progress=None):
    """Update research problem statement and progress independently"""
    try:
        # Check if record exists first
        existing = query_db('SELECT * FROM research_plans WHERE user_id = ?', [user_id], one=True)
        
        if not existing:
            # Create new record with whatever is provided
            execute_db('''
                INSERT INTO research_plans (user_id, problem_statement, research_progress) 
                VALUES (?, ?, ?)
            ''', (user_id, problem_statement or "", research_progress or ""))
            return True

        # Build update query dynamically based on provided fields
        updates = []
        params = []
        
        if problem_statement is not None:
            updates.append("problem_statement = ?")
            params.append(problem_statement)
            
        if research_progress is not None:
            updates.append("research_progress = ?")
            params.append(research_progress)
            
        if not updates:
            return True # Nothing to update
            
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        
        query = f"UPDATE research_plans SET {', '.join(updates)} WHERE user_id = ?"
        execute_db(query, params)
            
        return True
    except Exception as e:
        print(f"Error updating research plan: {e}")
        return False

def add_research_task(user_id, task_name, due_date, status='pending', start_date=None):
    """Add a new research task"""
    try:
        from datetime import datetime
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
            
        execute_db('''
            INSERT INTO research_tasks (user_id, task_name, due_date, status, start_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, task_name, due_date, status, start_date))
        return True
    except Exception as e:
        print(f"Error adding research task: {e}")
        return False

def update_research_task_status(task_id, status):
    """Update research task status"""
    try:
        execute_db('UPDATE research_tasks SET status = ? WHERE id = ?', (status, task_id))
        return True
    except Exception as e:
        print(f"Error updating research task: {e}")
        return False

def delete_research_task(task_id):
    """Delete a research task"""
    try:
        execute_db('DELETE FROM research_tasks WHERE id = ?', (task_id,))
        return True
    except Exception as e:
        print(f"Error deleting research task: {e}")
        return False

def get_task_by_id(task_id):
    """Get a task by ID"""
    task = query_db('SELECT * FROM research_tasks WHERE id = ?', [task_id], one=True)
    return dict(task) if task else None

def update_research_links(user_id, github_link, manuscript_link):
    """Update research links"""
    try:
        execute_db('''
            INSERT INTO research_plans (user_id, github_link, manuscript_link) 
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            github_link = excluded.github_link,
            manuscript_link = excluded.manuscript_link,
            updated_at = CURRENT_TIMESTAMP
        ''', (user_id, github_link, manuscript_link))
        return True
    except Exception as e:
        print(f"Error updating research links: {e}")
        return False

def update_task_due_date(task_id, new_due_date):
    """Update research task due date with history tracking"""
    try:
        # Get current task to check existing due date
        current_task = get_task_by_id(task_id)
        if not current_task:
            print(f"Task {task_id} not found")
            return False
            
        if current_task.get('due_date'):
            old_date = str(current_task['due_date']).split(' ')[0]
            if old_date != new_due_date:
                execute_db('UPDATE research_tasks SET due_date = ?, previous_due_date = ? WHERE id = ?', 
                          (new_due_date, old_date, task_id))
            else:
                 # Date didn't change, just update normally (or do nothing)
                 execute_db('UPDATE research_tasks SET due_date = ? WHERE id = ?', (new_due_date, task_id))
        else:
             # No previous date, just update
             execute_db('UPDATE research_tasks SET due_date = ? WHERE id = ?', (new_due_date, task_id))
        return True
    except Exception as e:
        print(f"Error updating task due date: {e}")
        return False

def update_task_start_date(task_id, new_start_date):
    """Update research task start date"""
    try:
        execute_db('UPDATE research_tasks SET start_date = ? WHERE id = ?', (new_start_date, task_id))
        return True
    except Exception as e:
        print(f"Error updating task start date: {e}")
        return False

def update_research_comments(user_id, comments):
    """Update research comments (admin/group lead only)"""
    try:
        # Check if record exists first
        existing = query_db('SELECT * FROM research_plans WHERE user_id = ?', [user_id], one=True)
        
        if not existing:
            # Create new record with comments
            execute_db('''
                INSERT INTO research_plans (user_id, comments) 
                VALUES (?, ?)
            ''', (user_id, comments))
        else:
            # Update existing record
            execute_db('''
                UPDATE research_plans 
                SET comments = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            ''', (comments, user_id))
        
        # Log action (optional - don't fail if logging fails)
        try:
            from flask import session
            from labman.lib.audit import log_action
            log_action(session.get('user_id'), "updated research comments", f"User ID: {user_id}")
        except Exception as log_error:
            print(f"Warning: Could not log action: {log_error}")
        
        return True
    except Exception as e:
        print(f"Error updating research comments: {e}")
        import traceback
        traceback.print_exc()
        return False
