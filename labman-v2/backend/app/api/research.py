from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models import ResearchPlan, ResearchTask, User
from app.schemas.research import (
    ResearchPlanUpdate, ResearchPlanResponse, ResearchPlanWithTasks,
    ResearchTaskCreate, ResearchTaskUpdate, ResearchTaskResponse
)

router = APIRouter()

@router.get("/me", response_model=ResearchPlanWithTasks)
async def get_my_research_plan(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's research plan"""
    # Prevent caching to ensure fresh data
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    plan = db.query(ResearchPlan).filter(ResearchPlan.user_id == current_user.id).first()
    if not plan:
        # Create empty plan
        plan = ResearchPlan(user_id=current_user.id)
        db.add(plan)
        db.commit()
        db.refresh(plan)
    return plan

@router.get("/{user_id}", response_model=ResearchPlanWithTasks)
async def get_user_research_plan(
    user_id: int,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a user's research plan"""
    # Prevent caching to ensure fresh data
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    plan = db.query(ResearchPlan).filter(ResearchPlan.user_id == user_id).first()
    if not plan:
        # Create empty plan
        plan = ResearchPlan(user_id=user_id)
        db.add(plan)
        db.commit()
        db.refresh(plan)
    return plan

@router.put("/me", response_model=ResearchPlanResponse)
async def update_my_research_plan(
    plan_data: ResearchPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's research plan"""
    plan = db.query(ResearchPlan).filter(ResearchPlan.user_id == current_user.id).first()
    if not plan:
        plan = ResearchPlan(user_id=current_user.id)
        db.add(plan)
    
    # Update fields
    if plan_data.problem_statement is not None:
        plan.problem_statement = plan_data.problem_statement
    if plan_data.research_progress is not None:
        plan.research_progress = plan_data.research_progress
    if plan_data.github_link is not None:
        plan.github_link = plan_data.github_link
    if plan_data.manuscript_link is not None:
        plan.manuscript_link = plan_data.manuscript_link
    if plan_data.start_date is not None:
        plan.start_date = plan_data.start_date
    if plan_data.end_date is not None:
        plan.end_date = plan_data.end_date
    if plan_data.comments is not None:
        plan.comments = plan_data.comments
    
    db.commit()
    db.refresh(plan)
    return plan

# Research Tasks

@router.post("/me/tasks", response_model=ResearchTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_research_task(
    task_data: ResearchTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a research task"""
    # Ensure plan exists
    plan = db.query(ResearchPlan).filter(ResearchPlan.user_id == current_user.id).first()
    if not plan:
        plan = ResearchPlan(user_id=current_user.id)
        db.add(plan)
        db.commit()
    
    task = ResearchTask(
        plan_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        start_date=task_data.start_date,
        end_date=task_data.end_date,
        status=task_data.status or "pending"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.put("/tasks/{task_id}", response_model=ResearchTaskResponse)
async def update_research_task(
    task_id: int,
    task_data: ResearchTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a research task"""
    task = db.query(ResearchTask).filter(ResearchTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Only task owner or admin can update
    if task.plan_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks"
        )
    
    # Update fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.start_date is not None:
        task.start_date = task_data.start_date
    if task_data.end_date is not None:
        task.end_date = task_data.end_date
    if task_data.status is not None:
        task.status = task_data.status
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a research task"""
    task = db.query(ResearchTask).filter(ResearchTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Only task owner or admin can delete
    if task.plan_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tasks"
        )
    
    db.delete(task)
    db.commit()
    return None

# Admin comment update
from pydantic import BaseModel

class CommentUpdate(BaseModel):
    comments: str

@router.put("/{user_id}/comments", response_model=ResearchPlanResponse)
async def update_user_research_comments(
    user_id: int,
    data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update research plan comments (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update comments"
        )
    
    plan = db.query(ResearchPlan).filter(ResearchPlan.user_id == user_id).first()
    if not plan:
        plan = ResearchPlan(user_id=user_id)
        db.add(plan)
    
    plan.comments = data.comments
    db.commit()
    db.refresh(plan)
    return plan
