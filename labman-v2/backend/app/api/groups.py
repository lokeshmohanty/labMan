from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models import ResearchGroup, UserGroup, User, GroupProject, GroupTask
from app.schemas.group import (
    GroupCreate, GroupUpdate, GroupResponse, GroupTreeNode,
    UserGroupCreate, UserGroupResponse
)
from app.schemas.group_project import (
    GroupProjectUpdate, GroupProjectResponse,
    GroupTaskCreate, GroupTaskUpdate, GroupTaskResponse
)
from app.services.audit import log_action

router = APIRouter()

@router.get("/", response_model=List[GroupResponse])
async def list_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """List all research groups"""
    groups = db.query(ResearchGroup).offset(skip).limit(limit).all()
    
    # Add has_project flag to each group
    result = []
    for group in groups:
        project_exists = db.query(GroupProject).filter(GroupProject.group_id == group.id).first() is not None
        group_dict = {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "parent_id": group.parent_id,
            "lead_id": group.lead_id,
            "created_at": group.created_at,
            "has_project": project_exists
        }
        result.append(GroupResponse(**group_dict))
    
    return result

@router.get("/tree", response_model=List[GroupTreeNode])
async def get_group_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get hierarchical group tree"""
    from app.schemas.group import GroupTreeMember
    
    def build_tree(parent_id=None):
        groups = db.query(ResearchGroup).filter(ResearchGroup.parent_id == parent_id).all()
        tree = []
        for group in groups:
            # Get member count
            member_count = db.query(UserGroup).filter(UserGroup.group_id == group.id).count()
            lead_name = group.lead.name if group.lead else None
            
            # Get members with user info
            memberships = db.query(UserGroup).filter(UserGroup.group_id == group.id).all()
            members = []
            for membership in memberships:
                user = db.query(User).filter(User.id == membership.user_id).first()
                if user:
                    members.append(GroupTreeMember(
                        user_id=user.id,
                        user_name=user.name,
                        user_email=user.email
                    ))
            
            node = GroupTreeNode(
                id=group.id,
                name=group.name,
                description=group.description,
                lead_id=group.lead_id,
                lead_name=lead_name,
                member_count=member_count,
                members=members,
                children=build_tree(group.id)
            )
            tree.append(node)
        return tree
    
    return build_tree()

@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new research group"""
    # Check if name already exists
    existing = db.query(ResearchGroup).filter(ResearchGroup.name == group_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group name already exists"
        )
    
    # Create group
    db_group = ResearchGroup(
        name=group_data.name,
        description=group_data.description,
        parent_id=group_data.parent_id,
        lead_id=group_data.lead_id
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    log_action(db, action="created group", user_id=current_user.id, details=f"Created group '{db_group.name}'")

    return db_group

@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get group by ID"""
    group = db.query(ResearchGroup).filter(ResearchGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update group"""
    group = db.query(ResearchGroup).filter(ResearchGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Update fields
    if group_data.name is not None:
        # Check if new name already exists
        existing = db.query(ResearchGroup).filter(
            ResearchGroup.name == group_data.name,
            ResearchGroup.id != group_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group name already exists"
            )
        group.name = group_data.name
    
    if group_data.description is not None:
        group.description = group_data.description
    if group_data.parent_id is not None:
        group.parent_id = group_data.parent_id
    if group_data.lead_id is not None:
        group.lead_id = group_data.lead_id
    
    db.commit()
    db.refresh(group)
    
    log_action(db, action="updated group", user_id=current_user.id, details=f"Updated group '{group.name}'")

    return group

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete group"""
    group = db.query(ResearchGroup).filter(ResearchGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    name = group.name
    db.delete(group)
    db.commit()
    
    log_action(db, action="deleted group", user_id=current_user.id, details=f"Deleted group '{name}'")
    
    return None

# Group Membership Endpoints

@router.get("/{group_id}/members", response_model=List[UserGroupResponse])
async def get_group_members(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all members of a group"""
    members = db.query(UserGroup).filter(UserGroup.group_id == group_id).all()
    
    # Enrich with user information
    result = []
    for member in members:
        user = db.query(User).filter(User.id == member.user_id).first()
        result.append(UserGroupResponse(
            id=member.id,
            user_id=member.user_id,
            group_id=member.group_id,
            joined_at=member.joined_at,
            user_name=user.name if user else None,
            user_email=user.email if user else None
        ))
    
    return result

@router.post("/{group_id}/members", response_model=UserGroupResponse, status_code=status.HTTP_201_CREATED)
async def add_group_member(
    group_id: int,
    member_data: UserGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a member to a group"""
    # Check if group exists
    group = db.query(ResearchGroup).filter(ResearchGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user exists
    user = db.query(User).filter(User.id == member_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing = db.query(UserGroup).filter(
        UserGroup.user_id == member_data.user_id,
        UserGroup.group_id == group_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this group"
        )
    
    # Add member
    membership = UserGroup(
        user_id=member_data.user_id,
        group_id=group_id
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    
    log_action(db, action="added member", user_id=current_user.id, details=f"Added {user.name} to group '{group.name}'")

    return membership

@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_group_member(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a member from a group"""
    membership = db.query(UserGroup).filter(
        UserGroup.user_id == user_id,
        UserGroup.group_id == group_id
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    # Get names for log
    group = db.query(ResearchGroup).filter(ResearchGroup.id == group_id).first()
    user = db.query(User).filter(User.id == user_id).first()

    db.delete(membership)
    db.commit()
    
    if group and user:
         log_action(db, action="removed member", user_id=current_user.id, details=f"Removed {user.name} from group '{group.name}'")

    return None

# Group Project Page Endpoints

@router.get("/{group_id}/project", response_model=GroupProjectResponse)
async def get_group_project(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get group project page"""
    project = db.query(GroupProject).filter(GroupProject.group_id == group_id).first()
    if not project:
        # Create empty project if doesn't exist
        project = GroupProject(group_id=group_id)
        db.add(project)
        db.commit()
        db.refresh(project)
    return project

@router.put("/{group_id}/project", response_model=GroupProjectResponse)
async def update_group_project(
    group_id: int,
    project_data: GroupProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update group project page (editable by all group members)"""
    # Check if user is a member of the group
    membership = db.query(UserGroup).filter(
        UserGroup.user_id == current_user.id,
        UserGroup.group_id == group_id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member of this group to edit its project page"
        )
    
    # Get or create project
    project = db.query(GroupProject).filter(GroupProject.group_id == group_id).first()
    if not project:
        project = GroupProject(group_id=group_id)
        db.add(project)
    
    # Update fields
    if project_data.problem_statement is not None:
        project.problem_statement = project_data.problem_statement
    if project_data.research_progress is not None:
        project.research_progress = project_data.research_progress
    if project_data.github_link is not None:
        project.github_link = project_data.github_link
    if project_data.manuscript_link is not None:
        project.manuscript_link = project_data.manuscript_link
    if project_data.start_date is not None:
        project.start_date = project_data.start_date
    if project_data.end_date is not None:
        project.end_date = project_data.end_date
    if project_data.comments is not None:
        project.comments = project_data.comments
    
    db.commit()
    db.refresh(project)
    
    log_action(db, action="updated project", user_id=current_user.id, details=f"Updated project page for group {group_id}")

    return project

# Group Project Tasks Endpoints

@router.post("/{group_id}/project/tasks", response_model=GroupTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_group_task(
    group_id: int,
    task_data: GroupTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a task for group project"""
    # Check membership
    membership = db.query(UserGroup).filter(
        UserGroup.user_id == current_user.id,
        UserGroup.group_id == group_id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member of this group"
        )
    
    # Ensure project exists
    project = db.query(GroupProject).filter(GroupProject.group_id == group_id).first()
    if not project:
        project = GroupProject(group_id=group_id)
        db.add(project)
        db.commit()
    
    # Create task
    task = GroupTask(
        project_id=group_id,
        title=task_data.title,
        description=task_data.description,
        start_date=task_data.start_date,
        end_date=task_data.end_date,
        status=task_data.status
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    log_action(db, action="created task", user_id=current_user.id, details=f"Created task '{task.title}' in group {group_id}")

    return task

@router.put("/{group_id}/project/tasks/{task_id}", response_model=GroupTaskResponse)
async def update_group_task(
    group_id: int,
    task_id: int,
    task_data: GroupTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a group task"""
    # Check membership
    membership = db.query(UserGroup).filter(
        UserGroup.user_id == current_user.id,
        UserGroup.group_id == group_id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member of this group"
        )
    
    task = db.query(GroupTask).filter(
        GroupTask.id == task_id,
        GroupTask.project_id == group_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
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
    
    log_action(db, action="updated task", user_id=current_user.id, details=f"Updated task '{task.title}' status to {task.status}")

    return task

@router.delete("/{group_id}/project/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_task(
    group_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a group task"""
    # Check membership
    membership = db.query(UserGroup).filter(
        UserGroup.user_id == current_user.id,
        UserGroup.group_id == group_id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member of this group"
        )
    
    task = db.query(GroupTask).filter(
        GroupTask.id == task_id,
        GroupTask.project_id == group_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    title = task.title
    db.delete(task)
    db.commit()
    
    log_action(db, action="deleted task", user_id=current_user.id, details=f"Deleted task '{title}' from group {group_id}")

    return None
