from fabric.api import *
from docker import Client
from os import path

db_nodes = []
db_first = []
db_lookup = {}

client = Client()
for container in client.containers():
    container_id = container['Id']
    info = client.inspect_container(container_id)
    ip = info['NetworkSettings']['IPAddress']
    if info['Config']['Image'] == 'riak':
        db_nodes.append((container_id, ip))
        db_lookup[ip] = container_id

if len(db_nodes) > 0:
    db_first.append(db_nodes[0])
    db_nodes = db_nodes[1:]

env.roledefs = {
    'db-main' : [value for key, value in db_first],
    'db': [value for key, value in db_nodes]
}

env.user = 'root'
env.password = 'password'

def build(number_nodes=2):
    local('docker build -t riak .')
    for i in xrange(0, int(number_nodes)):
        node = local("docker run -d riak", capture=True)

@parallel
@roles('db-main', 'db')
def destroy():
    client.kill(db_lookup[env.host_string])

@parallel
@roles('db-main', 'db')
def start():
    run('sed -i s/127\.0\.0\.1/{0}/g /etc/riak/app.config'.format(env.host_string))
    run('sed -i s/127\.0\.0\.1/{0}/g /etc/riak/vm.args'.format(env.host_string))
    run('riak start')

@parallel
@roles('db')
def cluster():
    node_id, node_ip = db_first[0]
    run('riak-admin cluster join riak@{0}'.format(node_ip))

@roles('db-main')
def commit():
    run('riak-admin cluster plan')
    run('riak-admin cluster commit')

def setup():
    execute(start)
    execute(cluster)
    execute(commit)

@roles('db-main')
def status():
    run('riak-admin status')
