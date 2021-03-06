#!/bin/bash

rcsoccersim &
sleep 2

TEAM_NAME="UmayuxBase"
SLEEP_TIME=0.1

i=1
python dqn_strategy.py -t $TEAM_NAME --goalie &
while [ $i -le 2 ]; do
    sleep $SLEEP_TIME
    echo ">>>>>>>>>>>>>>>>>>>>>> $TEAM_NAME Player: $i"
    python dqn_strategy.py -t $TEAM_NAME &
    i=`expr $i + 1`
done

TEAM_NAME="UmayuxOpp"

i=1
python dqn_strategy.py -t $TEAM_NAME --goalie &
while [ $i -le 2 ]; do
    echo ">>>>>>>>>>>>>>>>>>>>>> $TEAM_NAME Player: $i"
    sleep $SLEEP_TIME
    python dqn_strategy.py -t $TEAM_NAME &
    i=`expr $i + 1`
done

trap "killall python; killall rcssmonitor; killall -9 rcssserver;" SIGINT

wait
rm *.rcg *.rcl