import config
from api import API
from contribution import Contribution
from repository import Repository
from utility import log, log_dict


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
        self.star = 0

    def __repr__(self):
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} \n>\n'.format(classname, s)

    @classmethod
    def users_from_nodes(cls, nodes):
        for node in nodes:
            log('users_from_nodes')
            log_dict(node)
            n = node['node']
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
        # 非 100 整除的不管
        length = 100

        q = User.query_china_user(length, '')
        log('query', q)
        r = API.get_v4(q)
        s = r['data']['search']
        end_cursor = s['pageInfo']['endCursor']
        nodes = s['edges']
        yield from User.users_from_nodes(nodes)

        steps = int(config.user_count / length)
        for i in range(steps - 1):
            after = 'after:" {}"'.format(end_cursor)
            q = User.query_china_user(length, after)
            log('query', q)
            r = API.get_v4(q)
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
            r = API.get_v4(q)
            log_dict(r)
            node = r['data']['user']
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
            u.contribution = sorted(cs, key=lambda c: c.count, reverse=True)
            u.star = sum([c.count for c in u.contribution])
        return us
