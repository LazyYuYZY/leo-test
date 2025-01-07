#!/usr/bin/env python3
import socket
import random
import os
import struct
import fcntl
import time
import pickle
import threading
from parameters import *

tos_temp = 4
loss_rate = 0.01
loss_num = 0
file_name = ""
g_src_ip = ""
g_dst_ip = ""
g_src_mac = ""
g_dst_mac = ""

protocol_udp=17
protocol_tcp=6
protocol_detection=12 #探测包
protocol_test=13 #自检包

# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0
    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = (msg[i] << 8) + msg[i+1]
        s = s + w

    s = (s>>16) + (s & 0xffff)
    #s = s + (s >> 16)    #complement and mask to 4 byte short
    s = ~s & 0xffff

    return s

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])



def decetion_header():
    #状态码
    flag=FLAG
    forwording=0 #转发
    direction=0 #方向
    fb_state=0 #状态:0返回的第一个节点1非第一个节点
    flag=(flag<<3)+(forwording<<2)+(fb_state<<1)+direction
    # flag=flag<<8

    #时间戳
    T_head0=0
    T_tail0=0
    T_head1=0
    T_tail1=0
    #数据标识链路
    hop=0
    switch_id=0

    header = struct.pack(PACKET_FORMAT, flag, T_head0, T_tail0, T_head1, T_tail1, hop , switch_id)

    return header

def getInterfaceName():
    #assume it has eth0

    return [x for x in os.listdir('/sys/class/net') if "-eth1" in x]

def create_packet(src_ip, dst_ip, sport, dport, proto, id, ttl):
    # 新增
    transport_header=decetion_header()
    # return eth_h + ip_header(src_ip, dst_ip, ttl, proto,id) + transport_header
    return transport_header

def get_random_flow():
    # src_ip = socket.inet_ntoa(struct.pack("!I", random.randint(167772160, 4261412864)))
    # dst_ip = socket.inet_ntoa(struct.pack("!I", random.randint(167772160, 4261412864)))
    # sport = random.randint(1, 2 ** 16 - 2)
    # dport = random.randint(1, 2 ** 16 - 2)
    # ip_id = random.randint(1, 2 ** 16 - 2)
    # protocol = random.choice([6])
    src_ip = g_src_ip
    dst_ip = g_dst_ip
    sport = 666
    dport = 888
    ip_id = random.randint(1, 2 ** 16 - 2)
    protocol = protocol_udp
    return (src_ip, dst_ip, sport, dport, protocol, ip_id)

def save_flows(flows):
    with open("sent_flows.pickle", "wb") as f:
        pickle.dump(flows, f)

def create_test(n_packets, n_drops, fail_hops):
    global loss_num

    loss_num = 0

    packets_to_send = []

    assert n_packets >= n_drops

    for i in range(n_packets):
        if random.random() < loss_rate:
            packets_to_send.append(get_random_flow() + (fail_hops,))
            # print("2222")
            loss_num += 1
        else:
            packets_to_send.append(get_random_flow() + (64,))

    # for i in range(int(n_packets-n_drops)):
    #     packets_to_send.append(get_random_flow() + (64,))

    # for i in range(int(n_drops)):
    #     packets_to_send.append(get_random_flow() + (fail_hops,))

    return packets_to_send


def sendpkt(intf_name,n_packets, n_drops, fail_hops):
    send_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    send_socket.bind((intf_name, 0))

    flows = create_test(n_packets, n_drops, fail_hops)
    for flow in flows:
        # if flow[-1] < 10:
        #     print(flow)
        packet = create_packet(*flow)
        send_socket.send(packet)
        time.sleep(0.001)

    send_socket.close()



def main(n_packets, n_drops, fail_hops):

    
    intf_names = getInterfaceName()
    # 创建并启动一个线程来监听每个端口
    threads = []


    for intf_name in intf_names:
        print(intf_name)
        switch=intf_name.split('-')[0]
        switch_id=int(switch[1:])
        print(switch_id)
        # if switch_id%3==0:
        if True:
            thread = threading.Thread(target=sendpkt, args=(intf_name,n_packets, n_drops, fail_hops,))
            threads.append(thread)
            thread.start()
    # 等待所有线程结束
    for thread in threads:
        thread.join()
    
    

sleep_time = 0

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--n-pkt', help='number of packets', type=int, required=False, default=50)
    parser.add_argument('--n-drops', help='number of packts to drop',type=float, required=False, default=0)
    parser.add_argument('--fail-hops', help='Number of hops until packet is dropped, can be random', type=int, required=False, default=2)
    parser.add_argument('--loss-rate', help='丢包率', type=float, required=False, default=0.5)
    args= parser.parse_args()
    loss_rate = args.loss_rate

    # main(args.n_pkt, args.n_drops, int(args.fail_hops))
    # tos_temp = tos_temp^1
    # file_name = "sent_flows____{}.pickle".format(tos_temp)
    # main(args.n_pkt, args.n_drops, int(args.fail_hops))
    # print ("send ok: {}".format(tos_temp))
    n = 0
    while True:
        # 需要修正！！！1129
        # tos_temp = tos_temp^1  
        # file_name = "sent_flows____{}.pickle".format(tos_temp)
        g_src_ip = "10.13.1.2"
        g_src_mac = "00:00:0a:0d:01:02"
        dst_set = [("10.20.8.2","00:00:0a:14:08:02")]
        # dst_set = [("10.20.8.2","00:00:0a:14:08:02"), ("10.14.2.2","00:00:0a:0e:02:02"),("10.15.3.2","00:00:0a:0f:03:02")]
        # dst_set = [("10.20.8.2","00:00:0a:14:08:02")]
        sleep_time = 5/args.n_pkt/len(dst_set)
        for ip, mac in dst_set:
            g_dst_ip = ip
            g_dst_mac = mac
            main(args.n_pkt, args.n_drops, int(args.fail_hops))
            print("number of loss packet:{}".format(loss_num))

        print ("send ok: {}".format(tos_temp))

        time.sleep(1)
        n += 1
        if n == 1:
            break


