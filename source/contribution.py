import time

from requests import HTTPError

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
        except HTTPError:
            cs = []

        # only for last x year
        past = int(time.time()) - int(365 * 24 * 3600 * config.contribution_year)
        for c in cs:
            author = c['author']
            # https://api.github.com/repos/iview/iview/stats/contributors
            # author may be null
            if author is not None:
                _login = c['author']['login']
                weeks = c['weeks']
                for w in weeks:
                    week_start = int(w['w'])
                    if week_start > past and w['c'] > 0:
                        self.total_commit += w['c']
                        if _login == self.login:
                            self.commit += w['c']

    def add_star(self):
        self.rate = self.commit / self.total_commit
        self.star = int(self.repository.start_count * self.rate)

    def validate(self):
        self.repository.validate()
        if self.repository.valid:
            log('valid code repo', self.repository.name_with_owner)
            self.add_commit()
            # at least x commit
            if self.login == self.repository.owner and self.commit > 3:
                self.valid = True
            elif self.login != self.repository.owner and self.commit > 1:
                self.valid = True
            else:
                self.valid = False

            if not self.valid:
                self.all_invalid.append(
                    (self.repository.name_with_owner, self.commit, self.total_commit)
                )

    @classmethod
    def all(cls, login, repositories):
        for r in repositories:
            c = Contribution(login, r)
            c.validate()
            if c.valid:
                c.add_star()
                if c.star > 0:
                    yield c
