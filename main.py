import json

import config
from contribution import Contribution
from model import init_db
from repository import Repository
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
        log('user stat <{}> <{}> <{}>'.format(len(u.repositories), u.name, u.url))

    for r in Repository.invalid:
        log('invalid repository', r)
    for c in Contribution.wrong:
        log('wrong contribution', c)

    us = sorted(users, key=lambda u: u.star, reverse=True)
    for i, u in enumerate(us):
        # if len(u.contribution) > 0 and u.login not in u.contribution[0].repository.name_with_owner:
        formatted = 'user star:'
        formatted += f'{i:3} {u.login:15} {int(u.star):5} '
        for c in u.contribution[:3]:
            r = c.repository
            formatted += f'{r.name_with_owner:40} {r.language:12} {int(c.count):5} '
        log(formatted)


if __name__ == '__main__':
    main()
