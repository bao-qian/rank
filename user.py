from repository import Repository


class User:
    def __init__(self, name, url, pinned_repositories, popular_repositories):
        self.name = name
        self.url = url
        self.pinned_repositories = pinned_repositories['edges']
        self.popular_repositories = popular_repositories['edges']
        if len(self.pinned_repositories) == 0:
            self.repositories = self.popular_repositories
        else:
            self.repositories = self.pinned_repositories

    def __repr__(self):
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} \n>\n'.format(classname, s)

    @staticmethod
    def query_china_user():
        r1 = Repository.query_pinned()
        r2 = Repository.query_popular()
        q = """
            {{
                search(first: 100, query: "location:china", type: USER) {{
                    edges {{
                        node {{
                            ... on User {{
                            name
                            url
                            {0}
                            {1}
                            }}
                        }}
                    }}
                }}
            }}
            """.format(r1, r2)
        return q
