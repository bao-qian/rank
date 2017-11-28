from api import API
from utility import log, log_dict
from pyquery import PyQuery


class Repository:
    def __init__(self, node):
        self.name = node['name']
        self.name_with_owner = node['nameWithOwner']
        p = node['primaryLanguage']
        if p is not None:
            self.language = p['name']
        else:
            self.language = None
        self.url = node['url']
        self.start_count = node['stargazers']['totalCount']
        self.is_code = False

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

    def validate_code(self):
        query = '/{}/search?l=c'.format(self.name_with_owner)
        html = API.get_crawler(query)
        q = PyQuery(html)
        files = []
        for item in q.items('.filter-item'):
            parts = item.text().strip().split(' ', 1)
            if len(parts) == 2:
                count = int(parts[0].replace(',', ''))
                language = parts[1]
            else:
                count = 9999  # max
                language = parts[0]
            files.append((count, language))
        if len(files) > 0:
            primary_language = max(files, key=lambda f: f[0])[1]
            log('validate code <{}> <{}>'.format(primary_language, files))
            if primary_language not in ['HTML', 'Markdown', 'Text']:
                self.is_code = True

    @staticmethod
    def _query():
        q = """
        edges {
              node {
                    name  
                    nameWithOwner
                    url
                    primaryLanguage {
                        name
                    }       
                    stargazers {
                        totalCount
                    }
                    
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

    @classmethod
    def query_for_contributors(cls, name_with_owner):
        q = '/repos/{}/stats/contributors'.format(name_with_owner)
        return q
