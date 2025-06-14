"""
RSS解析配置管理
"""
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum


class ContentType(Enum):
    """内容类型枚举"""
    TITLE = "title"
    CONTENT = "content"
    SUMMARY = "summary"
    AUTHOR = "author"
    LINK = "link"
    PUBLISHED = "published"
    TAGS = "tags"
    IMAGE = "image"


@dataclass
class FieldMapping:
    """字段映射配置"""
    # 基础字段映射 - 按优先级排序
    title_fields: List[str] = field(default_factory=lambda: ['title'])
    content_fields: List[str] = field(default_factory=lambda: [
        'content', 'content:encoded', 'description', 'summary'
    ])
    author_fields: List[str] = field(default_factory=lambda: [
        'author', 'author_detail.name', 'dc:creator', 'creator'
    ])
    link_fields: List[str] = field(default_factory=lambda: [
        'link', 'links.0.href', 'id'
    ])
    published_fields: List[str] = field(default_factory=lambda: [
        'published', 'published_parsed', 'updated', 'updated_parsed', 'pubDate'
    ])
    tags_fields: List[str] = field(default_factory=lambda: [
        'tags', 'category', 'categories', 'keywords'
    ])
    image_fields: List[str] = field(default_factory=lambda: [
        'media_thumbnail', 'media_content', 'enclosures', 'image', 'media:thumbnail'
    ])
    
    # 自定义提取器函数
    custom_extractors: Dict[str, Callable[[Any], Any]] = field(default_factory=dict)


@dataclass 
class RSSSourceConfig:
    """RSS源配置"""
    name: str
    url: str = ""
    
    # 编码和请求配置
    encoding: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    
    # 字段映射
    field_mapping: Optional[FieldMapping] = None
    
    # 内容处理配置
    remove_html: bool = True
    max_content_length: Optional[int] = None
    max_title_length: Optional[int] = 200
    
    # 内容过滤器 - 正则表达式列表
    content_filters: List[str] = field(default_factory=lambda: [
        r'<script.*?</script>',  # 移除脚本
        r'<style.*?</style>',    # 移除样式
        r'<!--.*?-->',           # 移除注释
    ])
    title_filters: List[str] = field(default_factory=list)
    
    # URL处理
    base_url: Optional[str] = None  # 用于相对链接转换
    url_cleanup_patterns: List[str] = field(default_factory=lambda: [
        r'\?utm_.*',  # 移除UTM参数
        r'#.*$',      # 移除锚点
    ])
    
    # 自定义处理器
    custom_processors: Dict[str, Callable[[str, Any], str]] = field(default_factory=dict)
    
    # 验证规则
    required_fields: List[str] = field(default_factory=lambda: ['title', 'url'])
    min_title_length: int = 5
    min_content_length: int = 10


