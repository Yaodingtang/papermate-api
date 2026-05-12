from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models import User, Paper, Annotation
from app.schemas import AnnotationCreate, AnnotationResponse, AnnotationUpdate

router = APIRouter(prefix="/annotations", tags=["批注"])


@router.post("", response_model=AnnotationResponse, status_code=201)
async def create_annotation(
    annotation_data: AnnotationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建批注"""
    # 验证论文存在且属于用户
    result = await db.execute(
        select(Paper).where(Paper.id == annotation_data.paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    annotation = Annotation(
        paper_id=annotation_data.paper_id,
        user_id=current_user.id,
        type=annotation_data.type,
        page=annotation_data.page,
        position=annotation_data.position.model_dump(),
        content=annotation_data.content,
        color=annotation_data.color,
    )
    db.add(annotation)
    await db.commit()
    await db.refresh(annotation)
    
    return annotation


@router.get("", response_model=list[AnnotationResponse])
async def list_annotations(
    paper_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取论文的批注列表"""
    # 验证论文存在且属于用户
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    result = await db.execute(
        select(Annotation).where(Annotation.paper_id == paper_id).order_by(Annotation.page)
    )
    annotations = result.scalars().all()
    
    return annotations


@router.patch("/{annotation_id}", response_model=AnnotationResponse)
async def update_annotation(
    annotation_id: str,
    update_data: AnnotationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新批注"""
    result = await db.execute(
        select(Annotation).where(Annotation.id == annotation_id, Annotation.user_id == current_user.id)
    )
    annotation = result.scalar_one_or_none()
    
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    if update_data.content is not None:
        annotation.content = update_data.content
    if update_data.color is not None:
        annotation.color = update_data.color
    
    await db.commit()
    await db.refresh(annotation)
    
    return annotation


@router.delete("/{annotation_id}")
async def delete_annotation(
    annotation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除批注"""
    result = await db.execute(
        select(Annotation).where(Annotation.id == annotation_id, Annotation.user_id == current_user.id)
    )
    annotation = result.scalar_one_or_none()
    
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    await db.delete(annotation)
    await db.commit()
    
    return {"message": "Annotation deleted successfully"}