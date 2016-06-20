#!/bin/bash

python kick_off.py & 
PIDS[0]=$!
sleep 0.1
python decision_tree.py &
PIDS[1]=$!
sleep 0.1
python goalie.py &
PIDS[2]=$!
sleep 0.1


OPP_TEAM="UmayuxOpp"
python kick_off.py -t $OPP_TEAM &
PIDS[20]=$!
sleep 0.1
python decision_tree.py -t $OPP_TEAM &
PIDS[21]=$!
sleep 0.1
python goalie.py -t $OPP_TEAM &
PIDS[22]=$!
sleep 0.1

trap "kill ${PIDS[*]}" SIGINT

wait