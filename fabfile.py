from fabric.api import *
from docker import Client
from os import path

db_nodes = []
db_first = None

client = Client()
for container in client.containers():
    container_id = container['Id']
    info = client.inspect_container(container_id)
    ip = info['NetworkSettings']['IPAddress']
    if info['Config']['Image'] == 'riak':
        db_nodes.append((container_id, ip))

env.roledefs = {
    'db': [value for key, value in db_nodes]
}

env.user = 'root'
env.password = 'password'

def riak_build_image():
    local('docker build -t riak .')

@parallel
def riak_bootstrap():
    for i in xrange(0, 10):
        local("docker run -d riak")

@parallel
def riak_destroy():
    for key, value in db_nodes:
        client.kill(key)

@roles('db')
def riak_start():
    run('sed -i s/127\.0\.0\.1/{0}/g /etc/riak/app.config'.format(env.host_string))
    run('sed -i s/127\.0\.0\.1/{0}/g /etc/riak/vm.args'.format(env.host_string))
    run('/usr/sbin/riak start')

@roles('db')
def riak_cluster():
    global db_first
    if not db_first:
        db_first = env.host_string
    else:
        run('/usr/sbin/riak-admin cluster join riak@{0}'.format(db_first))

@roles('db')
def riak_commit():
    global db_first
    if db_first == env.host_string:
        db_first = env.host_string
        run('/usr/sbin/riak-admin cluster plan')
        run('/usr/sbin/riak-admin cluster commit')

def riak_setup():
    execute(riak_start)
    execute(riak_cluster)
    execute(riak_commit)
