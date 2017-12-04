import os

from jinja2 import FileSystemLoader, Environment

from contribution import Contribution
from model import init_db
from repository import Repository
from user import User
from utility import (
    log,
)


def all_data():
    users = User.all()
    us = sorted(users, key=lambda u: u.star, reverse=True)
    return us


def log_data(users):
    for u in users:
        log('user stat <{}> <{}> <{}>'.format(len(u.repositories), u.name, u.url))

    for r in Repository.all_invalid:
        log('invalid repository', r)
    for c in Contribution.all_invalid:
        log('wrong contribution', c)

    for i, u in enumerate(users):
        # if len(u.contribution) > 0 and u.login not in u.contribution[0].repository.name_with_owner:
        formatted = 'user star:'
        formatted += f'{i:3} {u.login:15} {int(u.star):5} '
        for c in u.contribution[:3]:
            if c.count > 0:
                r = c.repository
                formatted += f'{r.name_with_owner:40} {r.language:12} {int(c.count):5} '
        log(formatted)


def configured_environment():
    # __file__ 就是本文件的名字
    # 得到用于加载模板的目录
    path = '{}'.format(os.path.dirname(__file__))
    # 创建一个加载器, jinja2 会从这个目录中加载模板
    loader = FileSystemLoader(path)
    # 用加载器创建一个环境, 有了它才能读取模板文件
    return Environment(loader=loader)


class Template:
    env = configured_environment()

    @classmethod
    def render(cls, path, **kwargs):
        t = Template.env.get_template(path)
        return t.render(**kwargs)


def generate_html(users):
    pass


def main():
    init_db()
    us = all_data()
    log_data(us)
    generate_html(us)


if __name__ == '__main__':
    main()
