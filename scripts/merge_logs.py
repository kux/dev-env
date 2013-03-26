import copy
import datetime
import os
import re
import sys
import time


APACHE_TIMESTAMP_REGEX = re.compile(r'\[(\d\d)/(\w\w\w)/(\d\d\d\d):(\d\d):(\d\d):(\d\d) -\d*\]')

MONTHS = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
          'Jul': 7, 'Aug': 8, 'Sep': 9, 'Nov': 10, 'Oct': 11, 'Dec': 12}


def _get_timestamp_from_log_line(line):
    match = re.search(APACHE_TIMESTAMP_REGEX, line)
    if match:
        day, month, year, hour, mn, sec = match.groups()
        return datetime.datetime(int(year), MONTHS[month], int(day), int(hour), int(mn), int(sec))
    else:
        raise ValueError("Line %s doesn't contian a timestamp in expected format" % line)


def _skip_empty_logs(current_lines, fds):
    indexes_to_remove = set()
    for index, line in enumerate(current_lines[:]):
        if line == '':
            indexes_to_remove.add(index)
    current_lines[:] = [ln for (i, ln) in enumerate(current_lines)
                        if i not in indexes_to_remove]
    fds[:] = [fd for (i, fd) in enumerate(fds) if i not in indexes_to_remove]


def _nway_merge(logs, merged_log, burst_regex, burst_delta=5):
    fds = [open(log) for log in logs]
    fds_copy = copy.copy(fds)
    merged_fd = open(merged_log, 'w')
    post_log_fd = open(merged_log + '.post', 'w')
    prev_post = 0
    prev_post_line = ''
    prev_is_written = False
    try:
        current_lines = [fd.readline() for fd in fds]
        _skip_empty_logs(current_lines, fds)
        timestamps = [_get_timestamp_from_log_line(ln) for ln in current_lines]
        while fds:
            assert len(timestamps) == len(current_lines) == len(fds)
            min_timestamp = min(timestamps)
            min_index = timestamps.index(min_timestamp)
            line_to_write = current_lines[min_index]
            merged_fd.write(line_to_write)
            is_post = re.search(burst_regex, line_to_write) is not None
            if is_post:
                post_time = time.mktime(min_timestamp.timetuple())
                if post_time < prev_post + burst_delta:
                    if not prev_is_written:
                        post_log_fd.write('\n--- new burst ---\n')
                        post_log_fd.write(prev_post_line)
                    post_log_fd.write(line_to_write)
                    prev_is_written = True
                else:
                    prev_is_written = False
                prev_post = post_time
                prev_post_line = line_to_write
            new_line = fds[min_index].readline()
            if new_line != '':
                current_lines[min_index] = new_line
                timestamps[min_index] = _get_timestamp_from_log_line(new_line)
            else:
                del current_lines[min_index]
                del fds[min_index]
                del timestamps[min_index]
    finally:
        for fd in fds_copy:
            fd.close()
        merged_fd.close()
        post_log_fd.close()



def merge_logs(logs_dir, burst_regex, burst_delta):
    log_files = os.listdir(logs_dir)
    logs_by_day = {}
    log_regex = r'(?:(\w*)_)?(access|error)\.log(?:\.(\d+))?\.(\w+)'
    for log_file in log_files:
        match = re.search(log_regex, log_file)
        if match:
            vhost, log_type, day, host = match.groups()
            if host == 'post':
                continue
            logs_by_day.setdefault((vhost, log_type, day), []).append(os.path.join(logs_dir, log_file))
    for details, logs in logs_by_day.iteritems():
        vhost, log_type, day = details
        aggregated_log = '%s.log' % log_type
        if vhost:
            aggregated_log = '%s_%s' % (vhost, aggregated_log)
        if day:
            aggregated_log = '%s.%s' % (aggregated_log, day)
        aggregated_log = os.path.join(logs_dir, aggregated_log)
        _nway_merge(logs, aggregated_log, burst_regex, burst_delta)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage: python merge_logs.py logs_dir burst_regex burst_delta'
    _, logs_dir, burst_regex, burst_delta = sys.argv
    burst_regex = re.compile(burst_regex)
    merge_logs(logs_dir, burst_regex, int(burst_delta))
