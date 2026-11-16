# Lab: Blind SQL Injection with Conditional Responses

> **Platform:** PortSwigger Web Security Academy  
> **Module:** SQL Injection  
> **Lab:** Blind SQL injection with conditional responses  
> **Goal:** Exploit the blind SQL injection vulnerability to determine the password of the `administrator` user and log in to their account.

---

## 1. Lab Goal

The goal of this lab was to exploit a blind SQL injection vulnerability in the application's tracking cookie to infer the `administrator` user's password character by character using conditional responses, and then log in as `administrator`.

---

## 2. Given Information

The lab provided the following information:

- The application uses a tracking cookie (`TrackingId`) for analytics and performs a SQL query containing the value of the submitted cookie.
- The results of the SQL query are not returned in the HTTP response, and no database error messages are displayed.
- However, the application includes a `"Welcome back!"` message in the page response if the SQL query returns at least one row.
- The database contains a table called `users`, with columns named `username` and `password`.
- We need to find the password for the `administrator` user and log in to their account.

---

## 3. Vulnerability Summary

The application concatenates the user-supplied `TrackingId` cookie value directly into a backend `SELECT` SQL query without parameterization or sanitization. Even though query output and database errors are hidden, the presence or absence of the `"Welcome back!"` string acts as a boolean oracle (`True` vs. `False`). By injecting conditional SQL statements into `TrackingId` and automating the requests in Python with a binary search algorithm, an attacker can determine the exact password length and extract every character of the `administrator` password.

---

## 4. Observation

When browsing the lab application, the server sets a `TrackingId` cookie alongside the `session` cookie in HTTP requests:

```http
Cookie: TrackingId=CKdeSVOnOWRwQmJ1; session=DMmkDPivpu0Pp1HQNRNwK4Cnp69tApDi
```

When a valid `TrackingId` is sent and the backend query returns a matching record, the response HTML contains the string:

```text
Welcome back!
```

Because manually testing dozens of characters across every password position would be slow and repetitive, I automated the entire process in a Python script (`script.py`) using the `requests` library. The workflow follows a straightforward logic:

1. First, verify whether the `TrackingId` cookie is actually vulnerable to blind SQL injection using simple true and false conditions.
2. Next, determine the exact length of the `administrator` password.
3. Finally, apply binary search to extract the password character by character.

With binary search in place, the number of requests per character is minimized, meaning the overall speed simply depends on the internet connection and how fast requests transfer between the client and the server.

---

## 5. Initial Testing (Confirming Blind SQL Injection)

To verify the vulnerability in `test_vulnerability()`, the script appends two boolean test payloads to the original `BASE_TRACKING_ID` (`CKdeSVOnOWRwQmJ1`) and checks whether `"Welcome back!"` appears in the response:

1. **True Condition (`' AND '1'='1`):**
   ```text
   TrackingId=CKdeSVOnOWRwQmJ1' AND '1'='1
   ```
   Since `'1'='1'` always evaluates to true, the query returns a row and the page renders `"Welcome back!"` (`True`).

2. **False Condition (`' AND '1'='2`):**
   ```text
   TrackingId=CKdeSVOnOWRwQmJ1' AND '1'='2
   ```
   Since `'1'='2'` always evaluates to false, the query returns no rows and `"Welcome back!"` disappears from the response (`False`).

Confirming that the true condition returns `"Welcome back!"` while the false condition omits it proves that the `TrackingId` cookie is vulnerable to boolean-based blind SQL injection.

---

## 6. Exploiting the Vulnerability

Once the vulnerability was confirmed, `script.py` executed two automated enumeration phases against the `users` table for `username='administrator'`.

### Phase 1: Finding the Password Length

In `get_password_length()`, the script loops through lengths `1` to `49` and injects a `LENGTH(password)` check:

```sql
' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')={length}--
```

When the guessed length matches the actual password length, the condition evaluates to true and `"Welcome back!"` appears in the response, locking in the exact number of characters to extract.

### Phase 2: Extracting the Password via Binary Search

In `extract_password_binary(length)`, the script builds a sorted character set of lowercase letters, digits, and uppercase letters (`sorted(string.ascii_lowercase + string.digits + string.ascii_uppercase)`). For each character position `i` from `1` to `length`, it runs a binary search ($O(\log n)$):

1. It picks the midpoint character `guess_char = chars[mid]` and tests whether the character at position `i` is alphabetically/ASCII-wise greater than `guess_char`:
   ```sql
   ' AND (SELECT SUBSTRING(password,{i},1) FROM users WHERE username='administrator') > '{guess_char}'--
   ```
   - If `"Welcome back!"` is returned, the target character lies in the upper half, so `low = mid + 1`.

