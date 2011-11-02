#!/bin/sh
#
#
# set routes and forwarding to connect the
# Ben NanoNote with the net.
#
# created: 2010/5

iptables -t nat -F
ip addr add 192.168.254.100/24 dev usb0
ip link set usb0 up
ip route add 192.168.254.101 dev usb0
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -j MASQUERADE
