import json
import time

import requests
from requests import HTTPError
from sqlalchemy import (
    Column,
    String,
    exists,
)

from misc import secret
from source.model import Model
from source.utility import log


class API(Model.base):
    __tablename__ = 'api'
    graph_query = Column(String, primary_key=True)
    response = Column(String)

    @classmethod
    def _exist(cls, query):
        statement = exists().where(API.graph_query == query)
        r = Model.session.query(statement).scalar()
        log('cache exist', r, query)
        return r

    @classmethod
    def _get(cls, query):
        result = Model.session.query(API).filter(API.graph_query == query).scalar()
        log('get result for query', query)
        # log('get result for query', result)
        return result

    @classmethod
    def _set(cls, query, response):
        log('set result for query', query)
        c = API(
            graph_query=query,
            response=response,
        )
        Model.session.merge(c)
        Model.session.commit()

    @classmethod
    def get_v4(cls, query, force=False):
        if not force and cls._exist(query):
            c = cls._get(query)
            r = json.loads(c.response)
            return r
        else:
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
                message = 'url {} get error code {}'.format(url, r.status_code)
                raise HTTPError(message, response=r)

    @classmethod
    def get_v3(cls, query, force=False):
        if not force and cls._exist(query):
            c = cls._get(query)
            r = json.loads(c.response)
            return r
        else:
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
                message = 'url {} get error code {}'.format(url, r.status_code)
                raise HTTPError(message, response=r)

    @classmethod
    def get_crawler(cls, query, force=False):
        if not force and cls._exist(query):
            c = cls._get(query)
            html = c.response
            return html
        else:
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
                message = 'url {} get error code {}'.format(url, r.status_code)
                raise HTTPError(message, response=r)
