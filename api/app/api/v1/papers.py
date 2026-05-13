from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional, Dict, Any
from fastapi import UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import magic
import os
import tempfile
import logging

from app.api.deps import get_db, get_current_user
from app.models import User, Paper
from app.schemas import PaperResponse, PaperListResponse, PaperUpdate
from app.services import PDFParser, parse_pdf, get_paper_metadata, search_papers

router = APIRouter(prefix="/papers", tags=["论文"])
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

# 允许的 MIME 类型
ALLOWED_MIME_TYPES = {
    "application/pdf",
}

# PDF 文件头签名
PDF_SIGNATURE = b"%PDF-"


async def validate_file_security(file: UploadFile, content: bytes) -> None:
    """验证文件安全性"""
    # 1. 检查文件扩展名
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只允许上传 PDF 文件")
    
    # 2. 检查文件大小
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小超过 50MB 限制")
    
    if len(content) < 5:
        raise HTTPException(status_code=400, detail="文件内容无效")
    
    # 3. 检查文件头签名（防止伪造扩展名）
    if not content.startswith(PDF_SIGNATURE):
        raise HTTPException(status_code=400, detail="文件不是有效的 PDF 格式")
    
    # 4. 使用 magic 检查真实 MIME 类型
    try:
        mime_type = magic.from_buffer(content, mime=True)
        if mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型: {mime_type}"
            )
    except Exception:
        # magic 不可用时跳过 MIME 检查，但保留签名检查
        pass
    
    # 5. 检查文件名安全性（防止路径遍历攻击）
    filename = os.path.basename(file.filename)
    if filename != file.filename or ".." in file.filename:
        raise HTTPException(status_code=400, detail="文件名包含非法字符")


