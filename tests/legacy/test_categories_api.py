#!/usr/bin/env python3
"""
测试分类 API 是否正常工作
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_get_categories():
    """测试获取分类列表"""
    print("\n=== 测试获取分类列表 ===")
    try:
        response = requests.get(f"{BASE_URL}/categories")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"分类总数: {data.get('total', 0)}")
            print(f"返回分类数: {len(data.get('categories', []))}")
            
            print("\n分类列表:")
            for cat in data.get('categories', []):
                print(f"  - ID: {cat['id']}, 名称: {cat['name']}, 描述: {cat.get('description', '')}")
            
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_get_category_by_id(category_id=1):
    """测试获取单个分类"""
    print(f"\n=== 测试获取分类 ID: {category_id} ===")
    try:
        response = requests.get(f"{BASE_URL}/categories/{category_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            cat = response.json()
            print(f"分类: {cat['name']}")
            print(f"描述: {cat.get('description', '')}")
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_get_category_articles(category_id=1):
    """测试获取分类下的文章"""
    print(f"\n=== 测试获取分类 {category_id} 的文章 ===")
    try:
        response = requests.get(f"{BASE_URL}/categories/{category_id}/articles")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"文章总数: {data.get('total', 0)}")
            print(f"返回文章数: {len(data.get('articles', []))}")
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_create_category():
    """测试创建分类"""
    print("\n=== 测试创建新分类 ===")
    try:
        new_category = {
            "name": "测试分类",
            "description": "这是一个测试分类",
            "is_active": True
        }
        
        response = requests.post(
            f"{BASE_URL}/categories",
            json=new_category
        )
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 201:
            cat = response.json()
            print(f"✅ 创建成功: ID={cat['id']}, 名称={cat['name']}")
            return cat['id']
        else:
            print(f"创建失败或已存在: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def test_health_check():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ 后端服务正常")
            print(f"响应: {response.json()}")
            return True
        else:
            print(f"❌ 后端服务异常")
            return False
            
    except Exception as e:
        print(f"❌ 无法连接到后端: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("分类 API 测试工具")
    print("=" * 50)
    
    # 健康检查
    if not test_health_check():
        print("\n❌ 后端服务未启动，请先启动服务")
        print("启动命令: make run 或 uvicorn app.main:app --reload")
        return
    
    # 测试获取分类列表
    if not test_get_categories():
        print("\n⚠️  获取分类列表失败，可能需要先运行种子数据脚本")
        print("运行命令: python scripts/seed_data.py")
    
    # 测试获取单个分类
    test_get_category_by_id(1)
    
    # 测试获取分类下的文章
    test_get_category_articles(1)
    
    # 测试创建分类
    new_id = test_create_category()
    if new_id:
        print(f"\n可以手动删除测试分类: DELETE {BASE_URL}/categories/{new_id}")
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
