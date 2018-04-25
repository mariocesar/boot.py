import datetime
import getpass
import os
import platform
import pwd
import socket
import sys
import time


def collect_python_facts():
    return {
        'version': {
            'major': sys.version_info[0],
            'minor': sys.version_info[1],
            'micro': sys.version_info[2],
            'releaselevel': sys.version_info[3],
            'serial': sys.version_info[4]
        },
        'version_info': list(sys.version_info),
        'executable': sys.executable,
    }


def collect_env_facts():
    # Collect environment facts
    env_facts = {}

    for k, v in os.environ.items():
        env_facts[k] = v

    return env_facts


def collect_user_facts():
    user_facts = dict()
    user_facts['id'] = getpass.getuser()

    pwent = pwd.getpwnam(getpass.getuser())
    user_facts['uid'] = pwent.pw_uid
    user_facts['gid'] = pwent.pw_gid
    user_facts['gecos'] = pwent.pw_gecos
    user_facts['dir'] = pwent.pw_dir
    user_facts['shell'] = pwent.pw_shell
    user_facts['real_user_id'] = os.getuid()
    user_facts['effective_user_id'] = os.geteuid()
    user_facts['real_group_id'] = os.getgid()
    user_facts['effective_group_id'] = os.getgid()

    return user_facts


def collect_platform_facts():
    # Platform
    platform_facts = {}
    # platform.system() can be Linux, Darwin, Java, or Windows
    platform_facts['system'] = platform.system()
    platform_facts['kernel'] = platform.release()
    platform_facts['machine'] = platform.machine()

    platform_facts['python_version'] = platform.python_version()
    platform_facts['fqdn'] = socket.getfqdn()
    platform_facts['hostname'] = platform.node().split('.')[0]
    platform_facts['nodename'] = platform.node()
    platform_facts['domain'] = '.'.join(platform_facts['fqdn'].split('.')[1:])
    platform_facts['arch'] = platform.architecture()[0]
    return platform_facts


def collect_network_facts():
    from boot import run

    hostname = platform.node().split('.')[0]
    ipv4 = [line for line in run('cat /etc/hosts').out.strip().split('\n') if hostname in line].pop()
    ipv4 = ipv4.rstrip('app').strip()

    return {
        'hostname': hostname,
        'ipv4': ipv4
    }


def collect_datetime_facts():
    date_time_facts = {}

    now = datetime.datetime.now()
    date_time_facts['year'] = now.strftime('%Y')
    date_time_facts['month'] = now.strftime('%m')
    date_time_facts['weekday'] = now.strftime('%A')
    date_time_facts['weekday_number'] = now.strftime('%w')
    date_time_facts['weeknumber'] = now.strftime('%W')
    date_time_facts['day'] = now.strftime('%d')
    date_time_facts['hour'] = now.strftime('%H')
    date_time_facts['minute'] = now.strftime('%M')
    date_time_facts['second'] = now.strftime('%S')
    date_time_facts['epoch'] = now.strftime('%s')
    date_time_facts['date'] = now.strftime('%Y-%m-%d')
    date_time_facts['time'] = now.strftime('%H:%M:%S')
    date_time_facts['iso8601_micro'] = now.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    date_time_facts['iso8601'] = now.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    date_time_facts['iso8601_basic'] = now.strftime("%Y%m%dT%H%M%S%f")
    date_time_facts['iso8601_basic_short'] = now.strftime("%Y%m%dT%H%M%S")
    date_time_facts['tz'] = time.strftime("%Z")
    date_time_facts['tz_offset'] = time.strftime("%z")

    return date_time_facts
