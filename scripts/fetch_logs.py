import os.path

from fabric.api import env
from fabric.operations import get


env.hosts = ['root@ec2-23-23-66-181.compute-1.amazonaws.com', 'root@ec2-54-234-73-236.compute-1.amazonaws.com']


def _get_logs_dir(deployment):
    return'./logs/%s' % deployment
    

def _fetch_logs(log_type, vhost, days, dst):
    src = '/var/log/httpd/%s%s.log' % (vhost, log_type)
    filename = os.path.basename(src)
    get(src, '%s/%s.%s' % (dst, filename, env.host))
    for day in xrange(days):
        src = '/var/log/httpd/%s%s.log.%d' % (vhost, log_type, day + 1)
        filename = os.path.basename(src)
        get(src, '%s/%s.%s' % (dst, filename, env.host))


def fetch_logs(deployment, vhost='', days=0, access=True, error=False):
    if vhost:
        vhost = vhost + '_'
    days = int(days)
    dst = _get_logs_dir(deployment)
    if os.path.exists(dst) and not os.path.isdir(dst):
        raise ValueError('Destination must be a folder')
    if not os.path.exists(dst):
        os.mkdir(dst)
    if access:
        _fetch_logs('access', vhost, days, dst)
    if error:
        _fetch_logs('error', vhost, days, dst)
