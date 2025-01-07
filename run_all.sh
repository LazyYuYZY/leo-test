#!/bin/bash

count=0

while [ $count -lt 1 ]; do
    sudo sh run_p4.sh
    sleep 1
    sudo sh run.sh
    sleep 100
    sudo sh run_revpkt.sh
    sleep 1
    sudo sh run_sendpkt.sh
    ((count++))
done
