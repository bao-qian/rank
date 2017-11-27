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
    users = []
    for node in r['data']['search']['edges']:
        log('log', node)
        n = node['node']
        u = User(
            n['name'],
            n['url'],
            n['pinnedRepositories'],
            n['repositories'],
        )
        users.append(u)

    for u in users:
        log('user repo', len(u.repositories))
        log(json.dumps(u.repositories, indent=4))


if __name__ == '__main__':
    main()
    # test()
