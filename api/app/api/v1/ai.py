from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List, Optional
import httpx
import json
import os

from app.models import (
    AIChatRequest, AIChatResponse,
    ReviewCreate, ReviewRead,
    CardCreate, CardRead
)
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# AI API 配置 - 从环境变量读取
AI_API_URL = os.getenv("AI_API_URL", "https://spark-api-open.xf-yun.com/v1/chat/completions")
AI_MODEL = os.getenv("AI_MODEL", "generalv3.5")


def get_ai_api_key() -> str:
    """获取 AI API Key，优先从环境变量，其次从配置"""
    api_key = os.getenv("AI_API_KEY") or settings.AI_API_KEY
    if not api_key:
        raise ValueError("AI_API_KEY 未配置，请设置环境变量或在 .env 文件中配置")
    return api_key


async def call_ai_api(messages: List[dict]) -> str:
    """调用讯飞星火 API"""
    try:
        api_key = get_ai_api_key()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                AI_API_URL,
                json={
                    "model": AI_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                timeout=30.0
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                return "AI 服务暂时不可用，请稍后再试。"
    except Exception as e:
        return f"AI 调用出错: {str(e)}"


@router.post("/chat", response_model=AIChatResponse)
@limiter.limit("30/minute")
async def chat_with_paper(
    request: Request,
    chat_request: AIChatRequest,
    user = Depends(get_current_user)
):
    """与 AI 讨论论文"""
    
    # 构建系统提示
    system_prompt = """你是一个专业的学术论文研究助手。你的任务是帮助用户理解和分析学术论文。
请用清晰、专业的语言回答用户的问题。
如果用户问的是论文的具体内容，请基于论文内容回答。
如果用户问的是论文之外的问题，请礼貌地引导用户回到论文讨论。"""

    # 模拟论文内容（实际应从数据库获取）
    paper_context = f"""
论文标题: Attention Is All You Need
作者: Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin
年份: 2017
发表: NeurIPS 2017

摘要: 我们提出了一种新的简单网络架构——Transformer，完全基于注意力机制，摒弃了循环和卷积。
Transformer 在两个机器翻译任务上的实验表明，这些模型在质量上更优越，同时更具并行性，训练时间显著减少。

主要内容:
1. 自注意力机制 (Self-Attention)
2. 多头注意力 (Multi-Head Attention)
3. 位置编码 (Positional Encoding)
4. 编码器-解码器架构
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"以下是论文内容:\n{paper_context}"},
        {"role": "user", "content": chat_request.question}
    ]

    answer = await call_ai_api(messages)

    return AIChatResponse(
        answer=answer,
        conversation_id=request.conversation_id or 1,
        references=[
            {"page": 1, "text": "相关原文..."}
        ]
    )


@router.post("/review/generate")
async def generate_review(
    request: ReviewCreate,
    user = Depends(get_current_user)
):
    """生成文献综述"""
    
    system_prompt = """你是一个学术写作助手。请根据提供的论文信息，生成结构化的文献综述。
综述应包含以下部分：
1. 研究背景 - 介绍研究领域的背景和重要性
2. 主要方法 - 总结论文中使用的主要方法
3. 发展脉络 - 梳理该领域的发展历程
4. 方法对比 - 对比不同方法的优缺点
5. 未来方向 - 展望未来研究方向

请用学术、专业的语言撰写，并适当引用论文内容。"""

    # 模拟论文信息
    papers_info = """
论文1: Attention Is All You Need (2017)
- 提出Transformer架构
- 引入自注意力机制
- 在机器翻译任务上取得SOTA

论文2: BERT: Pre-training of Deep Bidirectional Transformers (2018)
- 双向预训练
- 掩码语言模型
- 在多项NLP任务上取得突破

论文3: GPT-3: Language Models are Few-Shot Learners (2020)
- 大规模预训练
- 少样本学习能力
- 展现出强大的生成能力
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"研究主题: {request.topic}\n\n参考论文:\n{papers_info}\n\n请生成文献综述。"}
    ]

    content = await call_ai_api(messages)

    return {
        "review_id": 1,
        "status": "completed",
        "sections": [
            {
                "id": "background",
                "title": "研究背景",
                "content": content[:500] if content else "生成中...",
                "status": "completed"
            }
        ]
    }


@router.get("/graph/{paper_id}")
async def get_paper_graph(
    paper_id: int,
    depth: int = 2,
    user = Depends(get_current_user)
):
    """获取论文关系图谱"""
    
    # 模拟图谱数据
    return {
        "nodes": [
            {"id": paper_id, "title": "Attention Is All You Need", "type": "core", "year": 2017, "citations": 89000},
            {"id": paper_id + 1, "title": "BERT", "type": "derived", "year": 2018, "citations": 75000},
            {"id": paper_id + 2, "title": "GPT-3", "type": "derived", "year": 2020, "citations": 45000},
            {"id": paper_id + 3, "title": "Seq2Seq", "type": "precursor", "year": 2014, "citations": 18000},
        ],
        "edges": [
            {"source": paper_id + 3, "target": paper_id, "type": "influenced"},
            {"source": paper_id, "target": paper_id + 1, "type": "cited"},
            {"source": paper_id, "target": paper_id + 2, "type": "cited"},
        ]
    }


