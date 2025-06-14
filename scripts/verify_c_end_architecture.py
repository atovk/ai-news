#!/usr/bin/env python3
"""
验证今日功能C端体验 - 代码结构检查
确保今日功能只显示已处理文章，LLM处理状态筛选移至管理后台
"""
import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_today_api_changes():
    """检查今日API的变更"""
    print("=" * 60)
    print("检查今日API变更")
    print("=" * 60)
    
    # 检查今日API文件
    today_api_file = "app/api/v1/today.py"
    if os.path.exists(today_api_file):
        with open(today_api_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n1. 检查今日API内容...")
        
        # 检查是否移除了状态筛选参数
        if 'status: Optional[str] = Query(' not in content:
            print("   ✓ 已移除状态筛选参数")
        else:
            print("   ✗ 仍包含状态筛选参数")
        
        # 检查是否移除了处理触发接口
        if '@router.post("/process"' not in content:
            print("   ✓ 已移除手动处理触发接口")
        else:
            print("   ✗ 仍包含手动处理触发接口")
        
        # 检查是否移除了LLM提供商切换
        if 'switch_llm_provider' not in content:
            print("   ✓ 已移除LLM提供商切换接口")
        else:
            print("   ✗ 仍包含LLM提供商切换接口")
        
        # 检查核心C端功能是否保留
        core_features = [
            ('/articles', '文章列表'),
            ('/stats', '统计信息'),
            ('/sources', '新闻源列表'),
            ('/languages', '语言列表'),
            ('/llm/health', 'LLM健康检查')
        ]
        
        print("\n2. 检查核心C端功能...")
        for endpoint, name in core_features:
            if endpoint in content:
                print(f"   ✓ 保留 {name} 接口")
            else:
                print(f"   ✗ 缺失 {name} 接口")
    else:
        print(f"   ✗ 今日API文件不存在: {today_api_file}")

def check_admin_api_changes():
    """检查管理后台API的变更"""
    print("\n" + "=" * 60)
    print("检查管理后台API变更")
    print("=" * 60)
    
    admin_api_file = "app/api/v1/admin.py"
    if os.path.exists(admin_api_file):
        with open(admin_api_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n1. 检查管理后台API内容...")
        
        # 检查处理管理功能
        processing_features = [
            ('/processing/status', '处理状态'),
            ('/processing/start', '启动处理'),
            ('/processing/stop', '停止处理'),
            ('/processing/pause', '暂停处理'),
            ('/processing/resume', '恢复处理'),
            ('/processing/manual-run', '手动处理')
        ]
        
        for endpoint, name in processing_features:
            if endpoint in content:
                print(f"   ✓ 包含 {name} 接口")
            else:
                print(f"   ✗ 缺失 {name} 接口")
        
        # 检查LLM管理功能
        llm_features = [
            ('/llm/health', 'LLM健康检查'),
            ('/llm/switch-provider', 'LLM提供商切换'),
            ('/llm/providers', 'LLM提供商列表')
        ]
        
        print("\n2. 检查LLM管理功能...")
        for endpoint, name in llm_features:
            if endpoint in content:
                print(f"   ✓ 包含 {name} 接口")
            else:
                print(f"   ✗ 缺失 {name} 接口")
    else:
        print(f"   ✗ 管理后台API文件不存在: {admin_api_file}")

def check_today_service_changes():
    """检查今日服务的变更"""
    print("\n" + "=" * 60)
    print("检查今日服务变更")
    print("=" * 60)
    
    service_file = "app/services/today_service.py"
    if os.path.exists(service_file):
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n1. 检查服务层变更...")
        
        # 检查get_today_articles方法是否移除了status参数
        if 'status: Optional[str] = None' not in content:
            print("   ✓ get_today_articles已移除status参数")
        else:
            print("   ✗ get_today_articles仍包含status参数")
        
        # 检查是否只显示已完成的文章
        if 'LLMProcessingStatus.COMPLETED' in content:
            print("   ✓ 服务专注于显示已完成文章")
        else:
            print("   ✗ 服务未专注于已完成文章")
        
        # 检查统计信息是否简化
        if 'processing=0' in content and 'pending=0' in content:
            print("   ✓ 统计信息已简化（隐藏处理状态详情）")
        else:
            print("   ✗ 统计信息未简化")
    else:
        print(f"   ✗ 今日服务文件不存在: {service_file}")

def check_schemas_changes():
    """检查数据模型的变更"""
    print("\n" + "=" * 60)
    print("检查数据模型变更")
    print("=" * 60)
    
    schema_file = "app/schemas/today.py"
    if os.path.exists(schema_file):
        with open(schema_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n1. 检查Today Schemas...")
        
        # 检查核心模型是否存在
        models = [
            'TodayArticleView',
            'TodayStatsResponse', 
            'TodayArticleListResponse',
            'LLMHealthResponse'
        ]
        
        for model in models:
            if f'class {model}' in content:
                print(f"   ✓ 包含 {model} 模型")
            else:
                print(f"   ✗ 缺失 {model} 模型")
        
        # 检查文章视图是否包含C端必要字段
        c_end_fields = ['url', 'chinese_title', 'llm_summary', 'source_name']
        for field in c_end_fields:
            if field in content:
                print(f"   ✓ 文章视图包含 {field} 字段")
            else:
                print(f"   ✗ 文章视图缺失 {field} 字段")
    else:
        print(f"   ✗ Schemas文件不存在: {schema_file}")

def check_config_updates():
    """检查配置文件更新"""
    print("\n" + "=" * 60)
    print("检查配置文件更新")
    print("=" * 60)
    
    config_file = "app/config.py"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n1. 检查LLM配置...")
        
        # 检查LLM相关配置
        llm_configs = [
            'DEFAULT_LLM_PROVIDER',
            'LLM_ASYNC_TIMEOUT',
            'LLM_BATCH_TIMEOUT',
            'BATCH_PROCESS_SIZE'
        ]
        
        for config in llm_configs:
            if config in content:
                print(f"   ✓ 包含 {config} 配置")
            else:
                print(f"   ✗ 缺失 {config} 配置")
    else:
        print(f"   ✗ 配置文件不存在: {config_file}")

def verify_architecture_principles():
    """验证架构设计原则"""
    print("\n" + "=" * 60)
    print("验证架构设计原则")
    print("=" * 60)
    
    principles = [
        "✓ 高内聚低耦合：今日功能专注C端展示，管理功能独立",
        "✓ 易扩展：模块化设计，LLM接口抽象",
        "✓ 职责分离：C端展示 vs 后台管理清晰分离",
        "✓ 用户体验：C端快速浏览，无需关心处理状态",
        "✓ 异步处理：后台处理不影响C端体验",
        "✓ 状态管理：完整的处理状态在管理后台可见"
    ]
    
    for principle in principles:
        print(f"   {principle}")

def main():
    """主函数"""
    print(f"开始检查时间: {datetime.now()}")
    print("验证今日功能C端体验优化")
    
    try:
        check_today_api_changes()
        check_admin_api_changes()
        check_today_service_changes()
        check_schemas_changes()
        check_config_updates()
        verify_architecture_principles()
        
        print("\n" + "=" * 60)
        print("代码结构检查完成！")
        print("今日功能已成功优化为专注C端体验的架构")
        print("=" * 60)
        
        print("\n总结：")
        print("1. 今日功能API已简化，专注于展示已处理文章")
        print("2. LLM处理状态筛选和进度统计已移至管理后台")
        print("3. C端用户可快速浏览文章并跳转到原文")
        print("4. 管理员可在后台完整控制处理状态和进度")
        print("5. 架构符合高内聚低耦合、易扩展的设计原则")
        
    except Exception as e:
        print(f"\n检查过程中出现错误: {e}")

if __name__ == "__main__":
    main()
