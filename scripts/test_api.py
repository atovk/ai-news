"""
今日功能 API 测试脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_today_api():
    """测试今日功能API"""
    print("=== 测试今日功能API ===")
    
    try:
        # 测试健康检查
        response = client.get("/api/v1/health")
        print(f"健康检查: {response.status_code} - {response.json()}")
        
        # 测试今日统计
        response = client.get("/api/v1/today/stats")
        print(f"今日统计: {response.status_code} - {response.json()}")
        
        # 测试今日文章列表
        response = client.get("/api/v1/today/articles?page=1&size=5")
        print(f"今日文章: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  总数: {data['total']}, 返回: {len(data['articles'])}")
        else:
            print(f"  错误: {response.json()}")
        
        # 测试获取可用源
        response = client.get("/api/v1/today/sources")
        print(f"可用源: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  源数量: {len(data['sources'])}")
        
        # 测试获取可用语言
        response = client.get("/api/v1/today/languages")
        print(f"可用语言: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  语言: {data['languages']}")
        
        # 测试LLM健康检查
        response = client.get("/api/v1/today/llm/health")
        print(f"LLM健康: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  默认提供商: {data['default_provider']}")
            print(f"  活跃提供商: {data['active_providers']}")
        else:
            print(f"  错误: {response.json()}")
        
        print("API测试完成！")
        
    except Exception as e:
        print(f"API测试失败: {e}")


def test_api_documentation():
    """测试API文档"""
    print("\n=== 测试API文档 ===")
    
    try:
        # 测试OpenAPI文档
        response = client.get("/openapi.json")
        print(f"OpenAPI文档: {response.status_code}")
        
        # 测试Swagger UI
        response = client.get("/docs")
        print(f"Swagger UI: {response.status_code}")
        
        print("API文档测试完成！")
        
    except Exception as e:
        print(f"API文档测试失败: {e}")


if __name__ == "__main__":
    print("开始API测试...")
    test_today_api()
    test_api_documentation()
    print("\n所有测试完成！")
    print("\n启动服务命令:")
    print("poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    print("\n访问地址:")
    print("- API文档: http://localhost:8000/docs")
    print("- 今日功能: http://localhost:8000/api/v1/today")
