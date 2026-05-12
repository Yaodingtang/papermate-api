from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import httpx
import json

from app.models import (
    AIChatRequest, AIChatResponse,
    ReviewCreate, ReviewRead,
    CardCreate, CardRead
)
from app.api.deps import get_current_user

router = APIRouter()

# AI API 配置
AI_API_URL = "https://spark-api-open.xf-yun.com/v1/chat/completions"
AI_MODEL = "generalv3.5"


async def call_ai_api(messages: List[dict]) -> str:
    """调用讯飞星火 API"""
    try:
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
                    "Content-Type": "application/json"
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
async def chat_with_paper(
    request: AIChatRequest,
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
        {"role": "user", "content": request.question}
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