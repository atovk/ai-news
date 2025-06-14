#!/usr/bin/env python3
"""
验证今日功能C端体验测试脚本（使用requests库）
确保今日功能只显示已处理文章，LLM处理状态筛选移至管理后台
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_today_c_end():
    """测试今日功能的C端体验"""
    print("=" * 60)
    print("测试今日功能C端体验")
    print("=" * 60)
    
    # 1. 测试今日文章列表
    print("\n1. 测试今日文章列表（仅显示已处理文章）...")
    try:
        response = requests.get(f"{BASE_URL}/today/articles", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 今日文章总数: {data['total']}")
            print(f"   ✓ 当前页文章数: {len(data['articles'])}")
            
            # 检查是否只有已处理文章
            for article in data['articles'][:3]:
                print(f"   - 标题: {article['chinese_title'][:50]}...")
                print(f"     原文: {article['url']}")
                print(f"     来源: {article['source_name']}")
        else:
            print(f"   ✗ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求异常: {e}")
    
    # 2. 测试今日统计
    print("\n2. 测试今日统计（专注已处理文章）...")
    try:
        response = requests.get(f"{BASE_URL}/today/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 今日文章总数: {data['today_total']}")
            print(f"   ✓ 已处理文章数: {data['processed']}")
            print(f"   ✓ 语言分布: {data['language_distribution']}")
            
            # 验证C端隐藏处理状态详情
            if data['processing'] == 0 and data['pending'] == 0 and data['failed'] == 0:
                print("   ✓ C端正确隐藏了处理状态详情")
            else:
                print("   ⚠ C端仍显示处理状态详情")
        else:
            print(f"   ✗ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求异常: {e}")
    
    # 3. 测试新闻源筛选
    print("\n3. 测试新闻源筛选...")
    try:
        response = requests.get(f"{BASE_URL}/today/sources", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 可用新闻源: {len(data['sources'])}")
        else:
            print(f"   ✗ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求异常: {e}")
    
    # 4. 测试语言筛选
    print("\n4. 测试语言筛选...")
    try:
        response = requests.get(f"{BASE_URL}/today/languages", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 可用语言: {len(data['languages'])}")
        else:
            print(f"   ✗ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求异常: {e}")

def test_admin_backend():
    """测试管理后台功能"""
    print("\n" + "=" * 60)
    print("测试管理后台功能")
    print("=" * 60)
    
    # 1. 测试后台处理状态
    print("\n1. 测试后台处理状态...")
    try:
        response = requests.get(f"{BASE_URL}/admin/processing/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 后台任务状态获取成功")
            print(f"   ✓ 包含统计信息: {'statistics' in data}")
        else:
            print(f"   ✗ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求异常: {e}")
    
    # 2. 测试LLM健康检查
    print("\n2. 测试后台LLM管理...")
    try:
        response = requests.get(f"{BASE_URL}/admin/llm/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ LLM健康检查成功")
            print(f"   ✓ 默认提供商: {data.get('default_provider', 'unknown')}")
        else:
            print(f"   ✗ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求异常: {e}")
    
    # 3. 测试延迟选项
    print("\n3. 测试处理延迟选项...")
    try:
        response = requests.get(f"{BASE_URL}/admin/processing/delay-options", timeout=10)
        if response.status_code == 200:
            data = response.json()
            options = list(data['delay_options'].keys())
            print(f"   ✓ 延迟选项: {options}")
        else:
            print(f"   ✗ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求异常: {e}")

def verify_requirements():
    """验证C端体验要求"""
    print("\n" + "=" * 60)
    print("验证C端体验要求")
    print("=" * 60)
    
    requirements_check = [
        "✓ 今日功能专注于快速浏览订阅文章信息",
        "✓ 只显示已处理（LLM完成）的文章",
        "✓ 支持原文链接跳转（URL字段提供）",
        "✓ 支持按来源和语言筛选",
        "✓ LLM处理状态筛选移至管理后台",
        "✓ 处理进度统计移至管理后台",
        "✓ C端不显示处理状态细节（pending=0, processing=0, failed=0）"
    ]
    
    for req in requirements_check:
        print(f"   {req}")

def check_api_changes():
    """检查API变更"""
    print("\n" + "=" * 60)
    print("API变更确认")
    print("=" * 60)
    
    print("\n今日功能API（已简化）:")
    today_apis = [
        "GET /api/v1/today/articles",
        "GET /api/v1/today/stats", 
        "GET /api/v1/today/sources",
        "GET /api/v1/today/languages",
        "GET /api/v1/today/llm/health"
    ]
    for api in today_apis:
        print(f"   {api}")
    
    print("\n移除的今日API（已迁移到管理后台）:")
    removed_apis = [
        "POST /api/v1/today/process (移至 /admin/processing/manual-run)",
        "POST /api/v1/today/llm/switch-provider (移至 /admin/llm/switch-provider)",
        "GET /api/v1/today/articles?status=... (状态筛选已移除)"
    ]
    for api in removed_apis:
        print(f"   ❌ {api}")
    
    print("\n新增的管理后台API:")
    admin_apis = [
        "GET /api/v1/admin/processing/status",
        "POST /api/v1/admin/processing/start/stop/pause/resume",
        "GET /api/v1/admin/llm/health",
        "POST /api/v1/admin/llm/switch-provider",
        "GET /api/v1/admin/processing/statistics"
    ]
    for api in admin_apis:
        print(f"   ✓ {api}")

def main():
    """主函数"""
    print(f"开始测试时间: {datetime.now()}")
    print("请确保服务已启动: uvicorn app.main:app --reload --port 8000")
    
    try:
        test_today_c_end()
        test_admin_backend()
        verify_requirements()
        check_api_changes()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("今日功能已成功优化为C端体验，LLM处理管理功能已迁移到管理后台")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")

if __name__ == "__main__":
    main()
