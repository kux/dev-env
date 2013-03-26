import copy
import datetime
import os
import re
import time

from optparse import OptionParser


def _nway_merge(dst, logs, destination_log, concurrent_post_delta=5):
    months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
              'Jul': 7, 'Aug': 8, 'Sep': 9, 'Nov': 10, 'Oct': 11, 'Dec': 12}
    try:
        fds = [open(log) for log in logs]
    except IOError:
        # if one of the files failes to open fds will point at the last succesfully opened file
        # the previous opened files are instantly closed by garbage collection
        try:
            fds.close()
        except NameError:
            # no file got opened
            pass
    else:
        fds_copy = copy.copy(fds)
        destination_fd = open(destination_log, 'w')
        post_log_fd = open(destination_log + '.post', 'w')
        prev_post = 0
        prev_post_line = ''
        prev_is_written = False
        try:
            current_lines = [fd.readline() for fd in fds]
            while fds:
                dates = []
                for index, line in enumerate(current_lines[:]):
                    if line == '':
                        del fds[index]
                        del current_lines[index]
                    else:
                        match = re.search(r'\[(\d\d)/(\w\w\w)/(\d\d\d\d):(\d\d):(\d\d):(\d\d) -\d*\]', line)
                        if match:
                            day, month, year, hour, mn, sec = match.groups()
                            ordered_tup = (int(year), months[month], int(day), int(hour), int(mn), int(sec))
                            dates.append(ordered_tup)
                if dates:
                    min_date = min(dates)
                    min_index = dates.index(min_date)
                    to_write = current_lines[min_index]
                    destination_fd.write(to_write)
                    is_post = re.search(r'request="POST', to_write) is not None
                    if is_post:
                        year, month, day, hour, mn, sec = min_date
                        post_time = time.mktime(datetime.datetime(year, month, day, hour, mn, sec).timetuple())
                        if post_time < prev_post + concurrent_post_delta:
                            if not prev_is_written:
                                post_log_fd.write('\n----------------new burst----------------\n')
                                post_log_fd.write(prev_post_line)
                            post_log_fd.write(to_write)
                            prev_is_written = True
                        else:
                            prev_is_written = False
                        prev_post = post_time
                        prev_post_line = to_write

                    current_lines[min_index] = fds[min_index].readline()
        finally:
            for fd in fds_copy:
                fd.close()
            destination_fd.close()
            post_log_fd.close()


def merge_logs(logs_dir, hosts, vhost='', days=0):
    if vhost:
        vhost = vhost + '_'
    days = int(days)

    def do_merge(day=None):
        base_log_path = os.path.join(logs_dir, '%saccess.log' % vhost)
        if day is not None:
            base_log_path = '%s.%d' % (base_log_path, day)
        logs = ['%s.%s' % (base_log_path, host) for host in hosts]
        destination_log = '%s/%saccess.log' % (logs_dir, vhost)
        if day:
            destination_log = '%s.%d' % (destination_log, day)
        _nway_merge(logs_dir, logs, destination_log)
        
    do_merge(None)
    for day in xrange(1, days + 1):
        do_merge(day)


if __name__ == '__main__':
    parser = OptionParser()