@router.post("/writing/polish")
async def polish_text(
    content: str,
    style: str = "academic",
    user = Depends(get_current_user)
):
    """润色文本"""
    
    system_prompt = f"""你是一个学术写作助手。请将用户提供的文本润色为{style}风格。
要求:
1. 保持原意不变
2. 使用更学术、专业的表达
3. 改善句子结构
4. 适当增加过渡词"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]

    polished = await call_ai_api(messages)

    return {
        "original": content,
        "polished": polished,
        "suggestions": [
            {"original": "新的", "suggested": "新型", "reason": "更学术化"}
        ]
    }


@router.post("/writing/citations")
async def suggest_citations(
    content: str,
    top_k: int = 5,
    user = Depends(get_current_user)
):
    """推荐引用"""
    
    # 模拟引用推荐
    return {
        "citations": [
            {
                "id": 1,
                "title": "Attention Is All You Need",
                "authors": "Vaswani et al.",
                "year": 2017,
                "relevance": 95,
                "reason": "核心方法引用"
            },
            {
                "id": 2,
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "authors": "Devlin et al.",
                "year": 2018,
                "relevance": 88,
                "reason": "相关工作"
            },
            {
                "id": 3,
                "title": "GPT-3: Language Models are Few-Shot Learners",
                "authors": "Brown et al.",
                "year": 2020,
                "relevance": 82,
                "reason": "方法对比"
            }
        ]
    }


@router.post("/writing/check")
async def check_paper(
    content: str,
    user = Depends(get_current_user)
):
    """检查论文"""
    
    system_prompt = """你是一个学术论文检查助手。请检查用户提供的论文内容，找出以下问题:
1. 语法错误
2. 表达不当
3. 引用缺失
4. 逻辑问题
5. 格式问题

返回 JSON 格式:
{
    "score": 85,
    "issues": [
        {"type": "grammar", "severity": "error", "line": 3, "text": "问题描述", "suggestion": "修改建议"}
    ]
}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]

    result = await call_ai_api(messages)

    return {
        "score": 85,
        "issues": [
            {"type": "grammar", "severity": "error", "line": 3, "text": "their 应为 there", "suggestion": "there"},
            {"type": "style", "severity": "warning", "line": 5, "text": "very good 改为 significant", "suggestion": "significant"},
            {"type": "citation", "severity": "info", "line": 8, "text": "缺少引用", "suggestion": "引用 Transformer 原论文"},
        ]
    }


# === 智能摘要功能 ===

@router.post("/summary/generate")
@limiter.limit("10/minute")
async def generate_summary(
    request: Request,
    paper_id: str,
    summary_type: str = "brief",  # brief, detailed, bullet
    user = Depends(get_current_user)
):
    """生成论文智能摘要"""
    
    # 根据摘要类型选择不同的提示词
    prompts = {
        "brief": """请为以下论文生成一个简洁的摘要（100-150字），包括：
1. 研究问题
2. 主要方法
3. 核心结论
请用简洁、专业的语言概括。""",
        
        "detailed": """请为以下论文生成一个详细的摘要（300-500字），包括：
1. 研究背景与动机
2. 研究问题
3. 主要方法与创新点
4. 实验设计与结果
5. 结论与贡献
请用学术、专业的语言撰写。""",
        
        "bullet": """请为以下论文生成要点摘要，以列表形式呈现：
- 研究问题：...
- 核心方法：...
- 主要创新：...
- 关键结果：...
- 重要结论：...
请简洁明了地列出要点。"""
    }
    
    system_prompt = prompts.get(summary_type, prompts["brief"])
    
    # 模拟论文内容（实际应从数据库获取）
    paper_content = """
论文标题: Attention Is All You Need
作者: Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin
年份: 2017
发表: NeurIPS 2017

摘要: 我们提出了一种新的简单网络架构——Transformer，完全基于注意力机制，摒弃了循环和卷积。
Transformer 在两个机器翻译任务上的实验表明，这些模型在质量上更优越，同时更具并行性，训练时间显著减少。

主要内容:
1. 自注意力机制 (Self-Attention)
2. 多头注意力 (Multi-Head Attention)
3. 位置编码 (Positional Encoding)
4. 编码器-解码器架构
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请为以下论文生成摘要:\n\n{paper_content}"}
    ]
    
    summary = await call_ai_api(messages)
    
    return {
        "paper_id": paper_id,
        "summary_type": summary_type,
        "summary": summary,
        "generated_at": "2024-01-01T00:00:00Z",
    }


@router.post("/summary/translate")
@limiter.limit("10/minute")
async def translate_summary(
    request: Request,
    text: str,
    target_lang: str = "zh",  # zh, en
    user = Depends(get_current_user)
):
    """翻译摘要"""
    
    lang_prompt = {
        "zh": "请将以下英文摘要翻译成中文，保持学术风格：",
        "en": "Please translate the following Chinese abstract to English, maintaining academic style:"
    }
    
    system_prompt = lang_prompt.get(target_lang, lang_prompt["zh"])
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    
    translated = await call_ai_api(messages)
    
    return {
        "original": text,
        "translated": translated,
        "target_lang": target_lang,
    }


@router.post("/summary/keypoints")
@limiter.limit("10/minute")
async def extract_keypoints(
    request: Request,
    paper_id: str,
    user = Depends(get_current_user)
):
    """提取论文关键点"""
    
    system_prompt = """请从以下论文中提取关键点，包括：
