#!/bin/bash
/usr/local/bin/taod -datadir=/data -verbose -rpcuser="$RPC_USERNAME" -rpcpassword="$RPC_PASSWORD"
while true; do
    echo "PID $$ - $(date) (to file)" >> /my_service.log
    echo "PID $$ - $(date) (to stdout)"
    echo "PID $$ - $(date) (to stderr)" 1>&2
    sleep 1
done