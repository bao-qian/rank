# noinspection PyUnresolvedReferences
from misc.base_config import *
import time


user_query_and_count = [
    ('location:china followers:>200', 1),
    ('location:china followers:100..200', 1),
    ('location:PRC followers:>=100', 1),
]
count_per_request = 100
cache_time = 36000000000000000
contribution_year = 3
valid_from = int(time.time()) - int(365 * 24 * 3600 * contribution_year)

extra_user = [
    'happlebao',
    'vczh',
]

block_user = [
    'diwu',
]