@router.post("/upload", response_model=PaperResponse)
@limiter.limit("10/minute")
async def upload_paper(
    request: Request,
    file: UploadFile = File(...),
    folder_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 读取文件内容
    content = await file.read()
    
    # 安全验证
    await validate_file_security(file, content)
    
    # 生成安全的存储路径
    safe_filename = os.path.basename(file.filename)
    
    paper = Paper(
        user_id=current_user.id,
        title=safe_filename.replace('.pdf', ''),
        pdf_url=f"temp://{safe_filename}",
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


# === PDF 解析相关 API ===

@router.post("/{paper_id}/parse")
@limiter.limit("5/minute")
async def parse_paper_pdf(
    request: Request,
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """解析论文 PDF，提取文本、元数据、目录等"""
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # 检查 PDF 文件是否存在
    pdf_path = paper.pdf_url
    if pdf_path.startswith("temp://"):
        raise HTTPException(status_code=400, detail="PDF 文件尚未存储，请先上传")
    
    try:
        parsed_data = parse_pdf(pdf_path)
        return {
            "paper_id": paper_id,
            "metadata": parsed_data.get("metadata", {}),
            "abstract": parsed_data.get("abstract"),
            "toc": parsed_data.get("toc", []),
            "page_count": len(parsed_data.get("pages", [])),
            "images_count": len(parsed_data.get("images", [])),
            "tables_count": len(parsed_data.get("tables", [])),
            "references_count": len(parsed_data.get("references", [])),
        }
    except Exception as e:
        logger.error(f"PDF parsing failed for paper {paper_id}: {e}")
        raise HTTPException(status_code=500, detail="PDF 解析失败，请检查文件格式")


@router.get("/{paper_id}/text")
async def get_paper_text(
    paper_id: str,
    start_page: int = Query(0, ge=0),
    end_page: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取论文文本内容"""
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    pdf_path = paper.pdf_url
    if pdf_path.startswith("temp://"):
        raise HTTPException(status_code=400, detail="PDF 文件尚未存储")
    
    try:
        with PDFParser(pdf_path) as parser:
            text = parser.extract_text(start_page, end_page)
            return {
                "paper_id": paper_id,
                "text": text,
                "start_page": start_page,
                "end_page": end_page or parser._doc and len(parser._doc),
            }
    except Exception as e:
        logger.error(f"Text extraction failed for paper {paper_id}: {e}")
        raise HTTPException(status_code=500, detail="文本提取失败，请检查文件格式")


@router.get("/{paper_id}/pages/{page_num}")
async def get_paper_page(
    paper_id: str,
    page_num: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取单页内容"""
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    pdf_path = paper.pdf_url
    if pdf_path.startswith("temp://"):
        raise HTTPException(status_code=400, detail="PDF 文件尚未存储")
    
    try:
        with PDFParser(pdf_path) as parser:
            if not parser._doc or page_num >= len(parser._doc):
                raise HTTPException(status_code=400, detail="页码超出范围")
            page = parser.extract_text_by_page()[page_num]
            return {
                "paper_id": paper_id,
                "page_number": page_num + 1,
                "text": page.get("text", ""),
                "char_count": page.get("char_count", 0),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"页面提取失败: {str(e)}")


@router.get("/{paper_id}/preview")
async def get_paper_preview(
    paper_id: str,
    page_num: int = Query(0, ge=0),
    zoom: float = Query(2.0, ge=0.5, le=4.0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取页面预览图"""
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    pdf_path = paper.pdf_url
    if pdf_path.startswith("temp://"):
        raise HTTPException(status_code=400, detail="PDF 文件尚未存储")
    
    try:
        with PDFParser(pdf_path) as parser:
            preview_bytes = parser.get_page_preview(page_num, zoom)
            if not preview_bytes:
                raise HTTPException(status_code=400, detail="无法生成预览")
            # 返回 PNG 图片
            from fastapi.responses import Response
            return Response(content=preview_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览生成失败: {str(e)}")


@router.get("/{paper_id}/search")
async def search_in_paper(
    paper_id: str,
    query: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """在论文中搜索文本"""
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    pdf_path = paper.pdf_url
    if pdf_path.startswith("temp://"):
        raise HTTPException(status_code=400, detail="PDF 文件尚未存储")
    
    try:
        with PDFParser(pdf_path) as parser:
            results = parser.search_text(query)
            return {
                "paper_id": paper_id,
                "query": query,
                "results": results,
                "total_matches": len(results),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


# === 元数据相关 API ===

@router.post("/metadata/doi")
@limiter.limit("20/minute")
async def get_metadata_by_doi(
    request: Request,
    doi: str = Query(..., description="论文 DOI"),
    current_user: User = Depends(get_current_user),
):
    """通过 DOI 获取论文元数据"""
    try:
        metadata = await get_paper_metadata(doi)
        if not metadata:
            raise HTTPException(status_code=404, detail="未找到该 DOI 的论文信息")
        return {
            "doi": doi,
            "metadata": metadata,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"元数据获取失败: {str(e)}")


@router.post("/metadata/search")
@limiter.limit("20/minute")
async def search_metadata(
    request: Request,
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    """搜索论文元数据"""
    try:
        results = await search_papers(query, limit)
        return {
            "query": query,
            "results": results,
            "total": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/{paper_id}/enrich")
@limiter.limit("10/minute")
async def enrich_paper_metadata(
    request: Request,
    paper_id: str,
    doi: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """丰富论文元数据（通过 DOI 或自动提取）"""
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # 如果没有提供 DOI，尝试从 PDF 提取
    if not doi and not paper.pdf_url.startswith("temp://"):
        try:
            with PDFParser(paper.pdf_url) as parser:
                text = parser.extract_text(end_page=3)
                # 尝试从文本提取 DOI
                from app.services.metadata_service import MetadataService
                service = MetadataService()
                doi = await service.extract_doi_from_text(text)
        except:
            pass
    
    if not doi:
        raise HTTPException(status_code=400, detail="无法提取 DOI，请手动提供")
    
    try:
        metadata = await get_paper_metadata(doi)
        if metadata:
            # 更新论文信息
            if metadata.get("title"):
                paper.title = metadata.get("title")
            if metadata.get("authors"):
                paper.authors = metadata.get("authors")
            if metadata.get("year"):
                paper.year = metadata.get("year")
            if metadata.get("journal"):
                paper.journal = metadata.get("journal")
            paper.doi = doi
            
            await db.commit()
            await db.refresh(paper)
            
            return {
                "paper_id": paper_id,
                "doi": doi,
                "metadata": metadata,
                "updated": True,
            }
        else:
            raise HTTPException(status_code=404, detail="未找到 DOI 对应的元数据")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"元数据丰富失败: {str(e)}")
