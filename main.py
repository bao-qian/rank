import json

import config
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
    users = list(User.users_from_nodes(nodes))

    for e in config.extra_user:
        q = User.query_user(e)
        log('query', q)
        r = API.get_v4(q)
        log_dict(r)
        node = r['data']['user']
        u = User.user_from_node(node)
        users.insert(0, u)

    s = set([])
    for u in users:
        l = len(u.repositories)
        s.add(l)
        log('user stat <{}> <{}> <{}>'.format(l, u.name, u.url))
    log('repo count', s)

    for i, u in enumerate(users):
        log('第{}个用户'.format(i, u.login))
        u.add_contribution()

    wrong_contribution = []
    cs = []
    for u in users:
        log('contribution', len(u.contribution))
        log(json.dumps(u.contribution, indent=4))
        for c in u.contribution:
            cs.append(c)
            if c[0] == 0 or c[1] is None or c[2] == 0:
                wrong_contribution.append(c)

    for u in users[:10]:
        u.calculate_star()

    us = sorted(users, key=lambda u: u.star, reverse=True)
    for i, u in enumerate(us):
        log('user star: <{}> <{}> <{}>'.format(i, u.login, u.star))

    log('wrong_contribution', wrong_contribution)


def test():
    r = API.get_v3('/users/octocat', True)
    log_dict(r)


if __name__ == '__main__':
    main()
    # test()
