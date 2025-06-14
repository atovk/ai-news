"""
RSSConfigManager 测试
"""
import pytest
import re
from unittest.mock import Mock

from app.utils.rss_config import (
    RSSConfigManager, 
    RSSSourceConfig, 
    FieldMapping, 
    ContentType
)


class TestFieldMapping:
    """字段映射测试"""
    
    def test_default_initialization(self):
        """测试默认初始化"""
        mapping = FieldMapping()
        
        assert 'title' in mapping.title_fields
        assert 'content' in mapping.content_fields
        assert 'author' in mapping.author_fields
        assert 'link' in mapping.link_fields
        assert 'published' in mapping.published_fields
        assert 'tags' in mapping.tags_fields
        assert 'media_thumbnail' in mapping.image_fields
        assert isinstance(mapping.custom_extractors, dict)

    def test_custom_initialization(self):
        """测试自定义初始化"""
        custom_extractors = {'test_field': lambda x: x}
        
        mapping = FieldMapping(
            title_fields=['custom_title'],
            content_fields=['custom_content'],
            custom_extractors=custom_extractors
        )
        
        assert mapping.title_fields == ['custom_title']
        assert mapping.content_fields == ['custom_content']
        assert mapping.custom_extractors == custom_extractors

    def test_field_priorities(self):
        """测试字段优先级"""
        mapping = FieldMapping()
        
        # 内容字段应该按优先级排序
        assert mapping.content_fields[0] == 'content'
        assert 'content:encoded' in mapping.content_fields
        
        # 发布时间字段应该有多个候选
        assert 'published' in mapping.published_fields
        assert 'updated' in mapping.published_fields


class TestRSSSourceConfig:
    """RSS源配置测试"""
    
    def test_default_initialization(self):
        """测试默认初始化"""
        config = RSSSourceConfig(name='test')
        
        assert config.name == 'test'
        assert config.url == ''
        assert config.encoding is None
        assert isinstance(config.headers, dict)
        assert config.timeout == 30
        assert config.remove_html is True
        assert config.max_title_length == 200
        assert isinstance(config.content_filters, list)
        assert isinstance(config.required_fields, list)
        assert config.min_title_length == 5
        assert config.min_content_length == 10

    def test_custom_initialization(self):
        """测试自定义初始化"""
        custom_headers = {'User-Agent': 'Custom Bot'}
        custom_filters = [r'<ad>.*?</ad>']
        custom_processors = {'title': lambda x, y: x.upper()}
        
        config = RSSSourceConfig(
            name='custom',
            url='https://example.com/feed',
            encoding='utf-8',
            headers=custom_headers,
            timeout=60,
            remove_html=False,
            max_content_length=5000,
            content_filters=custom_filters,
            custom_processors=custom_processors,
            required_fields=['title', 'url', 'content'],
            min_title_length=10
        )
        
        assert config.name == 'custom'
        assert config.url == 'https://example.com/feed'
        assert config.encoding == 'utf-8'
        assert config.headers == custom_headers
        assert config.timeout == 60
        assert config.remove_html is False
        assert config.max_content_length == 5000
        assert config.content_filters == custom_filters
        assert config.custom_processors == custom_processors
        assert 'content' in config.required_fields
        assert config.min_title_length == 10

    def test_field_mapping_inheritance(self):
        """测试字段映射继承"""
        custom_mapping = FieldMapping(title_fields=['custom_title'])
        config = RSSSourceConfig(name='test', field_mapping=custom_mapping)
        
        assert config.field_mapping is custom_mapping
        assert config.field_mapping.title_fields == ['custom_title']

    def test_url_cleanup_patterns(self):
        """测试URL清理模式"""
        config = RSSSourceConfig(name='test')
        
        # 默认应该包含UTM参数和锚点清理
        patterns = config.url_cleanup_patterns
        assert any('utm' in pattern for pattern in patterns)
        assert any('#' in pattern for pattern in patterns)


