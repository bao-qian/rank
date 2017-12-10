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
            search({parameter}) {{
                {page_info}
                edges {{
                    {edge}
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
    def users_for_query(cls):
        for user_query, count in config.user_query_and_count:
            query = cls.query_connection()
            edge = cls.query_edge()
            format_mapping = dict(
                edge=edge,
            )
            parameter = {
                'query': user_query,
                'type': 'USER',
                'first': config.user_per_request,
            }

            connection = API.get_v4_connection(
                query, ['search'], parameter, format_mapping,
            )
            edges = next(connection)

            while True:
                for e in edges:
                    e = e['node']
                    yield User(e)

                count = count - config.user_per_request
                should_continue = count > 0
                try:
                    edges = connection.send(should_continue)
                except StopIteration:
                    connection.close()
                    return

    @classmethod
    def users_for_extra(cls):
        for e in config.extra_user:
            q = User.query_object(e)
            try:
                r = API.get_v4_object(q)
            except ErrorCode:
                return
            else:
                node = r['data']['user']
                u = User(node)
                yield u

    @classmethod
    def all(cls):
        u2 = cls.users_for_extra()
        u1 = cls.users_for_query()
        us = list(u2) + list(u1)
        seen = set()
        for i, u in enumerate(us):
            if u.login not in seen and u.login not in config.block_user:
                seen.add(u.login)
                log('start user no.{} {} {}'.format(i, u.login, len(u.repositories)))
                cs = Contribution.all(u.login, u.repositories)
                u.contribution = sorted(cs, key=lambda c: c.star, reverse=True)
                u.star = sum([c.star for c in u.contribution])
                if u.star > 0:
                    ls = {}
                    for c in u.contribution:
                        k = c.repository.language
                        ls[k] = ls.get(k, 0) + c.star
                    u.language = sorted(ls.items(), key=lambda l: l[1], reverse=True)
                    yield u
                log('end user no.{} {} {}'.format(i, u.login, u.language))
