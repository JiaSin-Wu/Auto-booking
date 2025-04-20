#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR" || {
    echo "❌ Failed to cd into $SCRIPT_DIR"
    exit 1
}

LOG_DIR="$SCRIPT_DIR/log"
BACKUP_DIR="$SCRIPT_DIR/backup"

mkdir -p "$BACKUP_DIR"

if [ -f main_pid.txt ]; then
    PGID=$(ps -o pgid= $(cat main_pid.txt) | grep -o '[0-9]*')
    echo "🛑 Killing process group: $PGID"
    kill -TERM -"$PGID"
    rm main_pid.txt
    for file in run.log process_0.log; do
        if [ -f "$LOG_DIR/$file" ]; then
            echo "📦 Moving $file to backup folder..."
            mv "$LOG_DIR/$file" "$BACKUP_DIR/"
        fi
    done
    echo "start rm log/*"
    rm -rf log/*
    echo "finish"

fi

