#!/bin/bash

rcsoccersim &
SIM=$!
echo $SIM
sleep 2

TEAM_NAME="UmayuxBase"
SLEEP_TIME=0.1

i=1
while [ $i -le 3 ]; do
    echo ">>>>>>>>>>>>>>>>>>>>>> $TEAM_NAME Player: $i"
    python decision_tree.py -t $TEAM_NAME &
    MY_PIDS[$i]=$!
    sleep $SLEEP_TIME
    i=`expr $i + 1`
done

TEAM_NAME="UmayuxOpp"

i=1
while [ $i -le 3 ]; do
    echo ">>>>>>>>>>>>>>>>>>>>>> $TEAM_NAME Player: $i"
    python decision_tree.py -t $TEAM_NAME &
    OPP_PIDS[$i]=$!
    sleep $SLEEP_TIME
    i=`expr $i + 1`
done

trap "kill ${MY_PIDS[*]}; kill ${OPP_PIDS[*]}; kill $SIM; killall rcssmonitor" SIGINT

wait
rm *.rcg *.rcl