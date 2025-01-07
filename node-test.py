from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI

from p4_mininet import P4Switch, P4Host
from p4runtime_switch import P4RuntimeSwitch

import argparse
from time import sleep

from init_switch import *


parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", required=True)
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--num-hosts', help='Number of hosts to connect to switch',
                    type=int, action="store", default=1)
parser.add_argument('--mode', choices=['l2', 'l3'], type=str, default='l3')
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)
parser.add_argument('--pcap-dump', help='Dump packets on interfaces to pcap files',
                    type=str, action="store", required=False, default=False)

args = parser.parse_args()

linkopts=dict(bw=10,delay='5ms',loss=0,max_queue_size=10000,use_htb=True)
# (or you can use brace syntax: linkopts={'bw':10,'delay':'5ms',...})
# self.addLink(node1,node2,**linkopts)

class SingleSwitchTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, pcap_dump, n_host, n_switch,n_orbit, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        self.n_orbit=n_orbit
        self.n_switch=n_switch
        self.n_host=n_host
        self.allswitches=[]
        self.allhosts=[]
        self.sw_path=sw_path
        self.sw_path = sw_path
        self.json_path = json_path
        self.thrift_port = thrift_port
        self.pcap_dump = pcap_dump                        
        for i in range(self.n_orbit):
            self.build_ring(i)
        print(self.allswitches)
        for i in range(self.n_orbit):
            self.addLink(self.allswitches[i][0],self.allswitches[(i+1)%self.n_orbit][1],4,5)


    def build_ring(self,orbit_id):
        n_switch_built=orbit_id*self.n_switch
        switches = [self.addSwitch(f's{n_switch_built+i+1}',
                                sw_path = self.sw_path,
                                json_path = self.json_path,
                                thrift_port = self.thrift_port+n_switch_built+i,
                                pcap_dump = self.pcap_dump) for i in range(self.n_switch)]
        self.allswitches.append(switches)
        for i in range(self.n_switch):
            for j in range(self.n_host):
                host = self.addHost(f'h{(n_switch_built+i) * self.n_host + j + 1}',cpu=1/ self.n_host*self.n_switch*self.n_orbit)
                self.addLink(host, switches[i], bw=100, delay='5ms', loss=0, use_htb=True)
                self.allhosts.append(host)
        for i in range(self.n_switch):
            # if i > 0:
            #     self.addLink(switches[i], switches[(i+1)%self.n_switch])
            self.addLink(switches[i], switches[(i+1)%self.n_switch],2,3)

        
def main():
    num_hosts = args.num_hosts
    mode = args.mode
    topo = SingleSwitchTopo(args.behavioral_exe,
                            args.json,
                            args.thrift_port,
                            args.pcap_dump,
                            n_host=1,n_switch=2,n_orbit=2)
    
    net = Mininet(topo = topo,
                  host = P4Host,
                  switch = P4RuntimeSwitch,
                  controller = None)
    net.start()
    sw_mac = ["00:aa:bb:00:00:%02x" % n for n in range(num_hosts)]
    sw_addr = ["10.0.%d.1" % n for n in range(num_hosts)]
    for n in range(num_hosts):
        h = net.get('h%d' % (n + 1))
        if mode == "l2":
            h.setDefaultRoute("dev eth0")
        else:
            h.setARP(sw_addr[n], sw_mac[n])
            h.setDefaultRoute("dev eth0 via %s" % sw_addr[n])
    for n in range(num_hosts):
        h = net.get('h%d' % (n + 1))
        h.describe()
    print("Ready !")
    RoutingController(topo=topo)
    CLI( net )
    # net.stop()
if __name__ == '__main__':
    setLogLevel( 'info' )
    main()
