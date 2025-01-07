import socket
import os
import threading
import time
from parameters import *
from socket import SOL_SOCKET,SO_REUSEADDR,SO_SNDBUF,SO_RCVBUF

# 定义数据包格式
packet_format = PACKET_FORMAT

def recv_packet(eth_name):
    # 创建套接字并绑定到端口
    recv_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,socket.ntohs(3))
    recv_socket.bind((eth_name, 0))  # 假设绑定到 eth0 接口
    recv_socket.settimeout(10)



    # sk =recv_socket
    # sk.setsockopt(SOL_SOCKET,SO_SNDBUF,32*1024)
    # print('>>>>',sk.getsockopt(SOL_SOCKET,SO_SNDBUF))
    # print('>>>>',sk.getsockopt(SOL_SOCKET,SO_RCVBUF))


    # 初始化数据包计数器
    packet_count = 0
    start_time=time.time()
    folder_name="./packets/"+eth_name
    if not os.path.exists(folder_name):
        # 如果文件夹不存在，创建文件夹
        os.makedirs(folder_name)
    # 创建 pcap 文件
    filename = folder_name+"/captured_packets.txt"
    pcap_file = open(filename, "ab")
    try:
        while True:

            packet,addr= recv_socket.recvfrom(65565)  # 接收数据包
            # print(packet)
            if len(packet)!=20:
                continue
            # 创建 pcap 文件
            # filename = folder_name+"/captured_packets_" + str(packet_count).zfill(5) + ".txt"
            # pcap_file = open(filename, "wb")
            pcap_file.write(packet)
            # pcap_file.close()

            # 数据包计数器递增
            packet_count += 1
            
            

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")

    finally:
        # 关闭套接字和 pcap 文件
        recv_socket.close()
        pcap_file.close()
        


if __name__ == "__main__":
    eths=[x for x in os.listdir('/sys/class/net') if "-eth1" in x]
    print(eths)
    # 创建并启动一个线程来监听每个端口
    threads = []


    for eth in eths:
        switch=eth.split('-')[0]
        switch_id=int(switch[1:])
        if True:
            thread = threading.Thread(target=recv_packet, args=(eth,))
            threads.append(thread)
            thread.start()
    # 等待所有线程结束
    for thread in threads:
        thread.join()