class TestRSSConfigManager:
    """RSS配置管理器测试"""
    
    @pytest.fixture
    def config_manager(self):
        """创建配置管理器实例"""
        return RSSConfigManager()

    def test_initialization(self, config_manager):
        """测试初始化"""
        assert config_manager is not None
        assert isinstance(config_manager.configs, dict)
        assert len(config_manager.configs) > 0

    def test_default_configs_exist(self, config_manager):
        """测试默认配置存在"""
        expected_configs = ['default', 'medium', 'wordpress', 'github', 'reddit', 'hackernews']
        
        for config_name in expected_configs:
            assert config_name in config_manager.configs
            config = config_manager.configs[config_name]
            assert isinstance(config, RSSSourceConfig)
            assert config.name == config_name

    def test_get_config_existing(self, config_manager):
        """测试获取已存在的配置"""
        config = config_manager.get_config('medium')
        
        assert config is not None
        assert config.name == 'medium'
        assert isinstance(config, RSSSourceConfig)

    def test_get_config_nonexistent(self, config_manager):
        """测试获取不存在的配置"""
        config = config_manager.get_config('nonexistent')
        
        # 应该返回默认配置
        assert config is not None
        assert config.name == 'default'

    def test_detect_config_medium(self, config_manager):
        """测试检测Medium配置"""
        urls = [
            'https://medium.com/@user/feed',
            'https://medium.com/publication/feed',
            'https://user.medium.com/feed'
        ]
        
        for url in urls:
            config = config_manager.detect_config(url)
            assert config.name == 'medium'

    def test_detect_config_wordpress(self, config_manager):
        """测试检测WordPress配置"""
        urls = [
            'https://example.com/wp-content/feeds/rss.xml',
            'https://blog.wordpress.com/feed',
            'https://example.com/wp-json/wp/v2/posts'
        ]
        
        for url in urls:
            config = config_manager.detect_config(url)
            assert config.name == 'wordpress'

    def test_detect_config_github(self, config_manager):
        """测试检测GitHub配置"""
        urls = [
            'https://github.com/user/repo/commits.atom',
            'https://github.com/user/repo/releases.atom',
            'https://github.com/user.atom'
        ]
        
        for url in urls:
            config = config_manager.detect_config(url)
            assert config.name == 'github'

    def test_detect_config_reddit(self, config_manager):
        """测试检测Reddit配置"""
        urls = [
            'https://www.reddit.com/r/python/.rss',
            'https://reddit.com/r/programming/new/.rss',
            'https://old.reddit.com/r/MachineLearning/.rss'
        ]
        
        for url in urls:
            config = config_manager.detect_config(url)
            assert config.name == 'reddit'

    def test_detect_config_hackernews(self, config_manager):
        """测试检测HackerNews配置"""
        urls = [
            'https://news.ycombinator.com/rss',
            'https://news.ycombinator.com/bigrss'
        ]
        
        for url in urls:
            config = config_manager.detect_config(url)
            assert config.name == 'hackernews'

    def test_detect_config_default(self, config_manager):
        """测试检测默认配置"""
        urls = [
            'https://example.com/feed.xml',
            'https://unknown-site.com/rss',
            'https://blog.example.org/atom.xml'
        ]
        
        for url in urls:
            config = config_manager.detect_config(url)
            assert config.name == 'default'

    def test_add_config(self, config_manager):
        """测试添加自定义配置"""
        custom_config = RSSSourceConfig(
            name='custom_site',
            url='https://custom.com/feed',
            max_content_length=2000
        )
        
        config_manager.add_config('custom_site', custom_config)
        
        assert 'custom_site' in config_manager.configs
        retrieved_config = config_manager.get_config('custom_site')
        # 由于get_config返回深拷贝，所以不能用is比较，但内容应该相同
        assert retrieved_config.name == 'custom_site'
        assert retrieved_config.url == 'https://custom.com/feed'
        assert retrieved_config.max_content_length == 2000

    def test_medium_config_specifics(self, config_manager):
        """测试Medium配置特性"""
        config = config_manager.get_config('medium')
        
        assert 'content:encoded' in config.field_mapping.content_fields
        assert 'dc:creator' in config.field_mapping.author_fields
        assert config.max_content_length == 3000
        assert any('Medium is an open platform' in filter for filter in config.content_filters)

    def test_wordpress_config_specifics(self, config_manager):
        """测试WordPress配置特性"""
        config = config_manager.get_config('wordpress')
        
        assert 'content:encoded' in config.field_mapping.content_fields
        assert 'dc:creator' in config.field_mapping.author_fields
        assert 'category' in config.field_mapping.tags_fields
        assert any('wp-' in filter for filter in config.content_filters)

    def test_github_config_specifics(self, config_manager):
        """测试GitHub配置特性"""
        config = config_manager.get_config('github')
        
        assert 'author.name' in config.field_mapping.author_fields
        assert 'link.href' in config.field_mapping.link_fields
        assert 'repository' in config.field_mapping.custom_extractors
        assert 'event_type' in config.field_mapping.custom_extractors

    def test_reddit_config_specifics(self, config_manager):
        """测试Reddit配置特性"""
        config = config_manager.get_config('reddit')
        
        assert 'subreddit' in config.field_mapping.custom_extractors
        assert 'score' in config.field_mapping.custom_extractors
        assert any('submitted by' in filter for filter in config.content_filters)

    def test_hackernews_config_specifics(self, config_manager):
        """测试HackerNews配置特性"""
        config = config_manager.get_config('hackernews')
        
        assert 'points' in config.field_mapping.custom_extractors
        assert 'comments_count' in config.field_mapping.custom_extractors
        assert config.max_content_length == 500

    def test_custom_extractors_functionality(self, config_manager):
        """测试自定义提取器功能"""
        # 测试阅读时间估算
        reading_time = config_manager._estimate_reading_time('word ' * 400)  # 400个单词
        assert reading_time == 2  # 应该约为2分钟
        
        # 测试GitHub仓库提取
        repo = config_manager._extract_github_repo('https://github.com/user/repo/commits.atom')
        assert repo == 'user/repo'
        
        # 测试GitHub事件类型提取
        event_type = config_manager._extract_github_event_type('user pushed to main')
        assert event_type == 'push'
        
        # 测试subreddit提取
        subreddit = config_manager._extract_subreddit('https://reddit.com/r/python/comments/xyz')
        assert subreddit == 'python'
        
        # 测试Reddit分数提取
        score = config_manager._extract_reddit_score('[123] Interesting post title')
        assert score == 123
        
        # 测试HN点数提取
        points = config_manager._extract_hn_points('This has 456 points and 78 comments')
        assert points == 456
        
        # 测试HN评论数提取
        comments = config_manager._extract_hn_comments('This has 456 points and 78 comments')
        assert comments == 78

    def test_custom_extractors_edge_cases(self, config_manager):
        """测试自定义提取器边缘情况"""
        # 测试空内容的阅读时间
        reading_time = config_manager._estimate_reading_time('')
        assert reading_time == 1  # 最小值
        
        # 测试无匹配的GitHub仓库
        repo = config_manager._extract_github_repo('https://example.com/not-github')
        assert repo is None
        
        # 测试无匹配的事件类型
        event_type = config_manager._extract_github_event_type('random title')
        assert event_type == 'other'
        
        # 测试无匹配的subreddit
        subreddit = config_manager._extract_subreddit('https://example.com/not-reddit')
        assert subreddit is None
        
        # 测试无匹配的分数
        score = config_manager._extract_reddit_score('No score in this title')
        assert score is None
        
        # 测试无匹配的点数
        points = config_manager._extract_hn_points('No points mentioned here')
        assert points is None
        
        # 测试无匹配的评论数
        comments = config_manager._extract_hn_comments('No comments mentioned')
        assert comments is None

    def test_config_immutability(self, config_manager):
        """测试配置不可变性"""
        original_config = config_manager.get_config('medium')
        modified_config = config_manager.get_config('medium')
        
        # 修改一个配置不应该影响另一个
        modified_config.max_content_length = 9999
        
        # 获取新的配置实例进行验证
        fresh_config = config_manager.get_config('medium')
        assert fresh_config.max_content_length == 3000  # 应该保持原值

    def test_regex_patterns_validity(self, config_manager):
        """测试正则表达式模式有效性"""
        for config_name, config in config_manager.configs.items():
            # 测试内容过滤器
            for pattern in config.content_filters:
                try:
                    re.compile(pattern)
                except re.error:
                    pytest.fail(f"Invalid regex pattern in {config_name} content_filters: {pattern}")
            
            # 测试标题过滤器
            for pattern in config.title_filters:
                try:
                    re.compile(pattern)
                except re.error:
                    pytest.fail(f"Invalid regex pattern in {config_name} title_filters: {pattern}")
            
            # 测试URL清理模式
            for pattern in config.url_cleanup_patterns:
                try:
                    re.compile(pattern)
                except re.error:
                    pytest.fail(f"Invalid regex pattern in {config_name} url_cleanup_patterns: {pattern}")

    def test_content_type_enum(self):
        """测试内容类型枚举"""
        assert ContentType.TITLE.value == "title"
        assert ContentType.CONTENT.value == "content"
        assert ContentType.SUMMARY.value == "summary"
        assert ContentType.AUTHOR.value == "author"
        assert ContentType.LINK.value == "link"
        assert ContentType.PUBLISHED.value == "published"
        assert ContentType.TAGS.value == "tags"
        assert ContentType.IMAGE.value == "image"
        
        # 测试枚举完整性
        expected_types = {'title', 'content', 'summary', 'author', 'link', 'published', 'tags', 'image'}
        actual_types = {ct.value for ct in ContentType}
        assert actual_types == expected_types

    def test_config_validation(self, config_manager):
        """测试配置验证"""
        for config_name, config in config_manager.configs.items():
            # 验证必需字段存在
            assert config.name is not None
            assert isinstance(config.name, str)
            assert len(config.name) > 0
            
            # 验证超时时间合理
            assert config.timeout > 0
            assert config.timeout <= 300  # 不应该超过5分钟
            
            # 验证长度限制合理
            if config.max_content_length:
                assert config.max_content_length > 0
            if config.max_title_length:
                assert config.max_title_length > 0
            
            # 验证最小长度设置
            assert config.min_title_length >= 0
            assert config.min_content_length >= 0
            
            # 验证字段映射存在
            if config.field_mapping:
                assert isinstance(config.field_mapping, FieldMapping)
                assert len(config.field_mapping.title_fields) > 0
                assert len(config.field_mapping.content_fields) > 0

    def test_thread_safety_simulation(self, config_manager):
        """测试线程安全性模拟"""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker():
            try:
                for _ in range(10):
                    config = config_manager.get_config('medium')
                    results.append(config.name)
                    time.sleep(0.001)  # 模拟一些处理时间
            except Exception as e:
                errors.append(e)
        
        # 创建多个线程
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 50  # 5个线程 × 10次调用
        assert all(result == 'medium' for result in results)
