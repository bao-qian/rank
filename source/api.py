import datetime
import json
import time

import requests
from requests import HTTPError
from sqlalchemy import (
    Column,
    String,
    Integer,
)

from exception import (
    ErrorCode202,
    NotExist,
)
from misc import (
    secret,
    config,
)
from source.database import Database
from source.utility import log, log_error


class API(Database.base):
    __tablename__ = 'api'
    query = Column(String, primary_key=True)
    response = Column(String)
    unixtime = Column(Integer)

    @classmethod
    def _get(cls, query):
        log('get result for query', query)
        m = Database.session.query(API).filter(API.query == query).scalar()
        if m is None:
            log('query not exist')
            raise NotExist
        else:
            return m

    @classmethod
    def _valid_cache(cls, m):
        now = int(time.time())
        t = now - m.unixtime
        if t < config.cache_time:
            return True
        else:
            return False

    @classmethod
    def _set(cls, query, response):
        log('set result for query', query)
        now = int(time.time())
        c = API(
            query=query,
            response=response,
            unixtime=now,
        )
        Database.session.merge(c)
        Database.session.commit()

    @classmethod
    def _get_v4(cls, query):
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

            rate_limit = j['data']['rateLimit']
            limit = rate_limit['limit']
            remaining = rate_limit['remaining']
            cost = rate_limit['cost']
            reset_at = rate_limit['resetAt']
            log('v4 rate limit <{}> remaing <{}> cost <{}> resetAt <{}>'.format(
                limit, remaining, cost, reset_at)
            )
            time_format = '%Y-%m-%dT%H:%M:%SZ'
            reset_at = int(datetime.datetime.strptime(reset_at, time_format).timestamp())
            now = int(time.time())
            log('v4 rate will reset in <{}>'.format(reset_at - now))

            # don't knwo when rate will be 0, so compare with 3
            if remaining < 3:
                log('v4 no rate remaing')
                # sleep 5 seconds more to guarantee success
                time.sleep(5 + (reset_at - now))
            cls._set(query, r.text)
            return j
        else:
            message = 'error code for url <{}> <{}>'.format(url, r.status_code)
            log_error(message)
            raise HTTPError(message, response=r)

    @classmethod
    def query_for_connection(cls, keyword, parameter, node):
        parameter_string = ""
        for k, v in parameter.items():
            # type is enum, so no double quote
            if type(v) is str and k != 'type':
                parameter_string += f'{k}: "{v}" '
            else:
                parameter_string += f'{k}: {v} '

        q = f"""
            {keyword}({parameter_string}) {{
                pageInfo {{
                  endCursor
                  hasNextPage
                  hasPreviousPage
                  startCursor
                }}
                edges {{
                    node {{
                        {node}
                    }}
                }}
            }}
        """
        return q

    @classmethod
    def _get_v4_cache(cls, query):
        try:
            c = cls._get(query)
        except NotExist:
            return cls._get_v4(query)
        else:
            r = json.loads(c.response)
            return r

    @classmethod
    def get_v4_connection(cls, keyword, parameter, node, first, count):
        parameter['first'] = first
        q = cls.query_for_connection(keyword, parameter, node)
        r = cls._get_v4_cache(q)
        s = r['data'][keyword]
        nodes = s['edges']
        yield from nodes
        end_cursor = s['pageInfo']['endCursor']

        steps = count // first
        for i in range(steps - 1):
            parameter['after'] = end_cursor
            q = cls.query_for_connection(keyword, parameter, node)
            r = cls._get_v4_cache(q)
            s = r['data'][keyword]
            nodes = s['edges']
            yield from nodes
            end_cursor = s['pageInfo']['endCursor']
            has_next_page = s['pageInfo']['hasNextPage']
            if end_cursor is None or not has_next_page:
                break

    @classmethod
    def get_v4_object(cls, query):
        return cls._get_v4_cache(query)

    @classmethod
    def _get_v3(cls, query):
        base = 'https://api.github.com'
        url = '{}{}'.format(base, query)
        log('get v3 url', url)
        headers = {'Authorization': 'bearer {}'.format(secret.token)}
        r = requests.get(url=url, headers=headers)

        rate_limit = int(r.headers['X-RateLimit-Limit'])
        rate_reset = int(r.headers['X-RateLimit-Reset'])
        rate_remaing = int(r.headers['X-RateLimit-Remaining'])
        log('v3 rate limit <{}> rate remaing <{}>'.format(rate_limit, rate_remaing))
        now = int(time.time())
        log('v3 rate will reset in <{}>'.format(rate_reset - now))

        if r.status_code == 200:
            log('get v3 r', r)
            j = r.json()
            cls._set(query, r.text)
            return j
        elif r.status_code == 202:
            message = f'error code 202 for {query}'
            log_error(message)
            raise ErrorCode202(message, 202, query)
        # don't knwo when rate will be 0, so compare with 3
        elif rate_remaing < 3:
            log('v3 no rate remaing')
            # sleep 5 seconds more to guarantee success
            time.sleep(5 + (rate_reset - now))
        else:
            message = 'error code for url <{}> <{}>'.format(url, r.status_code)
            log_error(message)
            raise HTTPError(message, response=r)

    @classmethod
    def get_v3(cls, query):
        try:
            m = cls._get(query)
        except NotExist:
            try:
                cls._get_v3(query)
            except ErrorCode202:
                # https://developer.github.com/v3/repos/statistics/
                time.sleep(5)
                cls._get_v3(query)
        else:
            if cls._valid_cache(m):
                r = json.loads(m.response)
                return r
            else:
                try:
                    return cls._get_v3(query)
                except ErrorCode202:
                    # https://developer.github.com/v3/repos/statistics/
                    r = json.loads(m.response)
                    return r

    @classmethod
    def _get_crawler(cls, query):
        base = 'https://github.com'
        url = '{}{}'.format(base, query)
        log('get crawler url', url)
        agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                "AppleWebKit/537.36 (KHTML, like Gecko) " \
                "Chrome/62.0.3202.94 Safari/537.36"
        headers = {'User-Agent': agent}
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            html = r.text
            cls._set(query, html)
            return html
        else:
            message = 'error code for url <{}> <{}>'.format(url, r.status_code)
            log_error(message)
            raise HTTPError(message, response=r)

    @classmethod
    def get_crawler(cls, query):
        try:
            c = cls._get(query)
        except NotExist:
            return cls._get_crawler(query)
        else:
            html = c.response
            return html
