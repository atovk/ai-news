"""
FastAPI 应用主入口
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.api.v1 import articles, search, sources, today, admin
from app.models.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI News Aggregation System - 智能新闻聚合系统",
    debug=settings.DEBUG
)

# 配置 CORS 允许的来源
def get_allowed_origins():
    """获取允许的 CORS 来源列表"""
    if settings.ALLOWED_ORIGINS:
        # 生产环境：使用配置的来源列表
        return [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
    else:
        # 开发环境：仅允许本地开发来源
        return [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(articles.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")
app.include_router(today.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "api": "/api/v1"
    }


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": request.url.path
        }
    )


def main():
    """命令行启动入口"""
    import uvicorn
    uvicorn.run(
        "ai_news.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
