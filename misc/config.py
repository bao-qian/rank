import os

user_query = 'location:china'
user_count = 10
count_per_request = 5

root = os.path.dirname(os.path.dirname(__file__))
static = os.path.join(root, 'static')
misc = os.path.join(root, 'misc')
template = os.path.join(root, 'template')

extra_user = [
    'happlebao',
]

invalid_language = [
    'Graphviz (DOT)',
    'MediaWiki',
    'Markdown',
    'YAML',
    'HTML',
    'Text',
    'SVG',
    'TeX',
]