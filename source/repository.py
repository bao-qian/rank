from pyquery import PyQuery

from misc import config
from source.api import API
from source.utility import log


class Repository:
    all_invalid = []

    def __init__(self, node):
        self.name = node['name']
        self.owner = node['owner']
        self.name_with_owner = node['nameWithOwner']
        p = node['primaryLanguage']
        if p is not None:
            self.language = p['name']
        else:
            self.language = None
        self.url = node['url']
        self.start_count = node['stargazers']['totalCount']
        self.valid = False

    def __repr__(self):
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} \n>\n'.format(classname, s)

    @classmethod
    def repositories_from_nodes(cls, nodes):
        for node in nodes:
            n = node['node']
            log('repositories_from_nodes <{}>'.format(n['name']))
            r = cls(n)
            yield r

    def validate_code(self):
        # 有些仓库没有文件或者没有一点所以语言是 none
        if self.language is None or self.language in config.invalid_language:
            self.valid = False
            self.all_invalid.append((self.name_with_owner, self.language))
        else:
            # 必须要选一个语言
            query = '/{}/search?l=c'.format(self.name_with_owner)
            html = API.get_crawler(query)
            q = PyQuery(html)

            files = []
            for item in q.items('.filter-item'):
                parts = item.text().strip().split(' ', 1)
                if len(parts) == 2:
                    count = int(parts[0].replace(',', ''))
                    language = parts[1]
                    files.append((count, language))
                else:
                    # 选了一个语言后，该语言在右侧没有文件统计
                    head = q('.codesearch-results h3').text().strip()
                    text1 = 'code results'
                    text2 = 'Results'
                    if text1 in head:
                        count = head.split(text1, 1)[0].replace(',', '')
                        count = int(count)
                        language = 'C'
                        files.append((count, language))
                    elif text2 in head:
                        count = len(q('.code-list-item'))
                        language = 'C'
                        files.append((count, language))
                    else:
                        log('cannot find c in repo', self.name_with_owner)

            if len(files) > 1:
                files = sorted(files, key=lambda file: file[0], reverse=True)
                f1 = files[0]
                f2 = files[1]
                log('validate code <{}> <{}>'.format(files, files))
                if f1[1] in config.invalid_language:
                    self.valid = False
                    # 如果文件最多的两个语言相等，则他们都不能是文本
                elif f1[0] == f2[0] and f2[1] in config.invalid_language:
                    self.valid = False
                else:
                    self.valid = True
            else:
                self.valid = False

            # 主要语言文件不少于三个
            for f in files:
                if f[1] == self.language:
                    if f[0] < 3:
                        self.valid = False

            if not self.valid:
                self.all_invalid.append((self.name_with_owner, files))

    @staticmethod
    def _query():
        q = """
        edges {
              node {
                    name
                    owner  
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
