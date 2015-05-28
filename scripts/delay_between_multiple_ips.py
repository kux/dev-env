#! /usr/bin/python
import sys
import subprocess


def run_command(command):
    print command
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


delay_confs = [
    ('2000000', '1.1.2.2', '1.2.1.1', 'udp'),
    ('65000000', '1.1.2.1', '1.2.1.1', 'tcp'),
]


if __name__ == "__main__":
    interface = sys.argv[1]
    run_command('tc qdisc del dev %s root' % interface)
    run_command("tc qdisc add dev %s handle 1: root htb" % interface)

    protocols = {
        'tcp': '0x06',
        'udp': '0x11',
        'icmp': '0x01',
    }

    for no, delay_conf in enumerate(delay_confs):
        no += 1
        delay, ip1, ip2, protocol = delay_conf
        protocol = protocols[protocol]
        run_command("tc class add dev %s parent 1: classid 1:%d htb rate 100Mbps" % (interface, no))
        handle = no + 10
        run_command("tc qdisc add dev %s parent 1:%d handle %d: netem delay %s" % (interface, no, handle, delay))
        run_command("tc filter add dev %s protocol ip parent 1: prio 1 u32 "
                    "match u32 %s 0xffffffff at 12 "
                    "match u32 %s 0xffffffff at 16 "
                    "match u8 %s 0xff at 9 flowid 1:%d" % (
                        interface, ip_to_hex(ip1), ip_to_hex(ip2), protocol, no))
