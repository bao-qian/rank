import json

import requests

import secret
from model import Model
from sqlalchemy import (
    Column,
    String,
    exists)

from utility import log


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
        log('get result for query', result)
        return result

    @classmethod
    def _set(cls, query, response):
        log('add result for query', query, response)
        c = API(
            graph_query=query,
            response=response,
        )
        Model.session.add(c)
        Model.session.commit()

    @classmethod
    def get_v4(cls, query):
        if cls._exist(query):
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
            cls._set(query, r.text)
            j = r.json()
            return j

    @classmethod
    def get_v3(cls, query):
        pass
