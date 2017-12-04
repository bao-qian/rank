import os

from jinja2 import FileSystemLoader, Environment

from misc import config
from source.contribution import Contribution
from source.model import init_db
from source.repository import Repository
from source.user import User
from source.utility import log


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
        formatted += f'{i:3} {u.login:15} {u.star:5} '
        for c in u.contribution[:3]:
            if c.star > 0:
                r = c.repository
                formatted += f'{r.name_with_owner:40} {r.language:12} {c.star:5} '
        log(formatted)


def configured_environment():
    loader = FileSystemLoader(config.static)
    return Environment(loader=loader)


class Template:
    env = configured_environment()

    @classmethod
    def render(cls, path, **kwargs):
        t = Template.env.get_template(path)
        return t.render(**kwargs)


def generate_html(users):
    template = 'template_rank.html'
    html = Template.render(template, users=users)
    filename = 'rank.html'
    path = os.path.join(config.static, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    init_db()
    us = all_data()
    log_data(us)
    generate_html(us)


if __name__ == '__main__':
    main()
