#! /usr/bin/python
import sys
import subprocess


def run_command(command):
    command = command.split()
    subp = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    out, err = subp.communicate()
    if out:
        print out
    if err:
        print err


def ip_to_hex(ip):
    hex_parts = [hex(int(p))[2:] for p in ip.split('.')]
    for i, part in enumerate(hex_parts):
        if len(part) == 1:
            hex_parts[i] = '0%s' % part
    return '0x%s' % ''.join(hex_parts)


if __name__ == "__main__":
    interface = sys.argv[1]
    delay = sys.argv[2]
    ip1 = sys.argv[3]
    ip2 = sys.argv[4]
    protocol = sys.argv[5]
    protocols = {
        'tcp': '0x06',
        'udp': '0x11',
        'icmp': '0x01',
    }
    protocol = protocols[protocol]
    run_command('tc qdisc del dev %s root' % interface)
    run_command("tc qdisc add dev %s handle 1: root htb" % interface)
    run_command("tc class add dev %s parent 1: classid 1:1 htb rate 100Mbps"% interface)
    run_command("tc qdisc add dev %s parent 1:1 handle 10: netem delay %s" % (interface, delay))
    run_command("tc filter add dev %s protocol ip parent 1: prio 1 u32 "
                "match u32 %s 0xffffffff at 12 "
                "match u32 %s 0xffffffff at 16 "
                "match u8 %s 0xff at 9 flowid 1:1" % (
                    interface, ip_to_hex(ip1), ip_to_hex(ip2), protocol))
