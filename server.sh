#!/bin/bash

rcssserver server::coach=on server::coach_w_referee=on &
rcssmonitor &


trap "killall rcssmonitor; killall -9 rcssserver;" SIGINT

wait
rm *.rcg *.rcl