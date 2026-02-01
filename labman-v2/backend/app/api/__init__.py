from fastapi import APIRouter
from app.api import auth, users, groups, meetings, content, inventory, servers, research, audit

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(servers.router, prefix="/servers", tags=["servers"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
