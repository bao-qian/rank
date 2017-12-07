from pyquery import PyQuery
from requests import HTTPError

from misc import config
from source.model import Model
from source.api import API
from source.utility import log


class Repository(Model):
    all_invalid = []

    def __init__(self, node):
        self.name = node['name']
        self.owner = node['owner']['login']
        self.name_with_owner = node['nameWithOwner']
        self.description = node['description']
        # some repo has no description
        if self.description is None:
            self.description = ''

        p = node['primaryLanguage']
        if p is not None:
            self.language = p['name']
        else:
            self.language = None
        self.url = node['url']
        self.start_count = node['stargazers']['totalCount']
        self.valid = False

    @classmethod
    def repositories_from_nodes(cls, nodes):
        for node in nodes:
            n = node['node']
            log('repositories_from_nodes <{}>'.format(n['name']))
            r = cls(n)
            yield r

    def valid_name_and_description(self):
        for d in config.invalid_description:
            if d in self.name.lower() or d in self.description.lower():
                return False
        return True

    def validate_code(self):
        # language may be none for some repo due to none files or other reason
        if self.language is None or self.language in config.invalid_language or self.start_count == 0:
            self.valid = False
            self.all_invalid.append((self.name_with_owner, self.start_count, self.language))
        elif not self.valid_name_and_description():
            self.valid = False
            self.all_invalid.append((self.name_with_owner, self.start_count, self.name_with_owner, self.description))
        else:
            # at least one language to get result
            query = '/{}/search?l=c'.format(self.name_with_owner)
            try:
                html = API.get_crawler(query)
            except HTTPError:
                self.valid = False
                self.all_invalid.append((self.name_with_owner, self.start_count, self.language))
            else:
                q = PyQuery(html)
                files = []
                for item in q.items('.filter-item'):
                    parts = item.text().strip().split(' ', 1)
                    if len(parts) == 2:
                        count = int(parts[0].replace(',', ''))
                        language = parts[1]
                        files.append((count, language))
                    else:
                        # the selected language has no number count in right sidebar
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
                        # the top 2 type should be code instead of text
                    elif f1[0] == f2[0] and f2[1] in config.invalid_language:
                        self.valid = False
                    else:
                        self.valid = True
                else:
                    self.valid = False

                # code files shoud be at least 3
                total = 0
                for f in files:
                    if f[1] not in config.invalid_language:
                        total += f[0]
                self.valid = self.valid and total > 3

                if not self.valid:
                    self.all_invalid.append((self.name_with_owner, self.start_count, files))

    @staticmethod
    def _query():
        q = """
        edges {
              node {
                    name
                    owner {
                        login
                    } 
                    nameWithOwner
                    url
                    description
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
