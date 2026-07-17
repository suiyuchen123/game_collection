import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database.db import DatabaseManager
from core.knowledge_base import KnowledgeBase

app = FastAPI(title="游戏AI助手管理后台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseManager()
kb = KnowledgeBase()


class KnowledgeItem(BaseModel):
    game: str
    keywords: list
    answer: str


class FeedbackItem(BaseModel):
    message: str
    rating: int = None


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/knowledge")
async def get_knowledge(game: str = None):
    try:
        items = db.get_knowledge(game)
        return {"success": True, "data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge")
async def add_knowledge(item: KnowledgeItem):
    try:
        db.insert_knowledge(item.game, item.keywords, item.answer)
        kb.add_knowledge(item.game, item.keywords, item.answer)
        return {"success": True, "message": "添加成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/knowledge/{kb_id}")
async def update_knowledge(kb_id: int, item: KnowledgeItem):
    try:
        db.update_knowledge(kb_id, item.game, item.keywords, item.answer)
        return {"success": True, "message": "更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/knowledge/{kb_id}")
async def delete_knowledge(kb_id: int):
    try:
        db.delete_knowledge(kb_id)
        return {"success": True, "message": "删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat_logs")
async def get_chat_logs(user_id: str = None, limit: int = 50, offset: int = 0):
    try:
        logs = db.get_chat_logs(user_id, limit, offset)
        return {"success": True, "data": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/feedback")
async def get_feedback(limit: int = 50, offset: int = 0):
    try:
        feedbacks = db.get_feedback(limit, offset)
        return {"success": True, "data": feedbacks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback")
async def add_feedback(item: FeedbackItem, user_id: str = "default", username: str = "匿名"):
    try:
        db.insert_feedback(user_id, username, item.message, item.rating)
        return {"success": True, "message": "反馈提交成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    try:
        daily_stats = db.get_stats_by_date()
        top_queries = db.get_top_queries(10)
        source_dist = db.get_source_distribution()

        stats = {
            "daily_stats": daily_stats,
            "top_queries": top_queries,
            "source_distribution": source_dist
        }
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/game_categories")
async def get_game_categories():
    return {"success": True, "data": kb.game_categories}


@app.get("/api/search_knowledge")
async def search_knowledge(query: str):
    try:
        answer, category, score = kb.search(query)
        return {
            "success": True,
            "data": {
                "answer": answer,
                "category": category,
                "score": score
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export_knowledge")
async def export_knowledge():
    try:
        items = db.get_knowledge()
        default_kb = kb.knowledge
        return {
            "success": True,
            "database_knowledge": items,
            "default_knowledge": default_kb
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {
        "message": "游戏AI助手管理后台",
        "endpoints": [
            "GET /api/health - 健康检查",
            "GET /api/knowledge - 获取知识库",
            "POST /api/knowledge - 添加知识",
            "PUT /api/knowledge/{id} - 更新知识",
            "DELETE /api/knowledge/{id} - 删除知识",
            "GET /api/chat_logs - 获取对话日志",
            "GET /api/feedback - 获取反馈",
            "POST /api/feedback - 提交反馈",
            "GET /api/stats - 获取统计数据",
            "GET /api/game_categories - 获取游戏分类",
            "GET /api/search_knowledge?query=xxx - 搜索知识库",
            "GET /api/export_knowledge - 导出知识库"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)