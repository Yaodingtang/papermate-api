from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db, get_current_user
from app.models import User, Paper
from app.schemas import PaperResponse, PaperListResponse, PaperUpdate

router = APIRouter(prefix="/papers", tags=["论文"])


@router.post("/upload", response_model=PaperResponse)
async def upload_paper(
    file: UploadFile = File(...),
    folder_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
    
    paper = Paper(
        user_id=current_user.id,
        title=file.filename.replace('.pdf', ''),
        pdf_url=f"temp://{file.filename}",
        pdf_size=len(content),
    )
    db.add(paper)
    await db.commit()
    await db.refresh(paper)
    return paper


@router.get("", response_model=PaperListResponse)
async def list_papers(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Paper).where(Paper.user_id == current_user.id)
    
    if status:
        query = query.where(Paper.status == status)
    if search:
        query = query.where(Paper.title.ilike(f"%{search}%"))
    
    count_query = select(func.count(Paper.id)).where(Paper.user_id == current_user.id)
    if status:
        count_query = count_query.where(Paper.status == status)
    if search:
        count_query = count_query.where(Paper.title.ilike(f"%{search}%"))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.order_by(Paper.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    papers = result.scalars().all()
    
    return PaperListResponse(
        items=[PaperResponse.model_validate(p) for p in papers],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.patch("/{paper_id}", response_model=PaperResponse)
async def update_paper(
    paper_id: str,
    update_data: PaperUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    if update_data.status is not None:
        paper.status = update_data.status
    if update_data.tags is not None:
        paper.tags = update_data.tags
    if update_data.reading_progress is not None:
        paper.reading_progress = update_data.reading_progress
    if update_data.last_read_page is not None:
        paper.last_read_page = update_data.last_read_page
    
    await db.commit()
    await db.refresh(paper)
    return paper


@router.delete("/{paper_id}")
async def delete_paper(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    await db.delete(paper)
    await db.commit()
    return {"message": "Paper deleted successfully"}
