from pathlib import PurePosixPath

from fabric.context_managers import cd
from fabric.decorators import task
from fabric.operations import sudo, local
from fabric.state import env
from fabric.tasks import execute


def server():
    env.use_ssh_config = True
    env.hosts = ['rank']


class Directory:
    base = '/var/www/rank'
    misc = '/var/www/rank/misc'


def commands():
    cs = [
        "ln -f -s {} /etc/apt/sources.list".format(
            PurePosixPath(Directory.misc, 'ubuntu.list'),
        ),
        "mkdir -p /root/.pip",
        "ln -f -s {} /root/.pip/pip.conf".format(
            PurePosixPath(Directory.misc, 'pip.conf'),
        ),

        "sudo apt-get update",
        "sudo add-apt-repository -y ppa:jonathonf/python-3.6",
        "sudo apt-get update",
        "sudo apt-get install -y python3.6 python3-pip nginx",
        "sudo -H python3.6 -m pip install sqlalchemy pyquery",

        "sudo ln -f -s {} /etc/systemd/system/rank.service".format(
            PurePosixPath(Directory.misc, 'rank.service')
        ),
        "sudo ln -f -s {} /etc/systemd/system/rank.timer".format(
            PurePosixPath(Directory.misc, 'rank.timer')
        ),
        "sudo systemctl daemon-reload",
        "sudo systemctl restart rank.service",
        "sudo systemctl restart rank.timer",

        "rm -f /etc/nginx/sites-enabled/*",
        "sudo ln -f -s {} /etc/nginx/sites-enabled/rank.conf".format(
            PurePosixPath(Directory.misc, 'nginx.conf ')
        ),
        "sudo systemctl restart nginx",

        "echo 'full url:'",
        "hostname -I | sed -e 's/ /\\n/g' | sed -e 's/^/http:\/\//g'",
    ]
    return cs


@task
def update():
    server()

    def update_code():
        with cd(Directory.base):
            sudo('git pull')
        sudo('cp -f {} {}'.format(
            PurePosixPath(Directory.misc, 'server_config.py'),
            PurePosixPath(Directory.misc, 'config.py')
        ))
        for c in commands():
            sudo(c)

    execute(update_code)


@task
def provision():
    local('cp {} {}'.format(
        PurePosixPath(Directory.misc, 'test_config.py'),
        PurePosixPath(Directory.misc, 'config.py')
    ))
    for c in commands():
        local(c)


@task
def deploy():
    server()

    def deploy_code():
        with cd('/var/www'):
            sudo('rm -rf rank')
        sudo('git clone https://github.com/happlebao/rank.git')
        sudo('cp {} {}'.format(
            PurePosixPath(Directory.misc, 'server_config.py'),
            PurePosixPath(Directory.misc, 'config.py')
        ))
        for c in commands():
            sudo(c)

    execute(deploy_code)
