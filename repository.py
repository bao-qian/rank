class Repository:
    def __init__(self, name, url, star_count):
        self.name = name
        self.url = url
        self.start_count = star_count

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