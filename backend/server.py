import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from database.db import DatabaseManager
from core.coze_client import CozeClient
from core.knowledge_base import KnowledgeBase
from core.context_manager import ContextManager
from datetime import datetime

app = FastAPI(title="游戏AI助手后端服务", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseManager()
coze_client = CozeClient()
coze_client.load_config()
kb = KnowledgeBase()


class ChatRequest(BaseModel):
    user_id: str = "default"
    username: str = "玩家"
    query: str
    game_category: str = None


class ChatResponse(BaseModel):
    success: bool
    answer: str = ""
    source: str = ""
    game_category: str = None
    error: str = ""


class ConfigRequest(BaseModel):
    api_key: str
    bot_id: str


@app.get("/api/health")
async def health():
    return {"status": "ok", "coze_connected": bool(coze_client.api_key and coze_client.bot_id)}


@app.get("/api/config")
async def get_config():
    return {
        "api_key_set": bool(coze_client.api_key),
        "bot_id_set": bool(coze_client.bot_id),
        "api_key_masked": coze_client.api_key[:4] + "****" if coze_client.api_key else None
    }


@app.post("/api/config")
async def set_config(config: ConfigRequest):
    try:
        coze_client.set_config(config.api_key, config.bot_id)
        
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "coze_config.json")
        import json
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump({
                "api_key": config.api_key,
                "bot_id": config.bot_id
            }, f, indent=2, ensure_ascii=False)

        return {"success": True, "message": "Coze配置已更新"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        detected_game = request.game_category
        if not detected_game:
            ctx = ContextManager()
            detected_game = ctx.extract_keywords(request.query)

        kb_answer, kb_category, kb_score = kb.search(request.query, detected_game)

        if kb_answer and kb_score >= 3:
            db.insert_chat_log(
                user_id=request.user_id,
                username=request.username,
                query=request.query,
                response=kb_answer,
                source="local",
                game_category=kb_category,
                score=kb_score
            )
            today = datetime.now().strftime("%Y-%m-%d")
            db.update_daily_stats(today, source="local")

            return ChatResponse(
                success=True,
                answer=kb_answer,
                source="local",
                game_category=kb_category
            )

        if coze_client.api_key and coze_client.bot_id:
            ctx_manager = ContextManager()
            ctx_manager.set_current_game(detected_game)
            
            recent_logs = db.get_chat_logs(request.user_id, limit=5)
            for log in reversed(recent_logs):
                ctx_manager.add_message("user", log["query"])
                ctx_manager.add_message("assistant", log["response"])

            history = ctx_manager.get_context_prompt()
            full_query = f"{history}\n\n用户问题：{request.query}" if history else request.query

            result = coze_client.chat(full_query)
            if result.get("answer"):
                db.insert_chat_log(
                    user_id=request.user_id,
                    username=request.username,
                    query=request.query,
                    response=result["answer"],
                    source="coze",
                    game_category=detected_game
                )
                today = datetime.now().strftime("%Y-%m-%d")
                db.update_daily_stats(today, source="coze")

                return ChatResponse(
                    success=True,
                    answer=result["answer"],
                    source="coze",
                    game_category=detected_game
                )
            elif result.get("error"):
                print(f"Coze API error: {result['error']}")

        if kb_answer:
            db.insert_chat_log(
                user_id=request.user_id,
                username=request.username,
                query=request.query,
                response=kb_answer,
                source="local",
                game_category=kb_category,
                score=kb_score
            )
            today = datetime.now().strftime("%Y-%m-%d")
            db.update_daily_stats(today, source="local")

            return ChatResponse(
                success=True,
                answer=kb_answer,
                source="local",
                game_category=kb_category
            )

        fallback = "抱歉，我不太理解你的问题。你可以问我：\n• 关卡怎么解锁\n• 通关条件是什么\n• 操作按键怎么按\n• 存档丢失怎么办\n• 称号怎么获得"
        
        db.insert_chat_log(
            user_id=request.user_id,
            username=request.username,
            query=request.query,
            response=fallback,
            source="fallback",
            game_category=None
        )
        today = datetime.now().strftime("%Y-%m-%d")
        db.update_daily_stats(today, source="fallback", success=False)

        return ChatResponse(
            success=True,
            answer=fallback,
            source="fallback"
        )

    except Exception as e:
        print(f"Chat error: {e}")
        return ChatResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        detected_game = request.game_category
        if not detected_game:
            ctx = ContextManager()
            detected_game = ctx.extract_keywords(request.query)

        kb_answer, kb_category, kb_score = kb.search(request.query, detected_game)

        if kb_answer and kb_score >= 3:
            def generate():
                yield f"data: {kb_answer}\n\n"
            return StreamingResponse(generate(), media_type="text/event-stream")

        if coze_client.api_key and coze_client.bot_id:
            ctx_manager = ContextManager()
            ctx_manager.set_current_game(detected_game)

            recent_logs = db.get_chat_logs(request.user_id, limit=5)
            for log in reversed(recent_logs):
                ctx_manager.add_message("user", log["query"])
                ctx_manager.add_message("assistant", log["response"])

            history = ctx_manager.get_context_prompt()
            full_query = f"{history}\n\n用户问题：{request.query}" if history else request.query

            def generate():
                full_answer = ""
                for chunk in coze_client.chat_stream(full_query):
                    full_answer += chunk
                    yield f"data: {chunk}\n\n"

                if full_answer:
                    db.insert_chat_log(
                        user_id=request.user_id,
                        username=request.username,
                        query=request.query,
                        response=full_answer,
                        source="coze",
                        game_category=detected_game
                    )
                    today = datetime.now().strftime("%Y-%m-%d")
                    db.update_daily_stats(today, source="coze")

                yield "data: [DONE]\n\n"

            return StreamingResponse(generate(), media_type="text/event-stream")

        fallback = "抱歉，我不太理解你的问题。你可以问我：\n• 关卡怎么解锁\n• 通关条件是什么\n• 操作按键怎么按\n• 存档丢失怎么办\n• 称号怎么获得"

        def generate():
            yield f"data: {fallback}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        print(f"Stream chat error: {e}")
        def generate_error():
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(generate_error(), media_type="text/event-stream")


@app.get("/api/chat_logs")
async def get_chat_logs(user_id: str = None, limit: int = 50, offset: int = 0):
    try:
        logs = db.get_chat_logs(user_id, limit, offset)
        return {"success": True, "data": logs}
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


@app.get("/api/knowledge")
async def get_knowledge(game: str = None):
    try:
        items = db.get_knowledge(game)
        default_items = kb.get_game_knowledge(game) if game else kb.knowledge
        return {"success": True, "data": items, "default_data": default_items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge")
async def add_knowledge(item: dict):
    try:
        game = item.get("game", "common")
        keywords = item.get("keywords", [])
        answer = item.get("answer", "")

        db.insert_knowledge(game, keywords, answer)
        kb.add_knowledge(game, keywords, answer)
        return {"success": True, "message": "添加成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/knowledge/{kb_id}")
async def update_knowledge(kb_id: int, item: dict):
    try:
        db.update_knowledge(kb_id, item.get("game"), item.get("keywords"), item.get("answer"))
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


@app.get("/api/search_knowledge")
async def search_knowledge(query: str, game: str = None):
    try:
        answer, category, score = kb.search(query, game)
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


@app.get("/api/game_categories")
async def get_game_categories():
    return {"success": True, "data": kb.game_categories}


@app.post("/api/test_coze")
async def test_coze():
    if not coze_client.api_key or not coze_client.bot_id:
        return {"success": False, "error": "Coze配置未设置"}

    try:
        result = coze_client.chat("你好")
        if result.get("answer"):
            return {"success": True, "response": result["answer"]}
        else:
            return {"success": False, "error": result.get("error", "未知错误")}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/")
async def root():
    return {
        "message": "游戏AI助手后端服务",
        "endpoints": [
            "GET /api/health - 健康检查",
            "GET /api/config - 获取Coze配置",
            "POST /api/config - 设置Coze配置",
            "POST /api/chat - 非流式聊天",
            "POST /api/chat/stream - 流式聊天",
            "GET /api/chat_logs - 获取对话日志",
            "GET /api/stats - 获取统计数据",
            "GET/POST/PUT/DELETE /api/knowledge - 知识库管理",
            "GET /api/search_knowledge - 搜索知识库",
            "GET /api/game_categories - 游戏分类",
            "POST /api/test_coze - 测试Coze连接"
        ],
        "docs": "http://localhost:8000/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)