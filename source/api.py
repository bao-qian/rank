import json
import time
from contextlib import contextmanager

import requests
from sqlalchemy import (
    Column,
    String,
    Integer,
)

from source.exception import (
    NotExist,
    NoneError,
    ErrorCode,
    ErrorCode202,
    ErrorCode451,
    GraphQLError,
)
from misc import (
    secret,
    config,
)
from source.database import Database
from source.utility import (
    log,
    unixtime_from_api_v4,
)


class APIModel(Database.base):
    __tablename__ = 'api'
    query = Column(String, primary_key=True)
    response = Column(String)
    unixtime = Column(Integer)

    def valid_cache(self):
        now = int(time.time())
        t = now - self.unixtime
        if t < config.cache_time:
            return True
        else:
            return False


class API:
    def __init__(self):
        self.session = Database.session()

    def _get(self, query) -> APIModel:
        q = query.replace('\n', '')
        m = self.session.query(APIModel).filter(APIModel.query == query).scalar()
        if m is None:
            log('cache not exist', q)
            raise NotExist
        else:
            return m

    def _set(self, query, response):
        log('set result for query', query)
        now = int(time.time())
        a = APIModel(
            query=query,
            response=response,
            unixtime=now,
        )
        self.session.merge(a)
        self.session.commit()

    @staticmethod
    def ensure_not_none(data, message):
        valid = data is not None
        valid = valid and data is not [None]
        valid = valid and data is not {None}
        valid = valid and data is not {None: None}
        if not valid:
            raise NoneError(message)

    @staticmethod
    def _rate_v4(response):
        rate_limit = response['data']['rateLimit']
        limit = rate_limit['limit']
        remaining = rate_limit['remaining']
        cost = rate_limit['cost']
        reset_at = rate_limit['resetAt']
        now = int(time.time())
        reset_in = unixtime_from_api_v4(reset_at) - now
        return limit, remaining, cost, reset_at, reset_in

    def _get_v4(self, query, cache=True):
        full_query = f"""
        {{
            rateLimit {{
                limit
                cost
                remaining
                resetAt
            }}
            {query}
        }}
        """
        url = 'https://api.github.com/graphql'
        json_query = {
            'query': full_query
        }
        headers = {'Authorization': 'bearer {}'.format(secret.token)}

        r = requests.post(url=url, json=json_query, headers=headers)

        if r.status_code == 200:
            j = r.json()
            self.ensure_not_none(j, f'query <{query}> result is <{j}>')

            if 'errors' in j:
                for e in j['errors']:
                    if e['type'] == 'RATE_LIMITED':
                        j_rate = self._get_v4('', cache=False)
                        limit, remaining, cost, reset_at, reset_in = self._rate_v4(j_rate)
                        log('v4 query <{}> rate limit <{}> remaing <{}> cost <{}> resetAt <{}> reset_in <{}>'.format(
                            query, limit, remaining, cost, reset_at, reset_in
                        ))
                        # +3 to ensure
                        log('v4 sleep <{}> and try again <{}>'.format(reset_in, query))
                        time.sleep(reset_in + 3)
                        log('v4 finish sleep <{}>'.format(query))
                        return self._get_v4(query)
                raise GraphQLError(full_query, j['errors'])
            else:
                limit, remaining, cost, reset_at, reset_in = self._rate_v4(j)
                log('v4 query <{}> rate limit <{}> remaing <{}> cost <{}> resetAt <{}> reset_in <{}>'.format(
                    query, limit, remaining, cost, reset_at, reset_in
                ))
                if cache:
                    self._set(query, r.text)
                return j
        else:
            raise ErrorCode(r.status_code, query)

    @staticmethod
    def _query_for_connection(query, parameter, format_mapping):
        parameter_string = ""
        for k, v in parameter.items():
            # type is enum, so no double quote
            if type(v) is str and k != 'type' and k != 'orderBy':
                parameter_string += f'{k}: "{v}" '
            else:
                parameter_string += f'{k}: {v} '

        page_info = """
            pageInfo {
                endCursor
                hasNextPage
                hasPreviousPage
                startCursor
            }
            """
        q = query.format(
            parameter=parameter_string,
            page_info=page_info,
            **format_mapping,
        )
        return q

    def _get_v4_cache(self, query):
        try:
            m = self._get(query)
        except NotExist:
            return self._get_v4(query)
        else:
            if m.valid_cache():
                return json.loads(m.response)
            else:
                return self._get_v4(query)

    @staticmethod
    def _connection_for_keyword(response, keyword):
        c = response
        for k in keyword:
            c = c[k]
        return c

    def get_v4_connection(self, query, keyword, parameter, format_mapping):
        log('get_v4_connection', query, parameter)
        q = self._query_for_connection(query, parameter, format_mapping)
        r = self._get_v4_cache(q)
        c = self._connection_for_keyword(r['data'], keyword)
        edges = c['edges']
        yield edges
        should_continue = True

        while should_continue:
            end_cursor = c['pageInfo']['endCursor']
            has_next_page = c['pageInfo']['hasNextPage']
            if end_cursor is not None or has_next_page:
                parameter['after'] = end_cursor
                q = self._query_for_connection(query, parameter, format_mapping)
                r = self._get_v4_cache(q)
                c = self._connection_for_keyword(r['data'], keyword)
                edges = c['edges']
                should_continue = yield edges
            else:
                return

    def get_v4_object(self, query):
        log('get_v4_object', query)
        return self._get_v4_cache(query)

    @staticmethod
    def _rate_v3(response):
        rate_limit = int(response.headers['X-RateLimit-Limit'])
        rate_remaing = int(response.headers['X-RateLimit-Remaining'])
        rate_reset = int(response.headers['X-RateLimit-Reset'])
        now = int(time.time())
        reset_in = rate_reset - now
        return rate_limit, rate_remaing, rate_reset, reset_in

    def _get_v3(self, query, cache=True):
        base = 'https://api.github.com'
        url = '{}{}'.format(base, query)
        headers = {'Authorization': 'bearer {}'.format(secret.token)}
        r = requests.get(url=url, headers=headers)

        if r.status_code == 200:
            rate_limit, rate_remaing, rate_reset, reset_in = self._rate_v3(r)
            log('v3 rate limit <{}> rate remaing <{}> rate reset <{}>  reset in <{}>'.format(
                rate_limit, rate_remaing, rate_reset, reset_in,
            ))

            j = r.json()
            self.ensure_not_none(j, f'query <{query}> result is <{j}>')
            if cache:
                self._set(query, r.text)
            return j
        elif r.status_code == 202:
            raise ErrorCode202(202, query)
        # don't knwo when rate will be 0, so compare with 3
        elif r.status_code == 403:
            rate_limit, rate_remaing, rate_reset, reset_in = self._rate_v3(r)
            log('v3 rate limit <{}> rate remaing <{}> rate reset <{}>  reset in <{}>'.format(
                rate_limit, rate_remaing, rate_reset, reset_in,
            ))
            if rate_remaing == 0:
                # +3 to ensure
                log('v3 sleep <{}> and try again <{}>'.format(reset_in, query))
                time.sleep(reset_in + 3)
                log('v3 finish sleep <{}>'.format(query))
            else:
                raise ErrorCode(r.status_code, query)
        else:
            raise ErrorCode(r.status_code, query)

    def get_v3(self, query):
        log('get_v3', query)
        try:
            m = self._get(query)
        except NotExist:
            try:
                self._get_v3(query)
            except ErrorCode202:
                time.sleep(5)
                self._get_v3(query)
        else:
            if m.valid_cache():
                r = json.loads(m.response)
                return r
            else:
                try:
                    return self._get_v3(query)
                except ErrorCode202:
                    r = json.loads(m.response)
                    return r

    def _get_crawler(self, query):
        base = 'https://github.com'
        url = '{}{}'.format(base, query)
        agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                "AppleWebKit/537.36 (KHTML, like Gecko) " \
                "Chrome/62.0.3202.94 Safari/537.36"
        headers = {'User-Agent': agent}
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            html = r.text
            self._set(query, html)
            return html
        elif r.status_code == 451:
            raise ErrorCode451(451, query)
        else:
            raise ErrorCode(r.status_code, query)

    def get_crawler(self, query):
        log('get_crawler', query)
        try:
            m = self._get(query)
        except NotExist:
            return self._get_crawler(query)
        else:
            if m.valid_cache():
                return m.response
            else:
                return self._get_crawler(query)


@contextmanager
def api():
    a = API()
    yield a
    a.session.close()
