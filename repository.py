from utility import log, log_dict


class Repository:
    def __init__(self, node):
        self.name = node['name']
        self.url = node['url']
        self.start_count = node['stargazers']['totalCount']

    def __repr__(self):
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} \n>\n'.format(classname, s)

    @classmethod
    def repositories_from_nodes(cls, nodes):
        log('repositories_from_nodes')
        log_dict(nodes)
        for node in nodes:
            n = node['node']
            r = cls(n)
            yield r

    @staticmethod
    def _query():
        q = """
        edges {
              node {
                    stargazers {
                        totalCount
                    }
                    name
                    url
                }
        }
        """
        return q

    @classmethod
    def query_pinned(cls):
        r = cls._query()
        q = """
        pinnedRepositories(first: 6) {{
            {}
        }}
        """.format(r)
        return q

    @classmethod
    def query_popular(cls):
        r = cls._query()
        q = """
        repositories(first: 6, orderBy: {{field: STARGAZERS, direction: DESC}}) {{
            {}
        }}
        """.format(r)
        return q
