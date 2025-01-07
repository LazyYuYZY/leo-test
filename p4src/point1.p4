/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

//My includes
#include "include/headers_point1.p4"
#include "include/parsers_point1.p4"

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/





// register<timestamp_t>(2) T_revpkt_register;
// register<timestamp_t>(1) T_revpkt_threshold_register;


#define COUNTER_REGISTER(num) register<timestamp_t>(8) counter##num

#define COUNTER_COUNT(num, index_count) counter##num.read(meta.value_counter, index_count); \
meta.value_counter = meta.value_counter +1; \
counter##num.write(index_count, meta.value_counter)

#define COUNTER_READ(num, index_count) counter##num.read(meta.value_reader, index_count)





control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata){


    // 定义寄存器用于存储交换机的 ID/类型（是否为探测器下交换机）
    // 假设寄存器的索引为 0，存储的值为交换机的 ID/类型（是否为探测器下交换机）
    register<switch_id_t>(1) switch_id_register;
    register<switch_type_t>(1) switch_type_register;
    
    register<timestamp_t>(2) T_revpkt_register;
    register<timestamp_t>(1) T_revpkt_threshold_register;
    

    //左右节点数
    register<hop_t>(2) hop_register;

    //收包计数器
    COUNTER_REGISTER(1);

    action insert_T_tail0(){
        if(meta.packet_tpye==1){//丢包率
            hdr.detection_head.T_tail0=meta.N_revpkt;
        }else{//时延
            hdr.detection_head.T_tail0=standard_metadata.ingress_global_timestamp[31:0];
        }
    }

    action insert_T_tail1(){
        if(meta.packet_tpye==1){//丢包率
            hdr.detection_head.T_tail1=meta.N_revpkt;
        }else{//时延
            hdr.detection_head.T_tail1=standard_metadata.ingress_global_timestamp[31:0];
        }
    }

    action insert_linkmark(){
        hdr.detection_head.hop=hdr.detection_head.hop+1;
        switch_id_register.read(hdr.detection_head.switch_id,0);
    }

    action judge_ismonitor0(){
        if(meta.ismonitior[0:0]==1){//monitor收到返回的探测包
            standard_metadata.mcast_grp[8:0]=128;
        }
        else{
            standard_metadata.mcast_grp[1:1]=1;
            standard_metadata.mcast_grp[0:0]=hdr.detection_head.direction;
        }
    }

    action judge_ismonitor1(){
        if(meta.ismonitior[0:0]==1){//monitor收到发送的探测包
            standard_metadata.mcast_grp[8:0]=standard_metadata.ingress_port;
        }
        else{
            standard_metadata.mcast_grp=1;
        }
    }


    action drop(){
        mark_to_drop(standard_metadata);
    }

    apply {
        // 读取入端口的数据包数量
        COUNTER_COUNT(1,(bit<32>)standard_metadata.ingress_port);
        meta.N_revpkt=meta.value_counter;
        

        meta.packet_tpye=hdr.detection_head.packet_tpye;
        meta.forwording1=hdr.detection_head.forwording;
        meta.fb_state1=hdr.detection_head.fb_state;
        if(meta.packet_tpye>2){
            drop();
        }

        if(meta.packet_tpye==2){//自检包
            // 自检包逻辑
            if(meta.forwording1==1){
                if(){
                    standard_metadata.mcast_grp[1:1]=1;
                    standard_metadata.mcast_grp[0:0]=hdr.detection_head.direction;
                }
                else{
                    hop_register.write(hdr.detection_head.hop,hdr.detection_head.direction);
                    drop();
                }
            }
            else{
                insert_linkmark();
                standard_metadata.mcast_grp=23;//同轨多播组
            }
            return;
        }
        

        if(standard_metadata.ingress_port==1){//monitor发送探测包

            //同轨接收时间
            T_revpkt_register.read(meta.T_revpkt0,0);
            T_revpkt_register.read(meta.T_revpkt0,1);
            T_revpkt_threshold_register.read(meta.T_revpkt_threshold,0);
            if((meta.T_revpkt0!=0)&&(meta.T_revpkt0+meta.T_revpkt_threshold<standard_metadata.ingress_global_timestamp[31:])\
                &&(meta.T_revpkt1!=0)&&(meta.T_revpkt1+meta.T_revpkt_threshold<standard_metadata.ingress_global_timestamp[31:])){    
                meta.overthreshold==1;
            }
            else{
                meta.overthreshold==0;
            }
            
            //自检包跳数差
            if(meta.n_leftnodes)

            if(meta.n_leftnodes==meta.n_rightnodes||meta.n_leftnodes==meta.n_rightnodes+1){
                meta.temp_monitor=1;
            }
            

            switch_type_register.read(meta.ismonitior,0);
            if(meta.ismonitior==0&&meta.overthreshold==1){
                switch_type_register.write(2,0);
            }
            if(meta.ismonitior==2){
                if(meta.temp_monitor==1){
                    switch_type_register.write(3,0);
                }
                else{
                    switch_type_register.write(0,0);
                }
            }
            if(meta.ismonitior==3){
                if(meta.temp_monitor==1){
                    switch_type_register.write(3,0);
                }
                else{
                    switch_type_register.write(0,0);
                }
            }

            if(meta.ismonitior[1:1]==1){
                standard_metadata.mcast_grp=1;//向所有端口发送探测包
            }
            if(meta.ismonitior==0){
                drop();
            }
            if(meta.ismonitior==2){
                standard_metadata.mcast_grp=23;//向同轨端口发送自检包
            }
        }
        else{
            if(standard_metadata.ingress_port>3){//异轨
                if(meta.forwording1==0){//异轨收到探测包
                                      
                    hdr.detection_head.forwording=1;
                    hdr.detection_head.direction=1-hdr.detection_head.direction;
                    insert_T_tail0();
                    insert_linkmark();

                    standard_metadata.mcast_grp[8:0]=standard_metadata.ingress_port;
                }
                else{//收到异轨转发回的探测包
                    hdr.detection_head.fb_state=1;
                    insert_T_tail1();
                    judge_ismonitor0();
                }
            }
        
            else{//同轨
                T_revpkt_register.write(standard_metadata.ingress_global_timestamp,standard_metadata.ingress_port[0:0]);
                if(meta.forwording1==0){//同侧发送的探测包
                    insert_T_tail0();
                    insert_linkmark();
                    judge_ismonitor1();
                } 
                else{//同轨返回的探测包
                    if(meta.fb_state1==0){//测量链路的节点
                        hdr.detection_head.fb_state=1;
                        insert_T_tail1();
                    }
                    judge_ismonitor0();
                }
            }
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    //发包端口计数器
    COUNTER_REGISTER(0);

    action insert_T_head0(){
        if(meta.packet_tpye==1){//丢包率
            hdr.detection_head.T_head0=meta.N_sendpkt;
        }else{//时延
            hdr.detection_head.T_head0=standard_metadata.egress_global_timestamp[31:0];
        }
    }

    action insert_T_head1(){
        if(meta.packet_tpye==1){//丢包率
            hdr.detection_head.T_head1=meta.N_sendpkt;
        }else{//时延
            hdr.detection_head.T_head1=standard_metadata.egress_global_timestamp[31:0];
        }
    }
    action set_direction(){
        hdr.detection_head.direction=standard_metadata.egress_port[0:0];
    }
    apply {
        //读取出端口的数据包数量
        COUNTER_COUNT(0,(bit<32>)standard_metadata.egress_port);
        meta.N_sendpkt=meta.value_counter;


        if(meta.packet_tpye==2){//自检包
            // 自检包逻辑
            if(meta.forwording1==0){
                if(standard_metadata.egress_port==standard_metadata.ingress_port){
                    hdr.detection_head.forwording=1;
                    set_direction();
                }
            }
            return;
        }

        if(standard_metadata.ingress_port==1){//monitor发送探测包
            set_direction();
            insert_T_head0();
        }
        else{
            if(standard_metadata.ingress_port>3){//异轨
                if(meta.forwording1==0){
                    insert_T_head1();
                }
            }
            else{//同轨
                if(standard_metadata.egress_port==standard_metadata.ingress_port){//转发返回探测包
                    hdr.detection_head.forwording=1;
                    set_direction();
                    insert_T_head1();
                }
                else{
                    if(meta.forwording1==0){//链路节点
                        insert_T_head0();
                    }
                }
            }
        }
        return;
    }
}


/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
	    
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;