class RSSConfigManager:
    """RSS配置管理器"""
    
    def __init__(self):
        self.configs = self._create_default_configs()
    
    def _create_default_configs(self) -> Dict[str, RSSSourceConfig]:
        """创建默认配置"""
        return {
            'default': RSSSourceConfig(
                name='default',
                field_mapping=FieldMapping()
            ),
            
            'medium': RSSSourceConfig(
                name='medium',
                field_mapping=FieldMapping(
                    content_fields=['content:encoded', 'description'],
                    author_fields=['dc:creator', 'author'],
                    published_fields=['pubDate', 'published'],
                    custom_extractors={
                        'reading_time': lambda entry: self._estimate_reading_time(
                            entry.get('description', '') or entry.get('content', '')
                        )
                    }
                ),
                content_filters=[
                    r'<script.*?</script>',
                    r'<iframe.*?</iframe>',
                    r'Medium is an open platform.*',
                ],
                max_content_length=3000
            ),
            
            'wordpress': RSSSourceConfig(
                name='wordpress',
                field_mapping=FieldMapping(
                    content_fields=['content:encoded', 'description', 'content'],
                    author_fields=['dc:creator', 'author'],
                    tags_fields=['category', 'tags', 'dc:subject']
                ),
                content_filters=[
                    r'<script.*?</script>',
                    r'<div class="wp-.*?</div>',
                    r'The post .* appeared first on.*',
                ]
            ),
            
            'github': RSSSourceConfig(
                name='github',
                field_mapping=FieldMapping(
                    content_fields=['content', 'summary'],
                    author_fields=['author.name', 'author'],
                    link_fields=['link.href', 'link'],
                    custom_extractors={
                        'repository': lambda entry: self._extract_github_repo(entry.get('link', '')),
                        'event_type': lambda entry: self._extract_github_event_type(entry.get('title', ''))
                    }
                )
            ),
            
            'reddit': RSSSourceConfig(
                name='reddit',
                field_mapping=FieldMapping(
                    content_fields=['content', 'description'],
                    author_fields=['author'],
                    custom_extractors={
                        'subreddit': lambda entry: self._extract_subreddit(entry.get('link', '')),
                        'score': lambda entry: self._extract_reddit_score(entry.get('title', ''))
                    }
                ),
                content_filters=[
                    r'submitted by.*to r/',
                    r'\[link\].*\[comments\]',
                ]
            ),
            
            'hackernews': RSSSourceConfig(
                name='hackernews',
                field_mapping=FieldMapping(
                    content_fields=['description', 'summary'],
                    author_fields=[],  # HN 通常不提供作者信息
                    custom_extractors={
                        'points': lambda entry: self._extract_hn_points(entry.get('description', '')),
                        'comments_count': lambda entry: self._extract_hn_comments(entry.get('description', ''))
                    }
                ),
                max_content_length=500
            )
        }
    
    def get_config(self, source_name: str) -> RSSSourceConfig:
        """获取配置"""
        import copy
        config = self.configs.get(source_name, self.configs['default'])
        return copy.deepcopy(config)
    
    def detect_config(self, url: str) -> RSSSourceConfig:
        """根据URL自动检测配置"""
        url_lower = url.lower()
        
        if 'medium.com' in url_lower:
            return self.configs['medium']
        elif any(wp in url_lower for wp in ['wordpress', 'wp-content', 'wp-json']):
            return self.configs['wordpress']
        elif 'github.com' in url_lower:
            return self.configs['github']
        elif 'reddit.com' in url_lower:
            return self.configs['reddit']
        elif 'news.ycombinator.com' in url_lower:
            return self.configs['hackernews']
        else:
            return self.configs['default']
    
    def add_config(self, name: str, config: RSSSourceConfig):
        """添加自定义配置"""
        self.configs[name] = config
    
    def _estimate_reading_time(self, content: str) -> int:
        """估算阅读时间（分钟）"""
        if not content:
            return 1
        word_count = len(content.split())
        return max(1, word_count // 200)  # 假设每分钟200字
    
    def _extract_github_repo(self, link: str) -> Optional[str]:
        """从GitHub链接提取仓库名"""
        match = re.search(r'github\.com/([^/]+/[^/]+)', link)
        return match.group(1) if match else None
    
    def _extract_github_event_type(self, title: str) -> Optional[str]:
        """提取GitHub事件类型"""
        if 'pushed' in title.lower():
            return 'push'
        elif 'created' in title.lower():
            return 'create'
        elif 'opened' in title.lower():
            return 'issue_or_pr'
        return 'other'
    
    def _extract_subreddit(self, link: str) -> Optional[str]:
        """从Reddit链接提取subreddit"""
        match = re.search(r'reddit\.com/r/([^/]+)', link)
        return match.group(1) if match else None
    
    def _extract_reddit_score(self, title: str) -> Optional[int]:
        """提取Reddit分数"""
        match = re.search(r'\[(\d+)\]', title)
        return int(match.group(1)) if match else None
    
    def _extract_hn_points(self, description: str) -> Optional[int]:
        """提取HackerNews点数"""
        match = re.search(r'(\d+) points?', description)
        return int(match.group(1)) if match else None
    
    def _extract_hn_comments(self, description: str) -> Optional[int]:
        """提取HackerNews评论数"""
        match = re.search(r'(\d+) comments?', description)
        return int(match.group(1)) if match else None