2. If the greater-than check is false, it tests for exact equality:
   ```sql
   ' AND (SELECT SUBSTRING(password,{i},1) FROM users WHERE username='administrator') = '{guess_char}'--
   ```
   - If `"Welcome back!"` is returned, the exact character is found and appended to `password`.
   - Otherwise, the target character lies in the lower half, so `high = mid - 1`.

Running `script.py` automatically verified the injection, identified the password length, and extracted the full `administrator` password character by character.

Using the recovered `administrator` password, I logged in to the application and solved the lab.

---

## 7. Correct Testing Approach

1. Identify an input vector (such as the `TrackingId` cookie) that triggers a consistent boolean difference in the HTTP response (presence vs. absence of `"Welcome back!"`).
2. Confirm boolean blind SQL injection by comparing a tautology (`' AND '1'='1`) against a contradiction (`' AND '1'='2`).
3. Enumerate the target field's length first (`LENGTH(password) = N`) so the extraction loop has an exact stopping boundary.
4. Use binary search with `SUBSTRING()` and comparison operators (`>` and `=`) over a sorted character set instead of linear brute-forcing to minimize HTTP round-trips.
5. Authenticate with the extracted credentials to confirm account access.

---

## 8. Exploitation Steps

1. Captured a valid lab request to obtain the target URL, `TrackingId` cookie, and `session` cookie.
2. Configured `LAB_URL`, `BASE_TRACKING_ID`, `SESSION_COOKIE`, and `SUCCESS_INDICATOR` (`"Welcome back!"`) in `script.py`.
3. Executed `script.py` to test `' AND '1'='1` and `' AND '1'='2`, confirming the blind SQL injection vulnerability.
4. Automated `LENGTH(password)` probing in the script to determine the `administrator` password length.
5. Automated binary search with `SUBSTRING(password, i, 1)` comparisons to recover every character of the password.
6. Used the retrieved password to log in as `administrator` and solve the lab.

---

## 9. Evidence

### Boolean Vulnerability Verification Payloads

```sql
TrackingId=CKdeSVOnOWRwQmJ1' AND '1'='1
TrackingId=CKdeSVOnOWRwQmJ1' AND '1'='2
```

### Password Length Enumeration Payload

```sql
TrackingId=CKdeSVOnOWRwQmJ1' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')={length}--
```

### Binary Search Character Extraction Payloads

```sql
TrackingId=CKdeSVOnOWRwQmJ1' AND (SELECT SUBSTRING(password,{i},1) FROM users WHERE username='administrator') > '{guess_char}'--
TrackingId=CKdeSVOnOWRwQmJ1' AND (SELECT SUBSTRING(password,{i},1) FROM users WHERE username='administrator') = '{guess_char}'--
```

---

## 10. Why This Worked

Although the application never displays database query results or SQL errors, its UI conditionally renders `"Welcome back!"` based on whether the `TrackingId` query returns a row. Injecting `' AND <condition>--` turns the entire page response into a reliable boolean signal. Because characters in SQL can be compared lexicographically with `>` and `=`, binary search halves the search space on every iteration—reducing a 62-character search space to at most ~6–7 comparisons per character position. As a result, extraction completes rapidly, limited only by network latency and request round-trip speed between the client and the server.

---

## 11. Remediation / Fix

To prevent blind SQL injection vulnerabilities, the application should:

- **Use Parameterized Queries (Prepared Statements):** Pass cookie values such as `TrackingId` as bound parameters so the database treats them strictly as literal strings rather than executable SQL syntax.
- **Avoid Concatenating Cookie Values into SQL:** Never build SQL queries via raw string concatenation using HTTP headers or cookies.
- **Hash Stored Passwords:** Store user passwords using strong, salted cryptographic hashing algorithms (such as bcrypt or Argon2) rather than plaintext.

---

## 12. Lessons Learned

- Even when an application returns no data or error messages, a single conditional UI element (`"Welcome back!"`) is enough to extract full database records via boolean blind SQL injection.
- Combining boolean SQL injection with binary search ($O(\log n)$) makes character-by-character extraction dramatically faster than linear brute-forcing, making network round-trip latency the only real bottleneck.

---

## 13. Final Summary

In this lab, I exploited a boolean-based blind SQL injection vulnerability in the `TrackingId` cookie using a Python automation script (`script.py`). The script first confirmed the vulnerability by contrasting `' AND '1'='1` and `' AND '1'='2` against the `"Welcome back!"` response indicator, then determined the length of the `administrator` password, and finally extracted each character using binary search. With the recovered password, I logged in as `administrator` and solved the lab.
