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
    users = list(User.users_from_nodes(nodes))

    s = set([])
    for u in users[:10]:
        l = len(u.repositories)
        s.add(l)
        log('user stat <{}> <{}> <{}>'.format(l, u.name, u.url))
    log('repo count', s)

    for u in users[:10]:
        u.add_contribution()

    wrong_contribution = []
    for u in users[:10]:
        log('contribution', len(u.contribution))
        log(json.dumps(u.contribution, indent=4))
        for c in u.contribution:
            log(c)
            if c[0] == 0:
                wrong_contribution.append(c)

    log('wrong_contribution', wrong_contribution)


def test():
    r = API.get_v3('/users/octocat', True)
    log_dict(r)


if __name__ == '__main__':
    main()
    # test()
