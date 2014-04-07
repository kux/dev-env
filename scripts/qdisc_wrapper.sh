interface=$1
delay=$2
pattern=$3
mask=$4
offset=$5
tc qdisc add dev $interface handle 1: root htb
tc class add dev $interface parent 1: classid 1:1 htb rate 100Mbps
tc qdisc add dev $interface parent 1:1 handle 10: netem delay $delay
tc filter add dev lo protocol ip parent 1: prio 1 u32 match u32 $pattern $mask at $offset flowid 1:1

# tc qdisc del dev $interface root 
