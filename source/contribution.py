import time

from repository import Repository
from requests import HTTPError
from utility import log

from api import API


class Contribution:
    all_invalid = []

    def __init__(self, login, repository):
        self.repository = repository
        self.star = 0
        self.commit = 0
        self.total_commit = 0
        self.rate = 0
        self.login = login
        self.valid = False

        repository.validate_code()
        if repository.valid:
            log('valid code repo', repository.name_with_owner)
            q = Repository.query_for_contributors(repository.name_with_owner)

            try:
                cs = API.get_v3(q)
            except HTTPError:
                cs = []

            # 只统计过去三年的贡献
            threee_year_ago = int(time.time()) - 365 * 24 * 3600 * 3
            for c in cs:
                _login = c['author']['login']
                weeks = c['weeks']
                for w in weeks:
                    week_start = int(w['w'])
                    if week_start > threee_year_ago and w['c'] > 0:
                        self.total_commit += w['c']
                        if _login == login:
                            self.commit += w['c']

            # 至少贡献了十个 commit
            if self.login == self.repository.owner and self.commit > 10:
                self.valid = True
            elif self.login != self.repository.owner and self.commit > 1:
                self.valid = True
            else:
                self.valid = False

            if self.valid:
                self.rate = self.commit / self.total_commit
                self.star = int(repository.start_count * self.rate)
            else:
                self.all_invalid.append(
                    (repository.name_with_owner, self.commit, self.total_commit)
                )

    def __repr__(self):
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} \n>\n'.format(classname, s)

    @classmethod
    def all(cls, login, repositories):
        for r in repositories:
            c = Contribution(login, r)
            if c.valid:
                yield c
