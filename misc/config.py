import os

user_query_and_count = [
    ('location:china followers:>200', 1000),
    ('location:china followers:100..200', 1000),
    ('location:PRC', 100),
]
count_per_request = 100
cache_time = 10800

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