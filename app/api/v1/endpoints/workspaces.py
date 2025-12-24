"""
Workspace Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_active_user, get_admin_user, get_fm_user
from app.models.auth import User
from app.schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse, WorkspaceListResponse,
    WorkspaceMemberResponse, WorkspaceStatsResponse
)
from app.crud.workspace import workspace_crud

router = APIRouter()


@router.get("/", response_model=WorkspaceListResponse)
async def list_workspaces(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    workspace_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List workspaces for current user"""
    workspaces, total = await workspace_crud.get_user_workspaces(
        db, current_user.id, skip, limit, search, workspace_type
    )
    
    return WorkspaceListResponse(
        workspaces=[WorkspaceResponse.from_orm(ws) for ws in workspaces],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new workspace"""
    workspace = await workspace_crud.create_workspace(db, workspace_data, current_user.id)
    return WorkspaceResponse.from_orm(workspace)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workspace by ID"""
    workspace = await workspace_crud.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check if user has access to workspace
    has_access = await workspace_crud.user_has_workspace_access(db, current_user.id, workspace.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this workspace"
        )
    
    return WorkspaceResponse.from_orm(workspace)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: UUID,
    workspace_data: WorkspaceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update workspace"""
    workspace = await workspace_crud.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check if user is owner or admin
    is_owner_or_admin = await workspace_crud.user_is_workspace_owner_or_admin(
        db, current_user.id, workspace.id
    )
    if not is_owner_or_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workspace owners or admins can update workspace"
        )
    
    updated_workspace = await workspace_crud.update_workspace(db, workspace.id, workspace_data)
    return WorkspaceResponse.from_orm(updated_workspace)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete workspace (soft delete)"""
    workspace = await workspace_crud.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Only owner can delete workspace
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workspace owner can delete workspace"
        )
    
    await workspace_crud.delete_workspace(db, workspace.id)


@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberResponse])
async def list_workspace_members(
    workspace_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List workspace members"""
    workspace = await workspace_crud.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check access
    has_access = await workspace_crud.user_has_workspace_access(db, current_user.id, workspace.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this workspace"
        )
    
    members = await workspace_crud.get_workspace_members(db, workspace.id)
    return [WorkspaceMemberResponse.from_orm(member) for member in members]


@router.get("/{workspace_id}/stats", response_model=WorkspaceStatsResponse)
async def get_workspace_stats(
    workspace_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workspace statistics"""
    workspace = await workspace_crud.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check access
    has_access = await workspace_crud.user_has_workspace_access(db, current_user.id, workspace.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this workspace"
        )
    
    stats = await workspace_crud.get_workspace_stats(db, workspace.id)
    return WorkspaceStatsResponse(**stats)