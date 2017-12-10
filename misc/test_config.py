# noinspection PyUnresolvedReferences
from misc.base_config import *

user_query_and_count = [
    ('location:china followers:>200', 1),
    # ('location:china followers:100..200', 1000),
    ('location:PRC followers:>=100', 1),
]

user_per_request = 1
stargazers_per_request = 100
cache_time = 36000000000000000
contribution_year = 3

extra_user = [
    'vczh',
]
