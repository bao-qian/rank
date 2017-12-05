from requests import HTTPError

from misc import config
from source.api import API
from source.contribution import Contribution
from source.repository import Repository
from source.utility import log


class User:
    def __init__(self, node):
        self.name = node['name']
        self.login = node['login']
        self.url = node['url']
        self.avatar_url = node['avatarUrl']
        self.followers_count = node['followers']['totalCount']
        self.location = node['location']
        r1 = node['pinnedRepositories']['edges']
        r2 = node['repositories']['edges']

        if len(r1) == 0:
            r = Repository.repositories_from_nodes(r2)
        else:
            r = Repository.repositories_from_nodes(r1)

        self.repositories = list(r)
        self.pinned_repositories = r1
        self.popular_repositories = r2
        self.contribution = []
        self.language = {}
        self.star = 0

    @classmethod
    def users_from_nodes(cls, nodes):
        for node in nodes:
            n = node['node']
            log('users_from_nodes <{}>'.format(n['name']))
            yield User(n)

    @classmethod
    def user_from_node(cls, node):
        return User(node)

    @staticmethod
    def query_china_user(first, after):
        r1 = Repository.query_pinned()
        r2 = Repository.query_popular()
        q = """
            {{
                search(first: {},{} query: "{}", type: USER) {{
                    pageInfo {{
                      endCursor
                      hasNextPage
                      hasPreviousPage
                      startCursor
                    }}
                    edges {{
                        node {{
                            ... on User {{
                            login
                            name
                            url
                            avatarUrl
                            followers {{
                                totalCount
                            }}
                            location
                            {}
                            {}
                            }}
                        }}
                    }}
                }}
            }}
            """.format(first, after, config.user_query, r1, r2)
        return q

    @staticmethod
    def query_user(user):
        r1 = Repository.query_pinned()
        r2 = Repository.query_popular()
        q = """
            {{
                user(login: "{}") {{
                    login
                    name
                    url
                    avatarUrl
                    followers {{
                        totalCount
                    }}
                    location
                    {}
                    {}
                }}
            }}
            """.format(user, r1, r2)
        return q

    @classmethod
    def users_for_query(cls):
        q = User.query_china_user(config.count_per_request, '')
        log('query', q)

        try:
            r = API.get_v4(q)
        except HTTPError:
            yield from []
        else:
            s = r['data']['search']
            end_cursor = s['pageInfo']['endCursor']
            nodes = s['edges']
            yield from User.users_from_nodes(nodes)

            steps = config.user_count // config.count_per_request
            for i in range(steps - 1):
                after = 'after:" {}"'.format(end_cursor)
                q = User.query_china_user(config.count_per_request, after)
                log('query', q)

                try:
                    r = API.get_v4(q)
                except HTTPError:
                    yield from []
                else:
                    log('user for query', r)
                    s = r['data']['search']
                    end_cursor = s['pageInfo']['endCursor']
                    nodes = s['edges']
                    yield from User.users_from_nodes(nodes)

    @classmethod
    def users_for_extra(cls):
        for e in config.extra_user:
            q = User.query_user(e)
            log('query', q)
            try:
                r = API.get_v4(q)
            except HTTPError:
                yield from []
            else:
                node = r['data']['user']
                print('users for extra <{}>'.format(node['name']))
                u = User.user_from_node(node)
                yield u

    @classmethod
    def all(cls):
        u2 = cls.users_for_extra()
        u1 = cls.users_for_query()
        us = list(u2) + list(u1)
        for i, u in enumerate(us):
            log('user no.{} {}'.format(i, u.login))
            cs = list(Contribution.all(u.login, u.repositories))
            u.contribution = sorted(cs, key=lambda c: c.star, reverse=True)
            u.star = sum([c.star for c in u.contribution])
            ls = {}
            for c in cs:
                k = c.repository.language
                ls[k] = ls.get(k, 0) + c.star
            u.language = sorted(ls.items(), key=lambda i: i[1], reverse=True)
        return us
