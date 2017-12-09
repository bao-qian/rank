import os

import time

import config

root = os.path.dirname(os.path.dirname(__file__))
static = os.path.join(root, 'static')
misc = os.path.join(root, 'misc')
template = os.path.join(root, 'template')


block_user = [
    'diwu',
    'xuzhezhaozhao',
    'rover12421',
    'tiankonguse',
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
    'self-taught',
    'self taught',
    'study',
    'tips',
    '学习笔记',
    '读书笔记',
    '学习资源',
    '开发实战',
    '交流群',
    '学习群',
    '自学',
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
