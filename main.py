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

    users = User.all()

    for u in users:
        l = len(u.repositories)
        log('user stat <{}> <{}> <{}>'.format(l, u.name, u.url))

    wrong_contribution = []
    for u in users:
        log('contribution', len(u.contribution))
        log(json.dumps(u.contribution, indent=4))
        for c in u.contribution:
            if c[0] == 0 or c[1] is None or c[2] == 0:
                wrong_contribution.append(c)
    log('wrong_contribution', wrong_contribution)

    us = sorted(users, key=lambda u: u.star, reverse=True)
    for i, u in enumerate(us):
        log('user star: <{}> <{}> <{}>'.format(i, u.login, u.star))


if __name__ == '__main__':
    main()
