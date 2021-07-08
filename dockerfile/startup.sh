#!/bin/bash
pg_ctlcluster 13 main start

while true; do sleep 3650d; done

# while true; do sleep 2; echo "hello"; done

# tail -f /dev/null
