from source.exception import ErrorCode
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
    def query_filed(cls):
        r1 = Repository.query_pinned()
        r2 = Repository.query_popular()
        q = f"""
            login
            name
            url
            avatarUrl
            followers {{
                totalCount
            }}
            location
            {r1}
            {r2}
            """
        return q

    @classmethod
    def query_connection(cls):
        q = """
            search({}) {{
                {}
                edges {{
                    {}
                }}
            }}
        """
        return q

    @classmethod
    def query_edge(cls):
        f = cls.query_filed()
        edge = f"""
            node {{
                ... on User {{
                    {f}
                }}
            }}
        """
        return edge

    @classmethod
    def query_object(cls, user):
        f = cls.query_filed()
        q = f"""
            user(login: "{user}") {{
                {f}
            }}
            """
        return q

    @classmethod
    def users_for_query(cls, user_query, count):
        query = cls.query_connection()
        edge = cls.query_edge()
        parameter = {
            'query': user_query,
            'type': 'USER',
        }
        nodes = API.get_v4_connection(
            query, ['search'], parameter, edge, config.count_per_request, count
        )

        for query in nodes:
            n = query['node']
            log('users_from_nodes <{}>'.format(n['name']))
            yield User(n)

    @classmethod
    def users_for_queries(cls):
        for q, c in config.user_query_and_count:
            yield from User.users_for_query(q, c)

    @classmethod
    def users_for_extra(cls):
        for e in config.extra_user:
            q = User.query_object(e)
            log('query', q)
            try:
                r = API.get_v4_object(q)
            except ErrorCode:
                yield from []
            else:
                node = r['data']['user']
                print('users for extra <{}>'.format(node['name']))
                u = User(node)
                yield u

    @classmethod
    def all(cls):
        u2 = cls.users_for_extra()
        u1 = cls.users_for_queries()
        us = list(u2) + list(u1)
        seen = set()
        for i, u in enumerate(us):
            if u.login not in seen and u.login not in config.block_user:
                seen.add(u.login)
                log('user no.{} {}'.format(i, u.login))
                cs = list(Contribution.all(u.login, u.repositories))
                u.contribution = sorted(cs, key=lambda c: c.star, reverse=True)
                u.star = sum([c.star for c in u.contribution])
                if u.star > 0:
                    ls = {}
                    for c in cs:
                        k = c.repository.language
                        ls[k] = ls.get(k, 0) + c.star
                    u.language = sorted(ls.items(), key=lambda l: l[1], reverse=True)
                    yield u
