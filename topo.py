from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink

from p4_mininet import P4Switch, P4Host
from p4runtime_switch import P4RuntimeSwitch

import argparse
from time import sleep
from parameters import *
parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", required=True)
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--num-hosts', help='Number of hosts to connect to switch',
                    type=int, action="store", default=2)
parser.add_argument('--mode', choices=['l2', 'l3'], type=str, default='l3')
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)
parser.add_argument('--pcap-dump', help='Dump packets on interfaces to pcap files',
                    type=str, action="store", required=False, default=False)

args = parser.parse_args()
linkopts=dict(bw=BW, delay=DELAY, loss=LOSS,max_queue_size=10000,use_htb=True)

class SingleSwitchTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, pcap_dump, n, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1')
        for h in range(n):
            host = self.addHost('h%d' % (h + 1))
            self.addLink(host, switch,cls=TCLink,bw=BW, delay=DELAY, loss=LOSS)
def main():
    num_hosts = args.num_hosts
    mode = args.mode
    topo = SingleSwitchTopo(args.behavioral_exe,
                            args.json,
                            args.thrift_port,
                            args.pcap_dump,
                            num_hosts)
    net = Mininet(topo = topo)
    net.start()
    print("Ready !")
    CLI( net )
    # net.stop()
if __name__ == '__main__':
    setLogLevel( 'info' )
    main()


# from mininet.net import Mininet
# from mininet.topo import Topo
# from mininet.node import CPULimitedHost, OVSSwitch
# from mininet.link import TCLink
# from mininet.log import setLogLevel
# from mininet.cli import CLI
# from mininet.node import RemoteController
# from p4_mininet import P4Switch, P4Host
# from p4runtime_switch import P4RuntimeSwitch

# n_orbit=5
# n_switch=5
# n_host=1

# class RingTopology(Topo):
        
#     def build_ring(self,orbit_id):
#         n_switch_built=orbit_id*n_switch
#         switches = [self.addSwitch(f's{n_switch_built+i+1}', cls=BMv2Switch, json='p4src/point1.json') for i in range(self.n_switch)]
#         self.allswitches.append(switches)
#         for i in range(self.n_switch):
#             for j in range(self.n_host):
#                 host = self.addHost(f'h{(n_switch_built+i) * self.n_host + j + 1}', cpu=1/ self.n_host*self.n_switch*self.n_orbit)
#                 self.addLink(host, switches[i], bw=10, delay='5ms', loss=0, use_htb=True)
#                 self.allhosts.append(host)
#         for i in range(self.n_switch):
#             # if i > 0:
#             #     self.addLink(switches[i], switches[(i+1)%self.n_switch])
#             self.addLink(switches[i], switches[(i+1)%self.n_switch])

#     def build(self):
#         self.n_orbit=n_orbit
#         self.n_switch=n_switch
#         self.n_host=n_host
#         self.allswitches=[]
#         self.allhosts=[]
#         for i in range(self.n_orbit):
#             self.build_ring(i)
#         print(self.allswitches)
#         for i in range(self.n_orbit):
#             self.addLink(self.allswitches[i][1],self.allswitches[(i+1)%self.n_switch][2])
        

# def create_ring_topology():
#     n_orbit=5
#     n_switch=5
#     n_host=1
#     topo = RingTopology()
#     net = Mininet(topo=topo, host=CPULimitedHost, switch=OVSSwitch, link=TCLink)
    
#     net.start()
    
#     print("Dumping host connections")
#     h1, h2, h3, h4 = net.get('h1', 'h2', 'h3', 'h4')  
#     print(h1)
#     CLI(net)
#     # net.iperf((h1, h2))
    
#     # net.pingAll()
#     # net.stop()

# if __name__ == '__main__':
#     setLogLevel('info')
#     create_ring_topology()