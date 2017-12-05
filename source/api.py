import json
import time
from typing import Tuple

import requests
from requests import HTTPError
from sqlalchemy import (
    Column,
    String,
    Integer,
)

from misc import (
    secret,
    config,
)
from source.database import Database
from source.utility import log


class API(Database.base):
    __tablename__ = 'api'
    query = Column(String, primary_key=True)
    response = Column(String)
    unixtime = Column(Integer)

    @classmethod
    def _get(cls, query):
        log('get result for query', query)
        m = Database.session.query(API).filter(API.query == query).scalar()
        if m is not None:
            now = int(time.time())
            t = now - m.unixtime
            if t < config.cache_time:
                return m
            else:
                log('query cache not valid')
                raise ValueError
        else:
            log('query not exist')
            raise ValueError

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
        url = 'https://api.github.com/graphql'
        json_query = {
            'query': query
        }
        headers = {'Authorization': 'bearer {}'.format(secret.token)}
        r = requests.post(url=url, json=json_query, headers=headers)
        if r.status_code == 200:
            j = r.json()
            cls._set(query, r.text)
            return j
        else:
            message = 'error code for url <{}> <{}>'.format(url, r.status_code)
            raise HTTPError(message, response=r)

    @classmethod
    def get_v4(cls, query, force=False):
        if force:
            return cls._get_v4(query)
        else:
            try:
                c = cls._get(query)
            except ValueError:
                return cls._get_v4(query)
            else:
                r = json.loads(c.response)
                return r

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
        log('rate limit <{}> rate remaing <{}>'.format(rate_limit, rate_remaing))
        now = int(time.time())
        log('rate will reset in <{}>'.format(now - rate_reset))

        if r.status_code == 200:
            log('get v3 r', r)
            j = r.json()
            cls._set(query, r.text)
            return j
        elif rate_remaing == 0:
            log('no rate remaing')
            # 保险起见多睡 5 s
            time.sleep(now - rate_limit + 5)
        else:
            message = 'error code for url <{}> <{}>'.format(url, r.status_code)
            raise HTTPError(message, response=r)

    @classmethod
    def get_v3(cls, query, force=False):
        if force:
            return cls._get_v3(query)
        else:
            try:
                c = cls._get(query)
            except ValueError:
                return cls._get_v3(query)
            else:
                r = json.loads(c.response)
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
            raise HTTPError(message, response=r)

    @classmethod
    def get_crawler(cls, query, force=False):
        if force:
            return cls._get_crawler(query)
        else:
            try:
                c = cls._get(query)
            except ValueError:
                return cls._get_crawler(query)
            else:
                html = c.response
                return html
