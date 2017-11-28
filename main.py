import json

from model import init_db
from user import User
from utility import (
    log_dict,
    log,
)

from api import API


def main():
    init_db()

    q = User.query_china_user()
    log('query', q)
    r = API.get_v4(q)
    log_dict(r)
    nodes = r['data']['search']['edges']
    users = User.users_from_nodes(nodes)

    s = set([])
    for u in users:
        l = len(u.repositories)
        s.add(l)
        log('user stat <{}> <{}> <{}>'.format(l, u.name, u.url))
    print('repo count', s)


if __name__ == '__main__':
    main()
    # test()
