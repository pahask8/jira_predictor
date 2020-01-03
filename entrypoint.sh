#!/usr/bin/env bash
set -e

_term() {
  echo "Caught SIGTERM signal!"
  kill $child
  wait $child
  exit $?
}

trap _term 15

python serving.py &

child=$!
wait $child
