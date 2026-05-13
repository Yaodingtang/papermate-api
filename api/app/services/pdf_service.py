"""PDF 解析服务 - 提取 PDF 文本、元数据、目录等"""

import fitz  # PyMuPDF
import pdfplumber
from typing import Optional, List, Dict, Any
from pathlib import Path
import hashlib
import os
from datetime import datetime


class PDFParser:
    """PDF 解析器"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._doc = None
        self._plumber_pdf = None
    
    def open(self) -> bool:
        """打开 PDF 文件"""
        try:
            self._doc = fitz.open(self.file_path)
            self._plumber_pdf = pdfplumber.open(self.file_path)
            return True
        except Exception as e:
            print(f"打开 PDF 失败: {e}")
            return False
    
    def close(self):
        """关闭 PDF 文件"""
        if self._doc:
            self._doc.close()
        if self._plumber_pdf:
            self._plumber_pdf.close()
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def get_metadata(self) -> Dict[str, Any]:
        """提取 PDF 元数据"""
        if not self._doc:
            return {}
        
        metadata = self._doc.metadata
        return {
            "title": metadata.get("title", "") or self.file_path.stem,
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": self._parse_date(metadata.get("creationDate")),
            "modification_date": self._parse_date(metadata.get("modDate")),
            "page_count": len(self._doc),
            "file_size": self.file_path.stat().st_size if self.file_path.exists() else 0,
            "file_hash": self._compute_hash(),
        }
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """解析 PDF 日期格式 (D:YYYYMMDDHHmmSS)"""
        if not date_str:
            return None
        try:
            # 移除 "D:" 前缀
            if date_str.startswith("D:"):
                date_str = date_str[2:]
            # 解析 YYYYMMDD
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            return f"{year}-{month:02d}-{day:02d}"
        except:
            return None
    
    def _compute_hash(self) -> str:
        """计算文件 MD5 哈希"""
        hasher = hashlib.md5()
        with open(self.file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def extract_text(self, start_page: int = 0, end_page: Optional[int] = None) -> str:
        """提取 PDF 文本"""
        if not self._doc:
            return ""
        
        if end_page is None:
            end_page = len(self._doc)
        
        text_parts = []
        for page_num in range(start_page, min(end_page, len(self._doc))):
            page = self._doc[page_num]
            text_parts.append(page.get_text())
        
        return "\n\n".join(text_parts)
    
    def extract_text_by_page(self) -> List[Dict[str, Any]]:
        """按页提取文本"""
        if not self._doc:
            return []
        
        pages = []
        for page_num in range(len(self._doc)):
            page = self._doc[page_num]
            pages.append({
                "page_number": page_num + 1,
                "text": page.get_text(),
                "char_count": len(page.get_text()),
            })
        return pages
    
    def extract_toc(self) -> List[Dict[str, Any]]:
        """提取目录"""
        if not self._doc:
            return []
        
        toc = self._doc.get_toc()
        return [
            {
                "level": item[0],
                "title": item[1],
                "page": item[2],
            }
            for item in toc
        ]
    
    def extract_images(self) -> List[Dict[str, Any]]:
        """提取图片信息"""
        if not self._doc:
            return []
        
        images = []
        for page_num in range(len(self._doc)):
            page = self._doc[page_num]
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = self._doc.extract_image(xref)
                images.append({
                    "page": page_num + 1,
                    "index": img_index,
                    "width": base_image["width"],
                    "height": base_image["height"],
                    "colorspace": base_image.get("colorspace", 0),
                    "xref": xref,
                })
        return images
    
    def extract_tables(self) -> List[Dict[str, Any]]:
        """提取表格（使用 pdfplumber）"""
        if not self._plumber_pdf:
            return []
        
        tables = []
        for page_num, page in enumerate(self._plumber_pdf.pages):
            page_tables = page.extract_tables()
            for table_index, table in enumerate(page_tables):
                if table:
                    tables.append({
                        "page": page_num + 1,
                        "index": table_index,
                        "rows": len(table),
                        "cols": len(table[0]) if table else 0,
                        "data": table,
                    })
        return tables
    
    def extract_abstract(self) -> Optional[str]:
        """尝试提取摘要"""
        text = self.extract_text(end_page=3)  # 通常摘要在前几页
        
        # 常见摘要标记
        abstract_markers = [
            "Abstract",
            "ABSTRACT",
            "摘要",
            "摘  要",
        ]
        
        for marker in abstract_markers:
            if marker in text:
                start = text.find(marker) + len(marker)
                # 查找结束标记
                end_markers = ["Introduction", "INTRODUCTION", "引言", "1.", "Keywords", "关键词"]
                end = len(text)
                for end_marker in end_markers:
                    pos = text.find(end_marker, start)
                    if pos > start:
                        end = min(end, pos)
                
                abstract = text[start:end].strip()
                # 清理多余空白
                abstract = " ".join(abstract.split())
                if len(abstract) > 50:
                    return abstract
        
        return None
    
    def extract_references(self) -> List[str]:
        """尝试提取参考文献"""
        text = self.extract_text()
        
        # 查找参考文献部分
        ref_markers = ["References", "REFERENCES", "参考文献", "Bibliography"]
        
        for marker in ref_markers:
            if marker in text:
                start = text.rfind(marker)  # 使用最后一个匹配
                ref_text = text[start + len(marker):]
                
                # 简单分割（实际需要更复杂的解析）
                lines = ref_text.strip().split("\n")
                refs = []
                current_ref = ""
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    # 检测新引用开始（通常是 [1] 或数字）
                    if line.startswith("[") or (line[0].isdigit() and "." in line[:5]):
                        if current_ref:
                            refs.append(current_ref.strip())
                        current_ref = line
                    else:
                        current_ref += " " + line
                
                if current_ref:
                    refs.append(current_ref.strip())
                
                return refs[:50]  # 限制数量
        
        return []
    
    def get_page_preview(self, page_num: int = 0, zoom: float = 2.0) -> Optional[bytes]:
        """获取页面预览图（PNG 格式）"""
        if not self._doc or page_num >= len(self._doc):
            return None
        
        page = self._doc[page_num]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        return pix.tobytes("png")
    
    def search_text(self, query: str) -> List[Dict[str, Any]]:
        """搜索文本"""
        if not self._doc:
            return []
        
        results = []
        for page_num in range(len(self._doc)):
            page = self._doc[page_num]
            text_instances = page.search_for(query)
            for inst in text_instances:
                results.append({
                    "page": page_num + 1,
                    "rect": list(inst),
                    "context": self._get_context(page, inst),
                })
        return results
    
    def _get_context(self, page, rect, context_chars: int = 100) -> str:
        """获取搜索结果的上下文"""
        text = page.get_text()
        # 简化：返回整页文本的一部分
        start = max(0, int(rect.y0) - context_chars)
        end = min(len(text), int(rect.y1) + context_chars)
        return text[start:end].strip()


def parse_pdf(file_path: str) -> Dict[str, Any]:
    """解析 PDF 文件，返回完整信息"""
    with PDFParser(file_path) as parser:
        return {
            "metadata": parser.get_metadata(),
            "text": parser.extract_text(),
            "pages": parser.extract_text_by_page(),
            "toc": parser.extract_toc(),
            "images": parser.extract_images(),
            "tables": parser.extract_tables(),
            "abstract": parser.extract_abstract(),
            "references": parser.extract_references(),
        }
