import os
import re
from parameters import *
import struct
import math

packet_format=PACKET_FORMAT

def revdata(): 
    # 指定文件夹路径
    folder_path = './packets/'  # 替换为您的实际文件夹路径

    # 获取指定路径下的所有文件夹名
    folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

    # 打印所有文件夹名
    for folder_name in folders:
        folder_files = os.listdir(os.path.join(folder_path, folder_name))
        # 定义正则表达式来匹配以 "s" 开头后面的数字
        pattern = re.compile(r's(\d+)-')

        # 在示例文件名中查找匹配的数字
        match = pattern.search(folder_name)
        monitor_id=int(match.group(1))
        print(monitor_id)
        if monitor_id%(N_SWITCH/N_MONITOR)!=1:
            continue
        orbit_id=int((monitor_id-1)/N_SWITCH)
        # for packet in folder_files:
        packet=folder_files[0]
        pcap_file = open(folder_path+folder_name+'/'+packet, "rb")
        while True:
            # pcap_file_one=pcap_file.read()
            # print(pcap_file_one)
            pcap_file_one=pcap_file.read(20)
            if not pcap_file:
                break  # 到达文件末尾退出循环
            if len(pcap_file_one)<20:
                break
            try:
            # 尝试获取数据块的长度
                flag, T_head0, T_tail0, T_head1, T_tail1, hop , switch_id= struct.unpack(packet_format, pcap_file_one)
            except Exception as e:
            # 如果无法获取长度，输出错误信息并退出循环
                print("Error occurred while getting chunk length:", e,monitor_id)
                break
            flag, T_head0, T_tail0, T_head1, T_tail1, hop , switch_id= struct.unpack(packet_format, pcap_file_one)
            print(flag, T_head0, T_tail0, T_head1, T_tail1, hop , switch_id)
            if switch_id==0:
                continue
            direction=flag&1

            tail_id=switch_id
            if direction==0:
                head_id=monitor_id-hop+1
                if math.floor((head_id-1)/N_SWITCH)!=orbit_id:
                    head_id+=N_SWITCH
            else:
                head_id=monitor_id+hop-1
                if math.floor((head_id-1)/N_SWITCH)!=orbit_id:
                    head_id-=N_SWITCH
            # print(head_id,tail_id)
            link0=str(head_id)+'-'+str(tail_id)+".txt"
            link1=str(tail_id)+'-'+str(head_id)+".txt"

            # 检查文件是否存在
            link_file = open("./links/"+link0, "a")
            if FLAG==0:
                ans=str(T_tail0-T_head0)+'\n'
            if FLAG==1:
                ans=str((T_head0-T_tail0)/T_tail0)+'\n'
            link_file.write(ans)

            link_file = open("./links/"+link1, "a")
            if FLAG==0:
                ans=str(T_tail1-T_head1)+'\n'
            if FLAG==1:
                ans=str((T_head1-T_tail1)/T_tail1)+'\n'
            link_file.write(ans)

if __name__=="__main__":
    revdata()