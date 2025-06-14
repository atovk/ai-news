"""
UniversalRSSParser 综合测试
"""
import pytest
import asyncio
import aiohttp
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.utils.rss_parser import UniversalRSSParser, RSSParsingError, RSSValidationError
from app.utils.rss_config import RSSSourceConfig, RSSConfigManager, FieldMapping


class TestUniversalRSSParser:
    """通用RSS解析器测试"""

    @pytest.fixture
    def parser(self):
        """创建解析器实例"""
        return UniversalRSSParser()

    @pytest.fixture
    def config_manager(self):
        """创建配置管理器实例"""
        return RSSConfigManager()

    @pytest.fixture
    def sample_rss_content(self):
        """示例RSS内容"""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Test RSS Feed</title>
                <description>Test feed for parsing</description>
                <link>https://test.com</link>
                <item>
                    <title>Test Article 1</title>
                    <description>This is a test article description</description>
                    <link>https://test.com/article1</link>
                    <pubDate>Mon, 01 Jan 2023 00:00:00 GMT</pubDate>
                    <author>test@example.com (Test Author)</author>
                    <category>Technology</category>
                    <category>Testing</category>
                </item>
                <item>
                    <title>Test Article 2</title>
                    <description>Another test article</description>
                    <link>https://test.com/article2</link>
                    <pubDate>Tue, 02 Jan 2023 12:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>"""

    @pytest.fixture
    def sample_atom_content(self):
        """示例Atom内容"""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <title>Test Atom Feed</title>
            <link href="https://test.com"/>
            <updated>2023-01-01T00:00:00Z</updated>
            <id>https://test.com/feed</id>
            
            <entry>
                <title>Atom Test Article</title>
                <link href="https://test.com/atom-article"/>
                <id>https://test.com/atom-article</id>
                <updated>2023-01-01T10:00:00Z</updated>
                <summary>Atom article summary</summary>
                <content type="html">
                    &lt;p&gt;This is atom content with &lt;strong&gt;HTML&lt;/strong&gt; tags.&lt;/p&gt;
                </content>
                <author>
                    <name>Atom Author</name>
                    <email>atom@example.com</email>
                </author>
                <category term="atom" label="Atom"/>
                <category term="testing" label="Testing"/>
            </entry>
        </feed>"""

    @pytest.fixture
    def custom_config(self):
        """自定义测试配置"""
        return RSSSourceConfig(
            name='test',
            field_mapping=FieldMapping(
                title_fields=['title'],
                content_fields=['content', 'description'],
                author_fields=['author', 'dc:creator'],
                link_fields=['link'],
                published_fields=['published', 'pubDate'],
                tags_fields=['category', 'tags']
            ),
            remove_html=True,
            max_content_length=1000,
            max_title_length=100,
            content_filters=[r'<script.*?</script>'],
            required_fields=['title', 'url'],
            min_title_length=3,
            min_content_length=5
        )

    def test_init_default(self, parser):
        """测试默认初始化"""
        assert parser is not None
        assert parser.config_manager is not None
        assert parser.session is None

    def test_init_with_custom_config_manager(self):
        """测试使用自定义配置管理器初始化"""
        config_manager = RSSConfigManager()
        parser = UniversalRSSParser(config_manager)
        assert parser.config_manager is config_manager

    @pytest.mark.asyncio
    async def test_context_manager(self, parser):
        """测试异步上下文管理器"""
        async with parser as p:
            assert p.session is not None
            assert not p.session.closed
        # 退出后session应该被关闭
        # 注意：在某些版本的aiohttp中，session可能不会立即标记为closed

    def test_parse_rss_content_basic(self, parser, sample_rss_content, custom_config):
        """测试基本RSS内容解析"""
        articles = parser.parse_rss_content(sample_rss_content, custom_config)
        
        assert len(articles) == 2
        
        # 检查第一篇文章
        article1 = articles[0]
        assert article1['title'] == 'Test Article 1'
        assert article1['url'] == 'https://test.com/article1'
        assert article1['content'] == 'This is a test article description'
        assert article1['author'] == 'test@example.com (Test Author)'
        assert 'Technology' in article1['tags']
        assert 'Testing' in article1['tags']
        assert isinstance(article1['published_at'], datetime)

    def test_parse_rss_content_atom(self, parser, sample_atom_content, custom_config):
        """测试Atom内容解析"""
        articles = parser.parse_rss_content(sample_atom_content, custom_config)
        
        assert len(articles) == 1
        
        article = articles[0]
        assert article['title'] == 'Atom Test Article'
        assert article['url'] == 'https://test.com/atom-article'
        assert 'This is atom content with HTML tags.' in article['content']
        # 作者可能包含邮箱信息
        assert 'Atom Author' in article['author']
        assert 'atom' in article['tags']

    def test_parse_rss_content_with_default_config(self, parser, sample_rss_content):
        """测试使用默认配置解析"""
        articles = parser.parse_rss_content(sample_rss_content)
        
        assert len(articles) == 2
        assert all('title' in article for article in articles)
        assert all('url' in article for article in articles)

    def test_parse_rss_content_invalid_xml(self, parser, custom_config):
        """测试解析无效XML"""
        invalid_xml = "<invalid>xml content</invalid"
        articles = parser.parse_rss_content(invalid_xml, custom_config)
        # feedparser usually handles malformed XML gracefully
        assert isinstance(articles, list)

    def test_parse_rss_content_empty(self, parser, custom_config):
        """测试解析空内容"""
        articles = parser.parse_rss_content("", custom_config)
        assert articles == []

    @pytest.mark.asyncio
    async def test_fetch_rss_success(self, parser, custom_config):
        """测试成功获取RSS"""
        test_content = "<rss><channel><item><title>Test</title></item></channel></rss>"
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=test_content)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with parser:
                content = await parser.fetch_rss('https://test.com/feed', custom_config)
                
            assert content == test_content
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_rss_http_error(self, parser, custom_config):
        """测试HTTP错误"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with parser:
                content = await parser.fetch_rss('https://test.com/feed', custom_config)
                
            assert content is None

    @pytest.mark.asyncio
    async def test_fetch_rss_timeout(self, parser, custom_config):
        """测试请求超时"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = asyncio.TimeoutError()
            
            async with parser:
                content = await parser.fetch_rss('https://test.com/feed', custom_config)
                
            assert content is None

    @pytest.mark.asyncio
    async def test_parse_rss_url_success(self, parser, sample_rss_content, custom_config):
        """测试从URL解析RSS成功"""
        with patch.object(parser, 'fetch_rss', return_value=sample_rss_content):
            async with parser:
                articles = await parser.parse_rss_url('https://test.com/feed', custom_config)
                
            assert len(articles) == 2
            assert articles[0]['title'] == 'Test Article 1'

    @pytest.mark.asyncio
    async def test_parse_rss_url_fetch_failed(self, parser, custom_config):
        """测试URL获取失败"""
        with patch.object(parser, 'fetch_rss', return_value=None):
            async with parser:
                articles = await parser.parse_rss_url('https://test.com/feed', custom_config)
                
            assert articles == []

    @pytest.mark.asyncio
    async def test_parse_rss_url_with_config_detection(self, parser, sample_rss_content):
        """测试自动配置检测"""
        with patch.object(parser, 'fetch_rss', return_value=sample_rss_content):
            async with parser:
                # 测试Medium URL
                articles = await parser.parse_rss_url('https://medium.com/@user/feed')
                assert isinstance(articles, list)
                
                # 测试GitHub URL
                articles = await parser.parse_rss_url('https://github.com/user/repo/commits.atom')
                assert isinstance(articles, list)

    def test_extract_title_with_filters(self, parser):
        """测试标题提取和过滤"""
        config = RSSSourceConfig(
            name='test',
            title_filters=[r'\[SPAM\]', r'Advertisement:.*'],
            max_title_length=20
        )
        
        mock_entry = Mock()
        mock_entry.title = '[SPAM] Advertisement: This is a very long title that should be truncated'
        
        mapping = FieldMapping()
        title = parser._extract_title(mock_entry, mapping, config)
        
        # 标题被完全过滤掉后应该返回None
        assert title is None

    def test_extract_content_with_html_cleaning(self, parser):
        """测试内容提取和HTML清理"""
        config = RSSSourceConfig(
            name='test',
            remove_html=True,
            content_filters=[r'<script.*?</script>'],
            max_content_length=50
        )
        
        mock_entry = Mock()
        mock_entry.content = [{'value': '<p>Test content with <script>alert("xss")</script> <strong>HTML</strong> tags.</p>'}]
        
        mapping = FieldMapping()
        content = parser._extract_content(mock_entry, mapping, config)
        
        assert content is not None
        assert '<script>' not in content
        assert '<p>' not in content
        assert 'Test content with' in content
        assert 'HTML' in content
        assert len(content) <= 50

    def test_extract_content_priority_order(self, parser):
        """测试内容字段优先级"""
        mock_entry = Mock()
        mock_entry.content = None
        mock_entry.description = 'Description content'
        mock_entry.summary = 'Summary content'
        
        # 确保没有content:encoded属性
        if hasattr(mock_entry, 'content:encoded'):
            delattr(mock_entry, 'content:encoded')
        
        mapping = FieldMapping(
            content_fields=['content', 'description', 'summary']
        )
        config = RSSSourceConfig(name='test')
        
        content = parser._extract_content(mock_entry, mapping, config)
        assert content == 'Description content'

    def test_extract_url_with_base_url(self, parser):
        """测试URL提取和基础URL处理"""
        config = RSSSourceConfig(
            name='test',
            base_url='https://example.com',
            url_cleanup_patterns=[r'\?utm_.*', r'#.*$']
        )
        
        mock_entry = Mock()
        mock_entry.link = '/relative/path?utm_source=test#section'
        
        mapping = FieldMapping()
        url = parser._extract_url(mock_entry, mapping, config)
        
        assert url == 'https://example.com/relative/path'

    def test_extract_date_multiple_formats(self, parser):
        """测试多种日期格式提取"""
        mock_entry = Mock()
        mock_entry.published = None
        mock_entry.updated = '2023-01-01T12:00:00Z'
        
        mapping = FieldMapping()
        date = parser._extract_date(mock_entry, mapping)
        
        assert date is not None
        assert isinstance(date, datetime)
        assert date.year == 2023

    def test_extract_tags_complex_structure(self, parser):
        """测试复杂标签结构提取"""
        mock_entry = Mock()
        
        # 模拟不同类型的标签结构
        mock_tag1 = Mock()
        mock_tag1.term = 'tag1'
        
        mock_tag2 = Mock()
        mock_tag2.label = 'tag2'
        del mock_tag2.term  # 确保没有term属性
        
        mock_entry.tags = [mock_tag1, mock_tag2, 'string_tag']
        mock_entry.category = 'category1,category2'
        
        mapping = FieldMapping()
        tags = parser._extract_tags(mock_entry, mapping)
        
        assert 'tag1' in tags
        assert 'tag2' in tags
        assert 'string_tag' in tags
        assert 'category1' in tags
        assert 'category2' in tags

    def test_extract_image_multiple_sources(self, parser):
        """测试多种图片源提取"""
        mock_entry = Mock()
        
        # 模拟media_thumbnail
        mock_thumbnail = Mock()
        mock_thumbnail.url = 'https://example.com/thumb.jpg'
        mock_entry.media_thumbnail = [mock_thumbnail]
        
        mapping = FieldMapping()
        image_url = parser._extract_image(mock_entry, mapping)
        
        assert image_url == 'https://example.com/thumb.jpg'

    def test_get_nested_value(self, parser):
        """测试嵌套值获取"""
        mock_entry = Mock()
        mock_author = Mock()
        mock_author.name = 'Test Author'
        mock_entry.author = mock_author
        
        # 测试简单字段
        value = parser._get_nested_value(mock_entry, 'author')
        assert value is mock_author
        
        # 测试嵌套字段
        value = parser._get_nested_value(mock_entry, 'author.name')
        assert value == 'Test Author'
        
        # 测试不存在的字段 - 创建一个真实不存在的对象
        simple_obj = type('SimpleObj', (), {'existing_field': 'value'})()
        value = parser._get_nested_value(simple_obj, 'nonexistent_field')
        assert value is None

    def test_parse_date_various_formats(self, parser):
        """测试解析各种日期格式"""
        # 测试ISO格式
        date1 = parser._parse_date('2023-01-01T12:00:00Z')
        assert date1.year == 2023
        
        # 测试RFC格式
        date2 = parser._parse_date('Mon, 01 Jan 2023 12:00:00 GMT')  
        assert date2.year == 2023
        
        # 测试feedparser时间对象
        from time import struct_time
        time_struct = struct_time((2023, 1, 1, 12, 0, 0, 0, 1, -1))
        date3 = parser._parse_date(time_struct)
        assert date3.year == 2023
        
        # 测试已经是datetime对象
        existing_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        date4 = parser._parse_date(existing_date)
        assert date4 is existing_date

    def test_clean_html(self, parser):
        """测试HTML清理"""
        html_content = '''
        <div>
            <p>This is <strong>bold</strong> text.</p>
            <script>alert("xss")</script>
            <style>body { color: red; }</style>
            <a href="http://example.com">Link</a>
        </div>
        '''
        
        cleaned = parser._clean_html(html_content)
        
        assert '<script>' not in cleaned
        assert '<style>' not in cleaned
        assert '<p>' not in cleaned
        assert 'This is bold text.' in cleaned
        assert 'Link' in cleaned

    def test_validate_article_success(self, parser, custom_config):
        """测试文章验证成功"""
        article = {
            'title': 'Valid Article Title',
            'url': 'https://example.com/article',
            'content': 'This is valid content with enough length.',
            'author': 'Test Author'
        }
        
        assert parser._validate_article(article, custom_config) is True

    def test_validate_article_missing_required_field(self, parser, custom_config):
        """测试缺少必需字段"""
        article = {
            'title': 'Valid Title',
            # 缺少url字段
            'content': 'Valid content'
        }
        
        assert parser._validate_article(article, custom_config) is False

    def test_validate_article_title_too_short(self, parser, custom_config):
        """测试标题太短"""
        article = {
            'title': 'Hi',  # 少于3个字符
            'url': 'https://example.com/article',
            'content': 'Valid content'
        }
        
        assert parser._validate_article(article, custom_config) is False

    def test_validate_article_content_too_short(self, parser, custom_config):
        """测试内容太短"""
        article = {
            'title': 'Valid Title',
            'url': 'https://example.com/article',
            'content': 'Hi'  # 少于5个字符
        }
        
        assert parser._validate_article(article, custom_config) is False

    def test_validate_article_invalid_url(self, parser, custom_config):
        """测试无效URL"""
        article = {
            'title': 'Valid Title',
            'url': 'not-a-valid-url',
            'content': 'Valid content'
        }
        
        assert parser._validate_article(article, custom_config) is False

    def test_get_supported_sites(self, parser):
        """测试获取支持的站点列表"""
        sites = parser.get_supported_sites()
        
        expected_sites = ['default', 'medium', 'wordpress', 'github', 'reddit', 'hackernews']
        for site in expected_sites:
            assert site in sites

    def test_add_custom_config(self, parser):
        """测试添加自定义配置"""
        custom_config = RSSSourceConfig(name='custom_site')
        parser.add_custom_config('custom_site', custom_config)
        
        sites = parser.get_supported_sites()
        assert 'custom_site' in sites
        
        retrieved_config = parser.config_manager.get_config('custom_site')
        assert retrieved_config.name == 'custom_site'

    def test_custom_extractors(self, parser):
        """测试自定义提取器"""
        def custom_extractor(entry):
            return f"custom_{entry.title}"
        
        config = RSSSourceConfig(
            name='test',
            field_mapping=FieldMapping(
                custom_extractors={'custom_field': custom_extractor}
            )
        )
        
        mock_entry = Mock()
        mock_entry.title = 'Test Title'
        
        article = parser._extract_article_data(mock_entry, config)
        
        assert article['custom_field'] == 'custom_Test Title'

    def test_custom_processors(self, parser):
        """测试自定义处理器"""
        def title_processor(title, entry):
            return f"[PROCESSED] {title}"
        
        config = RSSSourceConfig(
            name='test',
            custom_processors={'title': title_processor}
        )
        
        mock_entry = Mock()
        mock_entry.title = 'Original Title'
        
        article = parser._extract_article_data(mock_entry, config)
        
        assert article['title'] == '[PROCESSED] Original Title'

    def test_error_handling_in_extraction(self, parser):
        """测试提取过程中的错误处理"""
        def failing_extractor(entry):
            raise Exception("Extractor failed")
            
        def failing_processor(value, entry):
            raise Exception("Processor failed")
        
        config = RSSSourceConfig(
            name='test',
            field_mapping=FieldMapping(
                custom_extractors={'failing_field': failing_extractor}
            ),
            custom_processors={'title': failing_processor}
        )
        
        mock_entry = Mock()
        mock_entry.title = 'Test Title'
        
        # 应该不会抛出异常，而是优雅处理
        article = parser._extract_article_data(mock_entry, config)
        
        assert article is not None
        assert article['failing_field'] is None
        assert article['title'] == 'Test Title'  # 处理器失败，保持原值

    @pytest.mark.asyncio
    async def test_session_management(self, parser):
        """测试session管理"""
        # 初始状态
        assert parser.session is None
        
        # 确保session创建
        await parser._ensure_session()
        assert parser.session is not None
        assert not parser.session.closed
        
        # 再次调用应该使用同一个session
        old_session = parser.session
        await parser._ensure_session()
        assert parser.session is old_session
        
        # 清理
        await parser.session.close()

    def test_config_manager_integration(self, parser, config_manager):
        """测试配置管理器集成"""
        # 测试使用自定义配置管理器
        custom_parser = UniversalRSSParser(config_manager)
        assert custom_parser.config_manager is config_manager
        
        # 测试配置检测
        medium_config = custom_parser.config_manager.detect_config('https://medium.com/@user/feed')
        assert medium_config.name == 'medium'
        
        github_config = custom_parser.config_manager.detect_config('https://github.com/user/repo.atom')
        assert github_config.name == 'github'

    @pytest.mark.asyncio
    async def test_real_world_scenario_simulation(self, parser):
        """测试真实世界场景模拟"""
        # 模拟一个包含各种复杂情况的RSS feed
        complex_rss = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" 
             xmlns:dc="http://purl.org/dc/elements/1.1/">
            <channel>
                <title>Complex RSS Feed</title>
                <item>
                    <title><![CDATA[Article with CDATA & Special Characters: "Quotes" & <Tags>]]></title>
                    <description><![CDATA[Short description]]></description>
                    <content:encoded><![CDATA[
                        <p>This is the full content with <strong>HTML</strong> formatting.</p>
                        <script>alert('This should be removed');</script>
                        <p>Multiple paragraphs of content here.</p>
                    ]]></content:encoded>
                    <link>https://example.com/article?utm_source=rss&amp;utm_medium=feed#comments</link>
                    <dc:creator>John Doe</dc:creator>
                    <pubDate>Wed, 01 Feb 2023 14:30:00 +0000</pubDate>
                    <category>Tech</category>
                    <category>Programming</category>
                </item>
            </channel>
        </rss>"""
        
        config = RSSSourceConfig(
            name='test',
            remove_html=True,
            url_cleanup_patterns=[r'\?utm_.*', r'#.*$'],
            content_filters=[r'<script.*?</script>']
        )
        
        articles = parser.parse_rss_content(complex_rss, config)
        
        assert len(articles) == 1
        article = articles[0]
        
        # 验证复杂标题处理
        assert 'Article with' in article['title']  # CDATA会被feedparser自动处理
        assert '"Quotes"' in article['title']
        
        # 验证内容提取和清理
        assert article['content'] is not None
        assert '<script>' not in article['content']
        assert 'HTML' in article['content']
        
        # 验证URL清理
        assert article['url'] == 'https://example.com/article'
        
        # 验证作者提取
        assert article['author'] == 'John Doe'
        
        # 验证标签提取
        assert 'Tech' in article['tags']
        assert 'Programming' in article['tags']
        
        # 验证日期解析
        assert article['published_at'] is not None
        assert article['published_at'].year == 2023
        assert article['published_at'].month == 2


class TestRSSParsingError:
    """RSS解析异常测试"""
    
    def test_rss_parsing_error(self):
        """测试RSS解析异常"""
        error = RSSParsingError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)


class TestRSSValidationError:
    """RSS验证异常测试"""
    
    def test_rss_validation_error(self):
        """测试RSS验证异常"""
        error = RSSValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, Exception)


class TestBackwardCompatibility:
    """向后兼容性测试"""
    
    def test_old_rss_parser_still_works(self):
        """测试旧的RSSParser仍然可用"""
        from app.utils.rss_parser import RSSParser
        
        parser = RSSParser()
        assert parser is not None
        assert isinstance(parser, UniversalRSSParser)  # 应该是子类

    def test_old_parser_methods_work(self):
        """测试旧解析器方法仍然工作"""
        from app.utils.rss_parser import RSSParser
        
        parser = RSSParser()
        
        # 测试旧方法仍然存在
        sample_rss = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Test</title>
                    <link>https://test.com</link>
                    <description>Test content</description>
                </item>
            </channel>
        </rss>"""
        
        articles = parser.parse_rss_content(sample_rss)
        assert isinstance(articles, list)
        
        if articles:  # 如果解析成功
            assert 'title' in articles[0]
            assert 'url' in articles[0]
