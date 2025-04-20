#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON="$SCRIPT_DIR/venv/bin/python"
LOG_PATH="$SCRIPT_DIR/log/run.log"


setsid bash -c "
while true; do
    echo \"[\$(date)] 🟢 啟動 main.py\" >> $LOG_PATH
   
    $PYTHON main.py >> $LOG_PATH 2>&1
    echo \"[\$(date)] 🔁 main.py 結束了，3 秒後重新啟動\" >> $LOG_PATH
    sleep 3
done" &

echo $! > main_pid.txt

