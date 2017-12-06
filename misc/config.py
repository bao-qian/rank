import os

user_query_and_count = [
    ('location:china followers:>200', 1000),
    ('location:china followers:100..200', 1000),
    ('location:PRC followers:>=100', 1000),
]
count_per_request = 100
cache_time = 36000

root = os.path.dirname(os.path.dirname(__file__))
static = os.path.join(root, 'static')
misc = os.path.join(root, 'misc')
template = os.path.join(root, 'template')

extra_user = [
    'guaxiao',
    'vczh',
    'JeffreyZhao',
]

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
    'leetcode',
    'study',
    'tips',
    '学习笔记',
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