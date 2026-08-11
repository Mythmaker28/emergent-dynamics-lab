#!/bin/sh
# FROZEN LAUNCH TEMPLATE. $1 = plan file, $2 = log dir. Detaches into its own session so that a
# bounded launcher tool call cannot reap the supervisor. Returns immediately.
set -e
PLAN="$1"; LOGD="$2"
mkdir -p "$LOGD"
/usr/bin/nohup /usr/bin/setsid -f /usr/bin/python3 -u \
  /home/claude/sweep/FCDDH01R/DURABLE_PHASE_SUPERVISOR.py "$PLAN" \
  </dev/null >>"$LOGD/phase.log" 2>>"$LOGD/phase.err" &
echo LAUNCHED
