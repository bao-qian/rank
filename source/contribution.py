import time

from source.exception import ErrorCode, GraphQLError
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
        self.part = 4
        self.interval_length = (config.contribution_year * 365 * 24 * 3600) // self.part
        self.commit_parts = [[0, 0] for _ in range(self.part)]
        self.star_pats = [0] * self.part

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
                weeks = sorted(weeks, key=lambda _w: _w['w'], reverse=True)

                until = int(time.time()) - self.interval_length
                i = 0

                for w in weeks:
                    week_start = int(w['w'])
                    if i < self.part:
                        self.commit_parts[i][1] += w['c']
                        if _login == self.login:
                            self.commit_parts[i][0] += w['c']
                        if week_start < until:
                            i = i + 1
                            until = until - self.interval_length
                    else:
                        break

    def valid_commit(self):
        self.add_commit()
        # at least x commit
        commit = sum([p[0] for p in self.commit_parts])
        if self.login == self.repository.owner and commit > 1:
            return True
        elif self.login != self.repository.owner and commit > 0:
            return True
        else:
            return False

    def add_star(self):
        until = int(time.time()) - self.interval_length
        i = 0

        for s in self.repository.starred_at:
            if i < self.part:
                self.star_pats[i] += 1
                if s < until:
                    i = i + 1
                    until = until - self.interval_length
            else:
                break

        rate = 0
        for i in range(self.part - 1, -1, -1):
            c = self.commit_parts[i]
            if c[1] > 0:
                if c[0] > 0:
                    rate = c[0] / c[1]
                    self.star += int(self.star_pats[i] * rate)
                elif c[1] < 2:
                    self.star += int(self.star_pats[i] * rate)
                else:
                    continue
            elif c[0] == 0:
                self.star += int(self.star_pats[i] * rate)
            else:
                continue

    def validate(self):
        self.repository.validate()
        if self.repository.valid:
            if self.valid_commit():
                try:
                    self.repository.add_starred_at()
                except GraphQLError:
                    # repository(owner: "Treri", name: "angular-require") not exist
                    # probally the user changed name and github cache is not updated
                    self.all_invalid.append(
                        (self.login, self.repository.name_with_owner, self.repository.total_star)
                    )
                    return
                else:
                    self.add_star()
                    if self.star > 0:
                        self.valid = True
                    else:
                        self.all_invalid.append(
                            ('star 0', self.login, self.repository.name_with_owner, self.commit, self.total_commit,
                             self.star)
                        )
            else:
                self.all_invalid.append(
                    ('commit not valid', self.login, self.repository.name_with_owner, self.commit, self.total_commit)
                )

    @classmethod
    def all(cls, login, repositories):
        for r in repositories:
            c = Contribution(login, r)
            c.validate()
            log('contribution all <{}> <{}> <{}> <{}> <{}> <{}>'.format(
                login, r.name_with_owner, c.valid, c.star, c.commit_parts, c.star_pats
            ))
            if c.valid:
                yield c
