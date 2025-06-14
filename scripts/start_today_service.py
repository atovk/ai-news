"""
今日功能启动脚本
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("启动 AI News 今日功能服务...")
    print("API 文档地址: http://localhost:8000/docs")
    print("今日功能 API: http://localhost:8000/api/v1/today")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
