BMV2_SWITCH_EXE="simple_switch_grpc"
sudo mn -c
sudo python3 ./topo_testorbit.py --behavioral-exe simple_switch_grpc --json ./p4src/build/point1.json
# sudo python3 ./topo.py --behavioral-exe simple_switch_grpc --json ./p4src/build/point1.json