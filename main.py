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
        users.append(u)

    s = set([])
    for e in users:
        l = len(e.repositories)
        s.add(l)
        log('user stat <{}> <{}> <{}>'.format(l, e.name, e.url))
    log('repo count', s)

    for i, e in enumerate(users):
        log('第{}个用户'.format(i, e.login))
        e.add_contribution()

    wrong_contribution = []
    cs = []
    for e in users:
        log('contribution', len(e.contribution))
        log(json.dumps(e.contribution, indent=4))
        for c in e.contribution:
            cs.append(c)
            if c[0] == 0 or c[1] is None or c[2] == 0:
                wrong_contribution.append(c)

    for e in users:
        e.calculate_star()

    us = sorted(users, key=lambda u: u.star, reverse=True)
    for i, e in enumerate(us):
        log('user star: <{}> <{}> <{}>'.format(i, e.login, e.star))

    log('wrong_contribution', wrong_contribution)


def test():
    r = API.get_v3('/users/octocat', True)
    log_dict(r)


if __name__ == '__main__':
    main()
    # test()
