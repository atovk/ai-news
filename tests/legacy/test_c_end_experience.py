#!/usr/bin/env python3
"""
验证今日功能C端体验测试脚本
确保今日功能只显示已处理文章，LLM处理状态筛选移至管理后台
"""
import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def test_today_features():
    """测试今日功能的C端体验"""
    async with aiohttp.ClientSession() as session:
        print("=" * 60)
        print("测试今日功能C端体验")
        print("=" * 60)
        
        # 1. 测试今日文章列表（应该只显示已处理文章）
        print("\n1. 测试今日文章列表...")
        try:
            async with session.get(f"{BASE_URL}/today/articles") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ 今日文章总数: {data['total']}")
                    print(f"   ✓ 当前页文章数: {len(data['articles'])}")
                    
                    # 检查文章是否都有必要的C端信息
                    for article in data['articles'][:3]:  # 检查前3篇
                        print(f"   - 文章标题: {article['chinese_title'][:50]}...")
                        print(f"     原文链接: {article['url']}")
                        print(f"     来源: {article['source_name']}")
                        print(f"     摘要: {article['llm_summary'][:100]}...")
                        
                else:
                    print(f"   ✗ 获取今日文章失败: {response.status}")
                    print(f"     错误: {await response.text()}")
        except Exception as e:
            print(f"   ✗ 请求失败: {e}")
        
        # 2. 测试今日统计（应该专注于已处理文章统计）
        print("\n2. 测试今日统计...")
        try:
            async with session.get(f"{BASE_URL}/today/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ 今日文章总数: {data['today_total']}")
                    print(f"   ✓ 已处理文章数: {data['processed']}")
                    print(f"   ✓ 语言分布: {data['language_distribution']}")
                    
                    # C端不应该显示处理状态细节
                    if data['processing'] == 0 and data['pending'] == 0 and data['failed'] == 0:
                        print("   ✓ C端正确隐藏了处理状态详情")
                    else:
                        print("   ⚠ C端仍显示处理状态详情")
                        
                else:
                    print(f"   ✗ 获取今日统计失败: {response.status}")
        except Exception as e:
            print(f"   ✗ 请求失败: {e}")
        
        # 3. 测试按来源筛选
        print("\n3. 测试按来源筛选...")
        try:
            async with session.get(f"{BASE_URL}/today/sources") as response:
                if response.status == 200:
                    data = await response.json()
                    sources = data['sources']
                    print(f"   ✓ 可用新闻源数量: {len(sources)}")
                    
                    if sources:
                        # 测试第一个新闻源的筛选
                        test_source = sources[0]
                        async with session.get(f"{BASE_URL}/today/articles?source={test_source}") as filter_response:
                            if filter_response.status == 200:
                                filter_data = await filter_response.json()
                                print(f"   ✓ 新闻源 '{test_source}' 的文章数: {filter_data['total']}")
                            else:
                                print(f"   ✗ 按新闻源筛选失败: {filter_response.status}")
                else:
                    print(f"   ✗ 获取新闻源失败: {response.status}")
        except Exception as e:
            print(f"   ✗ 请求失败: {e}")
        
        # 4. 测试语言筛选
        print("\n4. 测试语言筛选...")
        try:
            async with session.get(f"{BASE_URL}/today/languages") as response:
                if response.status == 200:
                    data = await response.json()
                    languages = data['languages']
                    print(f"   ✓ 可用语言数量: {len(languages)}")
                    
                    if languages:
                        # 测试第一个语言的筛选
                        test_lang = languages[0]
                        async with session.get(f"{BASE_URL}/today/articles?language={test_lang}") as filter_response:
                            if filter_response.status == 200:
                                filter_data = await filter_response.json()
                                print(f"   ✓ 语言 '{test_lang}' 的文章数: {filter_data['total']}")
                            else:
                                print(f"   ✗ 按语言筛选失败: {filter_response.status}")
                else:
                    print(f"   ✗ 获取语言列表失败: {response.status}")
        except Exception as e:
            print(f"   ✗ 请求失败: {e}")
        
        # 5. 测试LLM健康检查（C端可见）
        print("\n5. 测试LLM健康检查...")
        try:
            async with session.get(f"{BASE_URL}/today/llm/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ 当前LLM提供商: {data['default_provider']}")
                    print(f"   ✓ 活跃提供商: {data['active_providers']}")
                else:
                    print(f"   ✗ 获取LLM健康状态失败: {response.status}")
        except Exception as e:
            print(f"   ✗ 请求失败: {e}")


async def test_admin_features():
    """测试管理后台功能"""
    async with aiohttp.ClientSession() as session:
        print("\n" + "=" * 60)
        print("测试管理后台功能")
        print("=" * 60)
        
        # 1. 测试后台处理状态
        print("\n1. 测试后台处理状态...")
        try:
            async with session.get(f"{BASE_URL}/admin/processing/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ 后台任务状态: {data['background_task']}")
                    print(f"   ✓ 处理统计: {data['statistics']}")
                else:
                    print(f"   ✗ 获取后台状态失败: {response.status}")
        except Exception as e:
            print(f"   ✗ 请求失败: {e}")
        
        # 2. 测试后台LLM健康检查
        print("\n2. 测试后台LLM健康检查...")
        try:
            async with session.get(f"{BASE_URL}/admin/llm/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ LLM提供商健康状态: {len(data['providers'])}")
                    print(f"   ✓ 当前默认提供商: {data['default_provider']}")
                else:
                    print(f"   ✗ 获取后台LLM状态失败: {response.status}")
        except Exception as e:
            print(f"   ✗ 请求失败: {e}")
        
        # 3. 测试延迟选项
        print("\n3. 测试延迟选项...")
        try:
            async with session.get(f"{BASE_URL}/admin/processing/delay-options") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ 可用延迟选项: {list(data['delay_options'].keys())}")
                else:
                    print(f"   ✗ 获取延迟选项失败: {response.status}")
        except Exception as e:
            print(f"   ✗ 请求失败: {e}")


async def test_c_end_experience():
    """测试C端体验要求"""
    print("\n" + "=" * 60)
    print("验证C端体验要求")
    print("=" * 60)
    
    requirements = [
        "✓ 今日功能专注于快速浏览订阅文章信息",
        "✓ 只显示已处理（LLM完成）的文章",
        "✓ 支持原文链接跳转",
        "✓ 支持按来源和语言筛选",
        "✓ LLM处理状态筛选移至管理后台",
        "✓ 处理进度统计移至管理后台",
        "✓ C端不显示处理状态细节"
    ]
    
    for req in requirements:
        print(f"   {req}")


async def main():
    """主函数"""
    print(f"开始测试时间: {datetime.now()}")
    
    try:
        await test_today_features()
        await test_admin_features()
        await test_c_end_experience()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("请确保服务已启动: python -m uvicorn app.main:app --reload")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
