from fabric.api import run, sudo, puts, abort, env, open_shell, local, put
from fabric.colors import green, red, yellow
import os

env.use_ssh_config = True

def all():
    env.hosts = ['stats01']

def uptime():
    run('uptime')

def shell():
    open_shell()

def deploy():
    local("rm -rf dist")
    local("python setup.py bdist_egg")
    sudo("rm -rf /tmp/CMStats.egg")
    put("dist/CMStats-*-py*.egg", "/tmp/CMStats.egg")
    sudo("easy_install /tmp/CMStats.egg")
    sudo("supervisorctl restart stats")
