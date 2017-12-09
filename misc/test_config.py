# noinspection PyUnresolvedReferences
from misc.base_config import *

user_query_and_count = [
    ('location:china followers:>200', 1),
    ('location:china followers:100..200', 1),
    ('location:PRC followers:>=100', 1),
]
count_per_request = 1
cache_time = 36000000000000000
contribution_year = 3
past = int(time.time()) - int(365 * 24 * 3600 * config.contribution_year)

extra_user = [
    'vczh',
]

block_user = [
    'diwu',
]

