from requests import HTTPError

from api import API
from repository import Repository
from utility import log


class Contribution:
    wrong = []

    def __init__(self, login, repository):
        self.repository = repository
        self.count = 0
        self.contributed_commit = 0
        self.total_commit = 0
        self.rate = 0

        repository.validate_code()
        if repository.is_code:
            log('valid code repo', repository.name_with_owner)
            q = Repository.query_for_contributors(repository.name_with_owner)

            try:
                cs = API.get_v3(q)
            except HTTPError:
                cs = []

            for c in cs:
                _login = c['author']['login']
                total = c['total']
                self.total_commit += total
                if _login == login:
                    self.contributed_commit = total

        if self.total_commit != 0:
            self.rate = self.contributed_commit / self.total_commit
            self.count = repository.start_count * self.rate

    def __repr__(self):
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} \n>\n'.format(classname, s)

    @classmethod
    def all(cls, login, repositories):
        for r in repositories:
            c = Contribution(login, r)
            if c.contributed_commit == 0 or c.total_commit == 0:
                cls.wrong.append((r.name_with_owner, c.contributed_commit, c.total_commit))
            else:
                yield c
