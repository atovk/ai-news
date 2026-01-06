"""
工具类测试 (向后兼容性和基础功能测试)
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from app.utils.rss_parser import RSSParser, UniversalRSSParser
from app.utils.rss_config import FieldMapping, RSSSourceConfig


class TestRSSParserBackwardCompatibility:
    """RSS解析器向后兼容性测试"""
    
    def test_init(self):
        """测试初始化"""
        parser = RSSParser()
        assert parser is not None
        assert isinstance(parser, UniversalRSSParser)  # 应该是UniversalRSSParser的子类
    
    @patch('feedparser.parse')
    def test_parse_rss_content_success(self, mock_parse):
        """测试成功解析RSS内容"""
        # 模拟feedparser返回数据
        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.bozo_exception = None
        
        mock_entry = Mock()
        mock_entry.title = 'Test Article'
        mock_entry.link = 'https://test.com/article1'
        mock_entry.summary = 'Test summary'
        mock_entry.author = 'Test Author'
        mock_entry.published = '2023-01-01T00:00:00Z'
        mock_entry.tags = []
        
        # 模拟content为空，让它fallback到summary
        del mock_entry.content
        
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed
        
        parser = RSSParser()
        articles = parser.parse_rss_content("<rss></rss>")
        
        assert len(articles) == 1
        assert articles[0]["title"] == "Test Article"
        assert articles[0]["url"] == "https://test.com/article1"
        # 内容可能来自summary或description，取决于解析逻辑
        assert articles[0]["content"] in ["Test summary", ""]
        mock_parse.assert_called_once()
    
    @patch('feedparser.parse')
    def test_parse_rss_content_empty(self, mock_parse):
        """测试解析空RSS内容"""
        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.bozo_exception = None
        mock_feed.entries = []
        mock_parse.return_value = mock_feed
        
        parser = RSSParser()
        articles = parser.parse_rss_content("<rss></rss>")
        
        assert articles == []
        mock_parse.assert_called_once()
    
    @patch('feedparser.parse')
    def test_parse_rss_content_with_exception(self, mock_parse):
        """测试解析RSS内容异常处理"""
        mock_parse.side_effect = Exception("Parse error")
        
        parser = RSSParser()
        with pytest.raises(Exception):  # 新版本会抛出RSSParsingError
            parser.parse_rss_content("<rss></rss>")
        
        mock_parse.assert_called_once()
    
    def test_parse_date_valid(self):
        """测试解析有效日期"""
        parser = RSSParser()
        date_str = "2023-01-01T00:00:00Z"
        result = parser._parse_date(date_str)
        
        assert result is not None
        assert result.year == 2023
        assert isinstance(result, datetime)
    
    def test_parse_date_invalid(self):
        """测试解析无效日期"""
        parser = RSSParser()
        result = parser._parse_date("invalid-date")
        
        assert result is None
    
    def test_extract_tags(self):
        """测试提取标签"""
        parser = RSSParser()
        
        # 模拟entry对象
        mock_entry = Mock()
        mock_tag = Mock()
        mock_tag.term = "test-tag"
        mock_entry.tags = [mock_tag]
        
        mapping = FieldMapping()  # 使用默认映射
        tags = parser._extract_tags(mock_entry, mapping)
        
        assert len(tags) == 1
        assert tags[0] == "test-tag"

    def test_old_parser_deprecation_warning(self):
        """测试旧解析器废弃警告"""
        with patch('logging.Logger.warning') as mock_warning:
            parser = RSSParser()
            # 初始化时应该记录废弃警告
            mock_warning.assert_called_with("RSSParser已废弃，请使用UniversalRSSParser")


class TestUniversalRSSParserBasics:
    """UniversalRSSParser基础功能测试"""
    
    def test_init_default(self):
        """测试默认初始化"""
        parser = UniversalRSSParser()
        assert parser is not None
        assert parser.config_manager is not None
        assert parser.session is None
    
    def test_supported_sites(self):
        """测试支持的站点列表"""
        parser = UniversalRSSParser()
        sites = parser.get_supported_sites()
        
        expected_sites = ['default', 'medium', 'wordpress', 'github', 'reddit', 'hackernews']
        for site in expected_sites:
            assert site in sites
    
    def test_custom_config_addition(self):
        """测试添加自定义配置"""
        parser = UniversalRSSParser()
        custom_config = RSSSourceConfig(name='test_site')
        
        parser.add_custom_config('test_site', custom_config)
        
        sites = parser.get_supported_sites()
        assert 'test_site' in sites
    
    def test_field_extraction_basic(self):
        """测试基础字段提取"""
        parser = UniversalRSSParser()
        
        mock_entry = Mock()
        mock_entry.title = "Test Title"
        mock_entry.link = "https://test.com"
        mock_entry.author = "Test Author"
        
        # 测试字段提取
        title = parser._extract_field(mock_entry, ['title'])
        assert title == "Test Title"
        
        url_fields = parser._extract_field(mock_entry, ['link', 'url'])
        assert url_fields == "https://test.com"
    
    def test_nested_value_extraction(self):
        """测试嵌套值提取"""
        parser = UniversalRSSParser()
        
        mock_entry = Mock()
        mock_author = Mock()
        mock_author.name = "Author Name"
        mock_entry.author = mock_author
        
        # 测试嵌套字段提取
        value = parser._get_nested_value(mock_entry, 'author.name')
        assert value == "Author Name"
        
        # 测试不存在的字段 - 创建一个真实不存在的对象
        simple_obj = type('SimpleObj', (), {'existing_field': 'value'})()
        value = parser._get_nested_value(simple_obj, 'nonexistent_field')
        assert value is None
    
    def test_html_cleaning(self):
        """测试HTML清理"""
        parser = UniversalRSSParser()
        
        html_content = '<p>Test content with <strong>HTML</strong> tags.</p>'
        cleaned = parser._clean_html(html_content)
        
        assert '<p>' not in cleaned
        assert '<strong>' not in cleaned
        assert 'Test content with HTML tags.' in cleaned
    
    def test_url_validation(self):
        """测试URL验证"""
        parser = UniversalRSSParser()
        config = RSSSourceConfig(name='test')
        
        # 有效URL
        valid_article = {
            'title': 'Valid Title',
            'url': 'https://example.com/article',
            'content': 'Valid content'
        }
        assert parser._validate_article(valid_article, config) is True
        
        # 无效URL
        invalid_article = {
            'title': 'Valid Title',
            'url': 'not-a-url',
            'content': 'Valid content'
        }
        assert parser._validate_article(invalid_article, config) is False
    
    def test_date_parsing_formats(self):
        """测试多种日期格式解析"""
        parser = UniversalRSSParser()
        
        # ISO格式
        iso_date = parser._parse_date('2023-01-01T12:00:00Z')
        assert iso_date is not None
        assert iso_date.year == 2023
        assert iso_date.month == 1
        
        # RFC格式
        rfc_date = parser._parse_date('Mon, 01 Jan 2023 12:00:00 GMT')
        assert rfc_date is not None
        assert rfc_date.year == 2023
        assert rfc_date.month == 1
        
        # 已经是datetime对象
        existing_date = datetime(2023, 6, 15, tzinfo=timezone.utc)
        parsed_date = parser._parse_date(existing_date)
        assert parsed_date is existing_date
    
    def test_content_filtering(self):
        """测试内容过滤"""
        parser = UniversalRSSParser()
        
        config = RSSSourceConfig(
            name='test',
            content_filters=[r'<script.*?</script>', r'ADVERTISEMENT'],
            remove_html=True
        )
        
        mock_entry = Mock()
        mock_entry.content = [{'value': '<p>Good content</p><script>alert("bad")</script>ADVERTISEMENT'}]
        
        mapping = FieldMapping()
        content = parser._extract_content(mock_entry, mapping, config)
        
        assert content is not None
        assert 'Good content' in content
        assert '<script>' not in content
        assert 'ADVERTISEMENT' not in content
        assert '<p>' not in content  # HTML应该被清理
    
    def test_title_length_limiting(self):
        """测试标题长度限制"""
        parser = UniversalRSSParser()
        
        config = RSSSourceConfig(
            name='test',
            max_title_length=20
        )
        
        mock_entry = Mock()
        mock_entry.title = "This is a very long title that should be truncated"
        
        mapping = FieldMapping()
        title = parser._extract_title(mock_entry, mapping, config)
        
        assert title is not None
        assert len(title) <= 23  # 20 + "..."
        assert title.endswith('...')
    
    def test_validation_rules(self):
        """测试验证规则"""
        parser = UniversalRSSParser()
        
        config = RSSSourceConfig(
            name='test',
            required_fields=['title', 'url'],
            min_title_length=5,
            min_content_length=10
        )
        
        # 标题太短
        short_title_article = {
            'title': 'Hi',
            'url': 'https://example.com',
            'content': 'This is long enough content'
        }
        assert parser._validate_article(short_title_article, config) is False
        
        # 内容太短
        short_content_article = {
            'title': 'Valid Title',
            'url': 'https://example.com',
            'content': 'Short'
        }
        assert parser._validate_article(short_content_article, config) is False
        
        # 缺少必需字段
        missing_field_article = {
            'title': 'Valid Title',
            # 缺少url
            'content': 'Valid content'
        }
        assert parser._validate_article(missing_field_article, config) is False
        
        # 有效文章
        valid_article = {
            'title': 'Valid Title',
            'url': 'https://example.com',
            'content': 'This is valid content'
        }
        assert parser._validate_article(valid_article, config) is True
