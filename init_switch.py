#coding:utf-8
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from parameters import *

class RoutingController(object):

    def __init__(self,topo):
        
        self.direct_sw_to_host = {}
        self.direct_host_to_sw = {}
        self.sw_entries = {}
        self.register_num = 1
        self.sw_counters = {} #字典:{"sw1":{0:list=[0]*64}}
        self.sw_sketches = {} #字典 
        # self.topo = load_topo('topology.json')
        self.topo=topo
        self.controllers = {}
        self.sw_conterindex = {}
        self.sw_list = []
        self.init()

    def init(self):
        self.connect_to_switches()
        self.init_mc()
        self.init_registers()


    def connect_to_switches(self):
        i=0
        for p4orbits in self.topo.allswitches:
            for p4switch in p4orbits:
                print(p4switch)
                self.sw_list.append(p4switch)
                self.sw_entries[p4switch] = {}
                self.sw_counters[p4switch] = {}  
                thrift_port = self.topo.thrift_port+i
                self.controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port)
                self.controllers[p4switch].print_ = False
                i=i+1


    
    def init_registers(self):
        for switch_name in self.controllers.keys():
            controller=self.controllers[switch_name]
            
            switch_type=0
            switch_id=int(switch_name[1:])
            controller.register_write("switch_id_register", index=0, value=switch_id)
            if switch_id%(N_SWITCH/N_MONITOR)==1:
                switch_type=1
            controller.register_write("switch_type_register", index=0, value=switch_type)
            for port_id in range(8):
                controller.register_write("counter0", index=port_id, value=0)
                controller.register_write("counter1", index=port_id, value=0)
            



    
    def init_mc(self):
        for switch_name in self.controllers.keys():
            controller=self.controllers[switch_name]

            headl_id=0

            controller.mc_mgrp_create(1)  # 创建多播组
            # 添加节点到多播组
            nodes = [[2],[3],[4,5]]  # 节点列表
            for node_id in range(len(nodes)):
                ports=nodes[node_id]
                controller.mc_node_create(node_id,ports)  # 将节点添加到多播组
            # 关联节点与多播组
            node_id = 0  # 要关联的节点ID
            for i in range(len(nodes)):
                controller.mc_node_associate(1, headl_id)  # 将节点与多播组关联
                headl_id+=1

            controller.mc_mgrp_create(2)  # 创建多播组
            # 添加节点到多播组
            nodes = [[2]]  # 节点列表
            for node_id in range(len(nodes)):
                ports=nodes[node_id]
                controller.mc_node_create(node_id+headl_id,ports)  # 将节点添加到多播组
            # 关联节点与多播组
            for i in range(len(nodes)):
                controller.mc_node_associate(2, headl_id)  # 将节点与多播组关联
                headl_id+=1

            controller.mc_mgrp_create(3)  # 创建多播组
            # 添加节点到多播组
            nodes = [[3]]  # 节点列表
            for node_id in range(len(nodes)):
                ports=nodes[node_id]
                controller.mc_node_create(node_id+headl_id,ports)  # 将节点添加到多播组
            # 关联节点与多播组
            for i in range(len(nodes)):
                controller.mc_node_associate(3, headl_id)  # 将节点与多播组关联
                headl_id+=1


            controller.mc_mgrp_create(4)  # 创建多播组
            # 添加节点到多播组
            nodes = [[4]]  # 节点列表
            for node_id in range(len(nodes)):
                ports=nodes[node_id]
                controller.mc_node_create(node_id+headl_id,ports)  # 将节点添加到多播组
            # 关联节点与多播组
            for i in range(len(nodes)):
                controller.mc_node_associate(4, headl_id)  # 将节点与多播组关联
                headl_id+=1

            controller.mc_mgrp_create(5)  # 创建多播组
            # 添加节点到多播组
            nodes = [[5]]  # 节点列表
            for node_id in range(len(nodes)):
                ports=nodes[node_id]
                controller.mc_node_create(node_id+headl_id,ports)  # 将节点添加到多播组
            # 关联节点与多播组
            for i in range(len(nodes)):
                controller.mc_node_associate(5, headl_id)  # 将节点与多播组关联
                headl_id+=1

            controller.mc_mgrp_create(128)  # 创建多播组
            # 添加节点到多播组
            nodes = [[1]]  # 节点列表
            for node_id in range(len(nodes)):
                ports=nodes[node_id]
                controller.mc_node_create(node_id+headl_id,ports)  # 将节点添加到多播组
            # 关联节点与多播组
            for i in range(len(nodes)):
                controller.mc_node_associate(128, headl_id)  # 将节点与多播组关联
                headl_id+=1

            controller.mc_mgrp_create(23)  # 创建多播组
            # 添加节点到多播组
            nodes = [[2,3]]  # 节点列表
            for node_id in range(len(nodes)):
                ports=nodes[node_id]
                controller.mc_node_create(node_id+headl_id,ports)  # 将节点添加到多播组
            # 关联节点与多播组
            for i in range(len(nodes)):
                controller.mc_node_associate(23, headl_id)  # 将节点与多播组关联
                headl_id+=1



