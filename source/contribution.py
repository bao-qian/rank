import time

from source.exception import ErrorCode
from misc import config
from source.model import Model
from source.repository import Repository
from source.utility import log
from source.api import API


class Contribution(Model):
    all_invalid = []

    def __init__(self, login, repository):
        self.repository = repository
        self.star = 0
        self.commit = 0
        self.total_commit = 0
        self.rate = 0
        self.login = login
        self.valid = False

    def add_commit(self):
        q = Repository.query_for_contributors(self.repository.name_with_owner)

        try:
            cs = API.get_v3(q)
        except ErrorCode:
            cs = []

        # only for last x year
        for c in cs:
            author = c['author']
            # https://api.github.com/repos/iview/iview/stats/contributors
            # author may be null
            if author is not None:
                _login = c['author']['login']
                weeks = c['weeks']
                for w in weeks:
                    week_start = int(w['w'])
                    if week_start > config.valid_from and w['c'] > 0:
                        self.total_commit += w['c']
                        if _login == self.login:
                            self.commit += w['c']

    def valid_commit(self):
        self.add_commit()
        # at least x commit
        if self.login == self.repository.owner and self.commit > 3:
            return True
        elif self.login != self.repository.owner and self.commit > 1:
            return True
        else:
            return False

    def validate(self):
        self.repository.validate()
        if self.repository.valid:
            self.repository.add_starred_at()
            log('valid code repo {} with star {}'.format(
                self.repository.name_with_owner, len(self.repository.starred_at)
            ))
            if self.valid_commit():
                self.add_star()
                if self.star > 0:
                    self.valid = True
                else:
                    self.all_invalid.append(
                        (self.repository.name_with_owner, self.commit, self.total_commit, self.star)
                    )
            else:
                self.all_invalid.append(
                    (self.repository.name_with_owner, self.commit, self.total_commit)
                )

    def add_star(self):
        self.rate = self.commit / self.total_commit
        self.star = int(len(self.repository.starred_at) * self.rate)

    @classmethod
    def all(cls, login, repositories):
        for r in repositories:
            c = Contribution(login, r)
            c.validate()
            log('contribution all', r.name_with_owner, c.valid, c.star)
            if c.valid:
                yield c
