import os.path

from fabric.api import env
from fabric.operations import get


env.hosts = ['root@ec2-23-23-66-181.compute-1.amazonaws.com', 'root@ec2-54-234-73-236.compute-1.amazonaws.com']


def _fetch_logs(log_type, remote_logs_dir, vhost, days, dst):
    src = os.path.join(remote_logs_dir, '%s%s.log' % (vhost, log_type))
    filename = os.path.basename(src)
    get(src, '%s/%s.%s' % (dst, filename, env.host))
    for day in xrange(days):
        src = os.path.join(remote_logs_dir, '%s%s.log.%d' % (vhost, log_type, day + 1))
        filename = os.path.basename(src)
        get(src, os.path.join(dst, '%s.%s' % (filename, env.host)))


def fetch_logs(dst, remote_logs_dir='/var/log/httpd', vhost='', days=0, access=True, error=False):
    if vhost:
        vhost = vhost + '_'
    days = int(days)

    if os.path.exists(dst) and not os.path.isdir(dst):
        raise ValueError('Destination must be a folder')
    if not os.path.exists(dst):
        os.mkdir(dst)
    if access:
        _fetch_logs('access', remote_logs_dir, vhost, days, dst)
    if error:
        _fetch_logs('error', remote_logs_dir, vhost, days, dst)
