interface=$1
delay=$2
port=$3
tc qdisc add dev $interface handle 1: root htb
tc class add dev $interface parent 1: classid 1:1 htb rate 100Mbps
tc qdisc add dev $interface parent 1:1 handle 10: netem delay $delay
tc filter add dev $interface protocol ip parent 1: prio 1 u32 match ip dport $port 0xffff flowid 1:1

# Example for doing ip filtering. In the example below 0x01020101 is the hex reprezentation of the ip (1.2.1.1)
# tc filter add dev lo protocol ip parent 1: prio 1 u32 match u32  0xffffffff at 12 flowid 1:1