1. 核心概念（3-5个）
2. 关键方法（2-3个）
3. 重要发现（2-3个）
4. 局限性（1-2个）

请以结构化的方式返回。"""
    
    # 模拟论文内容
    paper_content = """
论文标题: Attention Is All You Need
主要内容: Transformer架构，自注意力机制，多头注意力，位置编码
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": paper_content}
    ]
    
    keypoints = await call_ai_api(messages)
    
    return {
        "paper_id": paper_id,
        "keypoints": keypoints,
        "concepts": ["自注意力", "多头注意力", "位置编码", "Transformer"],
        "methods": ["缩放点积注意力", "多头注意力机制"],
        "findings": ["在翻译任务上超越RNN", "训练速度显著提升"],
        "limitations": ["计算复杂度O(n²)", "对位置编码敏感"],
    }


# === 引用追踪功能 ===

@router.get("/citations/{paper_id}")
@limiter.limit("20/minute")
async def get_citation_network(
    request: Request,
    paper_id: str,
    depth: int = 1,
    user = Depends(get_current_user)
):
    """获取论文引用网络"""
    
    # 模拟引用网络数据
    return {
        "paper_id": paper_id,
        "paper_title": "Attention Is All You Need",
        "citation_count": 89000,
        "reference_count": 15,
        "cited_by": [
            {
                "id": "paper_1",
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "authors": "Devlin et al.",
                "year": 2018,
                "citations": 75000,
            },
            {
                "id": "paper_2",
                "title": "GPT-3: Language Models are Few-Shot Learners",
                "authors": "Brown et al.",
                "year": 2020,
                "citations": 45000,
            },
            {
                "id": "paper_3",
                "title": "Vision Transformer",
                "authors": "Dosovitskiy et al.",
                "year": 2020,
                "citations": 35000,
            },
        ],
        "references": [
            {
                "id": "ref_1",
                "title": "Sequence to Sequence Learning with Neural Networks",
                "authors": "Sutskever et al.",
                "year": 2014,
            },
            {
                "id": "ref_2",
                "title": "Neural Machine Translation by Jointly Learning to Align and Translate",
                "authors": "Bahdanau et al.",
                "year": 2014,
            },
        ],
        "network_depth": depth,
    }


@router.get("/citations/trending")
async def get_trending_citations(
    field: str = "AI",
    limit: int = 10,
    user = Depends(get_current_user)
):
    """获取领域内热门被引论文"""
    
    # 模拟热门论文数据
    return {
        "field": field,
        "papers": [
            {
                "id": "trend_1",
                "title": "GPT-4 Technical Report",
                "authors": "OpenAI",
                "year": 2023,
                "citations_growth": "+250%",
                "recent_citations": 5000,
            },
            {
                "id": "trend_2",
                "title": "LLaMA: Open and Efficient Foundation Language Models",
                "authors": "Touvron et al.",
                "year": 2023,
                "citations_growth": "+180%",
                "recent_citations": 3500,
            },
        ],
        "period": "last_30_days",
    }


@router.post("/citations/compare")
@limiter.limit("10/minute")
async def compare_citations(
    request: Request,
    paper_ids: list[str],
    user = Depends(get_current_user)
):
    """比较多篇论文的引用情况"""
    
    # 模拟对比数据
    return {
        "papers": [
            {
                "id": paper_ids[0] if len(paper_ids) > 0 else "paper_1",
                "title": "Attention Is All You Need",
                "total_citations": 89000,
                "year_over_year": "+15%",
            },
            {
                "id": paper_ids[1] if len(paper_ids) > 1 else "paper_2",
                "title": "BERT",
                "total_citations": 75000,
                "year_over_year": "+10%",
            },
        ],
        "comparison": {
            "common_citations": 1200,
            "unique_to_first": 15000,
            "unique_to_second": 12000,
        },
    }