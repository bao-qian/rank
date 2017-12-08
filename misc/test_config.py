import os

user_query_and_count = [
    ('location:china followers:>200', 1),
    ('location:china followers:100..200', 1),
    ('location:PRC followers:>=100', 1),
]
count_per_request = 1
cache_time = 36000000000000000
contribution_year = 3

extra_user = [
    'vczh',
]

root = os.path.dirname(os.path.dirname(__file__))
static = os.path.join(root, 'static')
misc = os.path.join(root, 'misc')
template = os.path.join(root, 'template')

invalid_language = [
    'reStructuredText',
    'Jupyter Notebook',
    'Graphviz (DOT)',
    'MediaWiki',
    'Markdown',
    'YAML',
    'HTML',
    'Text',
    'SVG',
    'TeX',
]

invalid_description = [
    'interview',
    'tutorial',
    'study',
    'tips',
    '学习笔记',
    '读书笔记',
    '学习资源',
    '开发实战',
    '交流群',
    '学习群',
    '实战',
    '精华',
    '入门',
    '书籍',
    '教程',
    '学习',
    '系列',
    '面试',
    '集锦',
    '文章',
    '解读',
    '指南',
    '讲解',
    '全书',
]
